---
type: concept
domain:
  - RAG
depth: L3
importance: extension
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Hypothetical Document Embeddings
tags:
  - hyde
  - dense-retrieval
---

# HyDE 假设文档检索

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

短查询与知识库长文在表达形式上差异很大。HyDE 先让模型生成一段“假设答案文档”，再对它编码并检索真实文档。假设文档用于靠近答案风格的向量区域，不作为事实证据。

## 不理解会造成什么错误

- 把模型编造的假设文档直接放进答案并引用。
- 假设文档改错产品、否定、地区或时间，导致检索漂移。
- 对精确编号查询仍调用生成模型，增加延迟且降低准确性。
- 只比较向量相似度，不与原查询检索基线做消融。
- 生成内容夹带越权数据源指令，改变检索范围。

## 它在 RAG 链路中的位置

```text
原查询 q → 约束提取 → 生成假设文档 h → 约束校验
→ Embedding(h) → 真实语料向量检索 → 真实证据 → 回答
            └→ 漂移时回退 Embedding(q)
```

## 从故障检索开始

用户只说“X2 更新后黑屏”。文档可能写成一段完整故障说明，短查询向量不够接近。HyDE 生成“X2 完成固件更新后启动显示黑屏，可检查……”以匹配文档风格，但其中解决步骤可能全是假的，最终只能使用检索到的真实手册。

简单基线是直接编码原查询；只有 Dense 召回失败且语体差异明显时再试 HyDE。

## 输入输出与信任状态

输入含原查询、实体、否定、时间、权限范围和生成长度上限。中间态 `hypothesis` 必须标记 `untrusted_non_evidence`。输出是来自真实索引的文档 ID、相似度和来源，引用不得指向假设文本。

## 向量检索机制

原查询向量为 $e_q$，假设文档向量为 $e_h$，真实文档向量为 $e_d$。余弦相似度为：

$$
\cos(e_h,e_d)=\frac{e_h\cdot e_d}{\|e_h\|_2\|e_d\|_2}
$$

HyDE 假设 $e_h$ 比 $e_q$ 更接近相关文档。多个假设可取平均向量：

$$
\bar e_h=\frac1m\sum_{i=1}^{m}e_{h_i}
$$

平均可能减少单次生成偏差，也会抹平不同意图，且成本随 $m$ 增长。

## 最小手算

设相关文档单位向量 $d=(0.8,0.6)$，原查询 $q=(1,0)$，相似度为 0.8。假设文档向量 $h=(0.8,0.6)$，相似度为 1.0；在这个玩具例子中更容易召回。若假设漂移为 $(0,1)$，相似度只有 0.6，反而变差。

## 可执行实验

```python
import numpy as np

def cosine(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def validate_hypothesis(original, hypothesis, entity, required_terms):
    if entity not in hypothesis or not all(term in hypothesis for term in required_terms):
        return original, "fallback_original"
    return hypothesis, "hyde"

docs = {"relevant": np.array([0.8, 0.6]),
        "irrelevant": np.array([0.1, 0.995])}
query = np.array([1.0, 0.0])
hypothesis_vector = np.array([0.8, 0.6])
assert cosine(hypothesis_vector, docs["relevant"]) > cosine(query, docs["relevant"])

text, mode = validate_hypothesis(
    "X2 更新后不启动", "X2 更新后不启动的故障说明", "X2", ["不启动"]
)
assert mode == "hyde"
fallback, mode2 = validate_hypothesis(
    "X2 更新后不启动", "X1 更新后的启动步骤", "X2", ["不启动"]
)
assert mode2 == "fallback_original" and fallback == "X2 更新后不启动"

# 假设文档不是可引用证据。
record = {"text": text, "trust": "untrusted_non_evidence", "citation_id": None}
assert record["citation_id"] is None
print(mode, mode2, round(cosine(hypothesis_vector, docs["relevant"]), 3))
```

## 实验结果解释

玩具向量展示假设向量可能更靠近相关文档，漂移文本则回退原查询；假设文档没有引用 ID。人工向量不能证明真实 Embedding 上有效，必须用目标领域、目标模型和固定 qrels 对照直接检索。

## 质量延迟与成本影响

- 比直接 Dense 检索多一次生成调用，增加 TTFT、Token 成本和故障率。
- 假设更长会增加生成与编码成本，未必提高召回。
- 可并行执行原查询和 HyDE 后融合，提高稳健性但再增检索量。
- 缓存需要包含模型、Prompt、实体约束和知识版本。

## 数据评测与安全风险

报告相对直接 Dense 的 Recall@k、MRR、漂移率、生成延迟和单问成本。测试实体替换、否定、时效、少数语言与不可回答问题。假设文本不能改变授权数据源，也不能作为证据或训练标签回流；若日志保存生成内容，应防止其中出现个人或敏感推断。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 召回偏向错误产品 | 假设替换实体 | 原查询约束、假设差异、回退率 |
| 答案引用不存在内容 | 把假设当证据 | 引用来源类型、证据 ID |
| 延迟明显升高 | 额外生成或多假设 | 生成 Token、并发、超时 |
| 比直接检索更差 | 领域语体无鸿沟或生成漂移 | 基线消融、查询切片 |
| 出现越权来源 | 假设文字影响授权 | 服务端允许源、ACL 过滤 |

## 适用与不适用场景

适合短查询与长文档语体差异明显、无监督 Dense 召回不足的探索场景。不适合精确 ID、法规条款号、极低延迟请求，以及无法容忍实体或否定漂移的高风险检索。

## 学习收益

你应能解释 HyDE 的中间文本为何不是证据，用余弦相似度说明其假设，设计约束校验、直接检索基线和失败回退。

## 给别人讲清楚

“先写一张可能长得像答案的草稿，用草稿去图书馆找真资料；草稿只是搜索诱饵，不能拿来当证据。”

## 自检问题

1. 为什么假设文档不能被引用？
2. HyDE 应与哪个最简单基线比较？
3. 哪些约束丢失时必须回退原查询？

## 相关主题

- [Dense 向量检索](09-Dense%20向量检索.md)
- [RAG 查询改写](13-RAG%20查询改写.md)
- [RAG 多查询检索](14-RAG%20多查询检索.md)
- [RAG 引用生成](36-RAG%20引用生成.md)

## 资料来源

- Gao 等, [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://aclanthology.org/2023.acl-long.99/)，访问日期：2026-09-10。
- Hugging Face, [Sentence Transformers](https://huggingface.co/docs/sentence-transformers/index)，访问日期：2026-09-10。

