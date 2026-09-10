---
type: concept
domain:
  - RAG
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - RAG 召回评测
tags:
  - retrieval-evaluation
  - ranking-metrics
---

# RAG 检索评测

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

检索评测回答“生成模型需要的证据是否被找回，以及排在什么位置”。如果证据根本不在候选中，修改 Prompt 或重排序无法补救。独立评测检索，才能把召回故障与生成故障分开。

## 不理解会造成什么错误

- 只看最终答案，无法知道模型是检索到还是靠记忆猜对。
- 只报告 Recall@k，忽略相关文档排在末尾造成的上下文浪费。
- 混淆“至少命中一个”和“找全所有相关证据”的 Recall 口径。
- 在测试集反复调 k、权重和查询改写。
- 把未标注文档一律当成不相关，低估新检索器。

## 它在 RAG 链路中的位置

固定语料版本、查询集和相关性标注 qrels，运行各检索配置并保存逐查询排名。先算总体与切片指标，再查看失败样例，最后才决定改切分、检索器、融合、重排或查询策略。

## 简单基线

关键词包含匹配或 BM25 是首个基线。Dense、Hybrid 和 Rerank 必须使用同一语料、过滤、查询和 k 比较。没有基线，无法证明复杂方案带来净收益。

## Recall at k

若查询 $q$ 的相关集合为 $R_q$，前 $k$ 个结果为 $D_q^k$，找全比例为：

$$
Recall@k(q)=\frac{|R_q\cap D_q^k|}{|R_q|}
$$

若业务只需一个证据，还可报告 Hit@k，即交集非空记 1。两者不能都叫 Recall 而不说明口径。

## MRR

设第一个相关结果名次为 $rank_q$，没有命中记 0：

$$
MRR=\frac{1}{|Q|}\sum_{q\in Q}\frac{1}{rank_q}
$$

MRR 重视第一个可用证据，不关心后续是否找全。

## nDCG at k

分级相关性 $rel_i$ 的折损收益为：

$$
DCG@k=\sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)},\qquad
nDCG@k=\frac{DCG@k}{IDCG@k}
$$

IDCG 是同一相关性标签的理想排序。没有相关文档时需预先约定 nDCG 为 0 或跳过，并报告样本数。

## 最小手算

某查询有两个相关文档，返回 `[相关, 不相关, 相关]`。Recall@2 为 $1/2$，Hit@2 为 1，第一个相关文档在第 1 名，所以倒数排名为 1。若相关性等级为 `[2,0,1]`，DCG@3 为 $3+0+1/2=3.5$；理想 `[2,1,0]` 的 IDCG 为 $3+1/\log_2 3\approx3.631$，nDCG 约 0.964。

## 可执行实验

```python
import math

def recall_at_k(ranking, relevant, k):
    if not relevant:
        return None  # 不可回答查询单独评测，不伪造 Recall。
    return len(set(ranking[:k]) & set(relevant)) / len(relevant)

def reciprocal_rank(ranking, relevant):
    return next((1 / rank for rank, doc in enumerate(ranking, 1)
                 if doc in relevant), 0.0)

def dcg(relevances):
    return sum((2 ** rel - 1) / math.log2(rank + 1)
               for rank, rel in enumerate(relevances, 1))

def ndcg_at_k(retrieved_relevances, all_qrel_relevances, k):
    actual = dcg(retrieved_relevances[:k])
    ideal = dcg(sorted(all_qrel_relevances, reverse=True)[:k])
    return actual / ideal if ideal > 0 else None

ranking = ["d1", "d3", "d2"]
relevant = {"d1", "d2"}
score_rels = [2, 0, 1]
all_qrels = [2, 1, 0]
ndcg = ndcg_at_k(score_rels, all_qrels, 3)
print("Recall@2", recall_at_k(ranking, relevant, 2),
      "RR", reciprocal_rank(ranking, relevant), "nDCG", round(ndcg, 3))
assert recall_at_k(ranking, relevant, 2) == 0.5
assert reciprocal_rank(ranking, relevant) == 1.0
assert 0 <= ndcg <= 1
assert recall_at_k(ranking, set(), 2) is None
assert ndcg_at_k([0, 0, 0], [0, 0, 0], 3) is None
assert ndcg_at_k([1, 0, 0], [3, 2, 1], 3) < 1.0
```

实验验证单查询手算；IDCG 从该查询完整 qrels 的理想前 k 项得到，因此漏召回高等级文档不会被误判为满分。无相关文档的 Recall 和零 IDCG 的 nDCG 标为 N/A。真实报告应说明跳过数量，对有效查询求平均并保存逐查询值。

## 数据集怎样构建

从真实流量按意图、语言、长度、时间、权限和难度分层采样；定义文档级或 Chunk 级相关性；保留不可回答查询。多跳问题需要标注证据集合，而不仅是任意一个相关段落。训练、开发、测试按来源或时间隔离，测试集只在配置冻结后运行。

## 不完整 qrels

人工通常只标注部分候选，未标注文档不一定不相关。合并多个检索器结果建立候选池并补标；对新方法抽样审查其“未标注高排名结果”。指标要配失败样例，避免把标注缺失误判成算法退化。

## 质量延迟与成本影响

增大 k 往往提高 Recall，却增加重排、上下文 Token 和延迟，并引入更多噪声。除质量外报告检索 P50/P95、索引大小、构建时间、查询成本和过滤后空结果率。用质量成本曲线选 k，而不是只取最大窗口。

## 数据评测与安全风险

qrels 本身可能泄露敏感文档关系，应按生产权限保护。每条查询评测时应用对应身份，不能用全权限离线指标替代真实授权。避免在查询改写或训练中使用测试答案和相关文档文本，防止污染。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| Recall 高但答案仍差 | 排序、上下文或生成故障 | 名次、证据位置、Faithfulness |
| MRR 高但多跳失败 | 只找到第一份证据 | 证据集合 Recall、多跳标注 |
| 新方法指标反而低 | qrels 不完整 | 未标注高排名结果、补标 |
| 总分好但错误码差 | 查询分布掩盖切片 | 意图和实体类型切片 |
| 增大 k 收益很小 | 召回器候选同质或标注上限 | 去重、分支互补、错误样例 |

## 适用与不适用场景

所有 RAG 迭代都应先有检索评测。若任务没有可定义证据，排名指标可能不适用，但仍需别的可证伪标准。检索分数不能替代最终回答与安全评测。

## 学习收益

你应能手算 Recall、MRR 和 nDCG，选择匹配业务的口径，识别不完整 qrels，并把质量与延迟成本一起比较。

## 给别人讲清楚

“检索评测像检查开卷考试发给学生的资料：先看正确资料有没有发到、排得靠不靠前，再讨论学生有没有根据资料答对。”

## 自检问题

1. Recall@k 和 Hit@k 的问题口径有什么差别？
2. MRR 为什么不能衡量多份证据是否找全？
3. 未标注文档为什么不能总当成不相关？

## 相关主题

- [BM25 稀疏检索](<08-BM25 稀疏检索.md>)
- [Dense 向量检索](<09-Dense 向量检索.md>)
- [RAG 生成评测](38-RAG 生成评测.md)

## 资料来源

- Christopher D. Manning 等, [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/), 2008，访问日期：2026-09-10。
- Nandan Thakur 等, [BEIR](https://openreview.net/forum?id=wCu6T5xFjeJ), 2021，访问日期：2026-09-10。
- Kalervo Järvelin, Jaana Kekäläinen, [Cumulated Gain Based Evaluation of IR Techniques](https://dl.acm.org/doi/10.1145/582415.582418), 2002，访问日期：2026-09-10。
