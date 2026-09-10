---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Reranking]
tags: [reranking, cross-encoder]
---

# RAG 重排序

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

召回器为速度分别编码查询和文档，可能把词面或主题相近但不能回答问题的文档排前。重排序器对较小候选集逐对读取“查询 + 文档”，用更细致的交互分数改善前几名顺序。

## 不理解会造成什么错误

- 期待重排序找回根本没进入候选集的相关文档。
- 候选窗口过小，相关文档在精排前已被截断。
- 只比较最终 Top-1，不记录召回上限和额外延迟。
- 将含提示注入的候选直接交给模型式重排序器执行指令。

## 它在 RAG 链路中的位置

`查询 → 初筛 Top-N → 构造 N 个查询文档对 → 相关度评分 → 重新排序 → Top-k 上下文`。输入形状可写为 N 对文本，输出为 `[N]` 分数。Cross-Encoder 不生成新候选。

## 从退款政策开始

查询“企业客户退款期限”，召回结果包含个人客户退款、企业客户开票和企业退款政策。简单基线沿用 BM25 或 Dense 顺序；Cross-Encoder 可同时注意“企业客户”和“退款期限”，把完整匹配排前。

## 召回上限与排序指标

设候选集合为 $C_N(q)$，相关文档集合为 $R(q)$。重排序后 Top-k 必然仍来自候选：

$$
P_k(q)\subseteq C_N(q)
$$

因此若 $C_N(q)\cap R(q)=\varnothing$，无论重排序器多强，Top-k 相关数仍为 0。候选召回上限为：

$$
\operatorname{Recall@N}=\frac{|C_N(q)\cap R(q)|}{|R(q)|}
$$

只有相关文档已进入候选时，精排才可能改善首个相关结果名次、nDCG 或生成上下文质量。

## 最小手算

唯一相关文档是 C。初筛顺序 `[A,B,C]`，Recall@3 为 1，首个相关名次为 3；精排成 `[C,A,B]` 后首个相关名次为 1。若窗口只取 `[A,B]`，Recall@2 为 0，任何重排都不能出现 C。

## 可执行实验

```python
relevant = {"C"}
retrieved = ["A", "B", "C", "D"]
rerank_score = {"A": 0.2, "B": 0.1, "C": 0.9, "D": 0.0}

def rerank(candidates):
    return sorted(candidates, key=lambda doc: (-rerank_score[doc], doc))

def recall(candidates):
    return len(set(candidates) & relevant) / len(relevant)

wide = rerank(retrieved[:3])
narrow = rerank(retrieved[:2])
print(wide, narrow)
assert wide[0] == "C"
assert recall(retrieved[:3]) == 1.0
assert recall(narrow) == 0.0
assert set(wide) == set(retrieved[:3])  # 只改顺序，不新增候选
assert "C" not in narrow
```

## 实验结果边界

实验严格证明集合边界和候选窗口影响，不证明手工分数来自有效模型，也不证明重排后答案一定更好。真实系统需用冻结的查询、qrels 和端到端生成评测比较无重排基线。

## 质量延迟与成本影响

Cross-Encoder 通常比双编码器更精细，却需对 N 个文本对推理，成本大致随候选数和序列长度增长。可批处理、截断和缓存文档部分，但都要重新验证。先选择达到召回目标的最小 N，再评估 p50、p95 和吞吐。

## 数据评测与安全风险

训练数据需包含主题相近但答案错误的困难负例，并防止文档泄漏到测试集。候选内容属于不可信数据，模型输入用清晰边界，输出只解释为相关度。权限必须在重排序前执行，避免越权文本进入模型或外部服务。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 精排毫无提升 | 相关文档未进候选 | Recall@N、候选窗口、召回错误 |
| Top-1 变差 | 领域不匹配或截断 | 失败样例、Token 长度、训练分布 |
| p95 延迟过高 | N 太大或序列太长 | 候选数、批大小、截断、队列 |
| 越权文本被处理 | 权限在精排后执行 | ACL 下推、调用 Trace、服务边界 |
| 离线好线上差 | 测试污染或查询漂移 | 数据切分、时间切片、线上样本 |

## 适用与不适用场景

适合召回率已足够但前排顺序差、且质量收益能覆盖延迟的场景。候选根本缺失时先修召回；严格低延迟、极短候选或初筛已经满足目标时可不使用。

## 学习收益

你应能区分召回与重排序职责，证明候选集合上限，设计候选窗口消融，并计算新增模型调用的成本。

## 给别人讲清楚

“召回像选入复赛，重排序像给复赛选手重新打分。没进复赛的文档，裁判再聪明也排不进前三。”

## 自检问题

1. 为什么重排序不能提高候选集合的 Recall@N？
2. 候选窗口 N 增大有什么质量和成本变化？
3. 为什么权限过滤必须发生在重排序前？

## 相关主题

- [混合检索 Hybrid Search](02-混合检索%20Hybrid%20Search.md)
- [RAG 检索评测](37-RAG%20检索评测.md)
- [RAG 上下文构建](35-RAG%20上下文构建.md)

## 资料来源

- Nogueira 与 Cho, [Passage Re-ranking with BERT](https://arxiv.org/abs/1901.04085), 2019，访问日期：2026-09-10。
- Khattab 与 Zaharia, [ColBERT](https://arxiv.org/abs/2004.12832), 2020，访问日期：2026-09-10。
- Thakur 等, [BEIR](https://openreview.net/forum?id=wCu6T5xFjeJ), 2021，访问日期：2026-09-10。
