---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Vector Index]
tags: [vector-index, ann]
---

# RAG 向量索引

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

向量索引从大量文档向量中找到与查询最接近的候选。逐个比较的精确搜索简单可靠，但数据增长后延迟高；近似最近邻 ANN 用可能漏召回的代价换取更少计算。

## 不理解会造成什么错误

- 把 ANN 返回结果当作数学上的精确 Top-k。
- 只测每秒查询量，不测相对精确搜索的 Recall@k。
- 查询和索引的距离度量、归一化或向量版本不一致。
- 删除只改业务库，旧向量仍能被召回。

## 它在 RAG 链路中的位置

离线：`Chunk → Embedding [N,D] → 构建索引与 ID 映射`。在线：`查询向量 [D] → 权限和元数据约束 → 相似搜索 → 文档 ID 与分数 Top-k`。索引只保存检索结构，不取代原文和来源记录。

## 从精确扫描开始

小知识库有 1000 个向量，简单基线是矩阵乘法精确扫描，便于验证。数据达到百万级后，可用 HNSW、IVF 等 ANN。先保留精确子集作为金标准，再调搜索预算。

## 精确搜索与近似召回

归一化向量下，精确余弦 Top-k 为：

$$
G_k(q)=\operatorname{TopK}_{i\in\{1,\ldots,N\}} q^Td_i
$$

ANN 只搜索候选集合 $S(q)\subseteq\{1,\ldots,N\}$：

$$
A_k(q)=\operatorname{TopK}_{i\in S(q)}q^Td_i
$$

相对精确结果的索引召回为：

$$
\operatorname{Recall@k}=\frac{|A_k(q)\cap G_k(q)|}{k}
$$

增加探测簇数、图搜索宽度等预算通常扩大 $S(q)$，可能提高 Recall，也增加延迟；它不是业务相关性 Recall 的替代品。

## 最小手算

精确 Top-3 是 `[A,B,C]`，ANN 返回 `[A,C,D]`。交集为 `{A,C}`，所以 Recall@3 为 $2/3$。这只说明 ANN 保留了多少精确近邻，不说明 A、B、C 是否真的回答用户问题。

## 可执行实验

```python
import numpy as np

vectors = np.array([
    [1.0, 0.0], [0.9, 0.1], [0.8, 0.2],
    [0.0, 1.0], [-1.0, 0.0], [-0.8, 0.2],
])
vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
query = np.array([1.0, 0.0])

def topk(indices, k):
    scores = vectors[indices] @ query
    order = np.argsort(-scores, kind="stable")[:k]
    return [int(indices[i]) for i in order]

all_ids = np.arange(len(vectors))
gold = topk(all_ids, 3)
small_candidates = np.array([0, 2, 3])
large_candidates = np.array([0, 1, 2, 3])
approx_small = topk(small_candidates, 3)
approx_large = topk(large_candidates, 3)

def recall(result, truth):
    return len(set(result) & set(truth)) / len(truth)

print(gold, approx_small, approx_large)
assert gold == [0, 1, 2]
assert recall(approx_small, gold) == 2 / 3
assert recall(approx_large, gold) == 1.0
assert len(small_candidates) < len(all_ids)
```

## 实验结果边界

实验用“受限候选集合”说明 ANN 的核心取舍，不实现 HNSW 或 IVF，也不证明候选越多时召回必然单调。真实索引要在相同硬件、并发、过滤条件和数据分布下测 Recall、p95 延迟和吞吐。

## 质量延迟与成本影响

精确搜索约需 $O(ND)$ 次运算。ANN 通过额外索引内存和构建时间减少查询比较。量化降低内存与带宽但可能损失邻居排序。构建、增量写入、压缩、备份和双版本迁移都计入总成本。

## 数据评测与安全风险

过滤 ANN 可能因授权集合很小而召回不足，应验证后端是预过滤、搜索中过滤还是后过滤。向量仍是敏感派生数据。索引清单绑定语料快照、模型、维度、距离、归一化与参数；删除必须移除 ID、向量和缓存。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| ANN 比精确结果差很多 | 搜索预算太低 | Recall@k、候选量、搜索参数 |
| 排名整体异常 | 距离或归一化不一致 | cosine、inner product、向量范数 |
| 查询报维度错误 | 模型与索引版本混用 | 模型 ID、维度、索引清单 |
| 过滤后候选不足 | ANN 后过滤或选择率低 | 过滤执行位置、搜索扩展、零结果率 |
| 删除内容仍出现 | ID 映射或缓存未清理 | 墓碑位点、索引版本、缓存 |

## 适用与不适用场景

向量量大且精确扫描达不到延迟目标时适合 ANN。小语料、离线批处理或强过滤后候选很少时，精确搜索更简单可靠。索引优化不能弥补低质量 Embedding。

## 学习收益

你应能区分业务检索 Recall 与 ANN 相对 Recall，手算 Recall@k，并解释搜索预算、延迟、内存和过滤之间的关系。

## 给别人讲清楚

“精确搜索把所有书都比较一遍；ANN 先快速缩小书架再比较，所以更快但可能走错书架。要用精确结果测它漏了多少。”

## 自检问题

1. ANN Recall@k 的金标准是什么？
2. 为什么 ANN Recall 高仍不代表业务相关性好？
3. 元数据过滤会怎样影响近似搜索？

## 相关主题

- [Dense 向量检索](09-Dense%20向量检索.md)
- [RAG 元数据](07-RAG%20元数据.md)
- [大模型量化](../J-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM/15-%E5%A4%A7%E6%A8%A1%E5%9E%8B%E9%87%8F%E5%8C%96.md)

## 资料来源

- Malkov 与 Yashunin, [Efficient and Robust Approximate Nearest Neighbor Search Using HNSW](https://doi.org/10.1109/TPAMI.2018.2889473), 2018，访问日期：2026-09-10。
- Johnson 等, [Billion-scale similarity search with GPUs](https://arxiv.org/abs/1702.08734), 2017，访问日期：2026-09-10。
- Faiss, [Guidelines to choose an index](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)，访问日期：2026-09-10。
