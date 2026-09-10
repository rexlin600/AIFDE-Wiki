---
type: concept
domain:
  - RAG
depth: L3
importance: common
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Multi Query Retrieval
tags:
  - query-expansion
  - reciprocal-rank-fusion
---

# RAG 多查询检索

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

同一个意图可以有不同表达，单条查询可能只覆盖一种词汇或视角。多查询检索生成少量、意图一致但互补的查询，分别召回，再去重和融合候选，以提高相关证据进入候选集的机会。

## 不理解会造成什么错误

- 生成十几条近义句，成本增加却没有新增候选。
- 扩展查询丢失产品型号、否定或权限条件，召回错误数据。
- 直接相加 BM25 与向量原始分数，量纲不同导致排序失真。
- 合并结果不去重，同一文档挤占全部上下文。
- 只追求 Recall，噪声增多后最终回答反而变差。

## 它在 RAG 链路中的位置

```text
原查询 → 约束抽取 → 生成 2 至 n 条互补查询 → 分别检索
→ 每路候选去重 → 排名融合 → 重排序 → 上下文
```

简单基线是单查询 top-k。只有单查询在固定失败集存在词汇鸿沟时，才值得支付额外查询成本。

## 从技术支持开始

用户问“X2 更新后一直转圈怎么办？”可以生成“X2 升级后启动卡住”和“X2 更新后加载界面无响应”。两个视角可能分别命中发布说明和故障手册，但都必须保留 `X2`，不能改成 X1，也不能扩展到用户无权访问的内部库。

## 输入输出与状态

输入包含原查询、不可变约束、最大查询数 $m$ 和每路候选数 $k$。输出保留每个候选的文档 ID、来源查询、原始名次和权限标签。完整预算近似为最多 $m\times k$ 个原始候选，去重后再进入重排。

## 用 RRF 融合不同排名

不同检索路的原始分数未必可比。倒数排名融合 RRF 只使用名次：

$$
RRF(d)=\sum_{j=1}^{m}\frac{1}{K+r_j(d)}
$$

$r_j(d)$ 是文档 $d$ 在第 $j$ 路中的名次，未出现则不加；$K$ 是平滑常数。多路都靠前的文档会累积分数。RRF 不会判断文档是否真实相关，仍需评测和重排。

## 最小手算

取 $K=60$。文档 A 在两路排名 1、3：

$$
RRF(A)=\frac1{61}+\frac1{63}\approx0.03227
$$

文档 B 只在一路排名 1，得 $1/61\approx0.01639$，因此 A 靠前。若三条扩展查询返回完全相同列表，Recall 不变，只把检索请求增至三倍。

## 可执行实验

```python
from collections import defaultdict

def validate_queries(original_entity, required_slots, queries, max_queries=3):
    unique = []
    for query in queries[:max_queries]:
        keeps_slots = all(any(term in query for term in alternatives)
                          for alternatives in required_slots.values())
        if original_entity not in query or not keeps_slots:
            continue
        if query not in unique:
            unique.append(query)
    if not unique:
        raise ValueError("no intent-preserving query")
    return unique

def rrf(rankings, k=60):
    scores = defaultdict(float)
    sources = defaultdict(list)
    for query_id, docs in rankings.items():
        for rank, doc_id in enumerate(docs, start=1):
            scores[doc_id] += 1 / (k + rank)
            sources[doc_id].append((query_id, rank))
    return sorted(scores, key=lambda d: (-scores[d], d)), scores, sources

candidates = [
    "X2 更新后不启动",
    "X2 升级后加载无响应",
    "X1 更新方法",                 # 丢实体，拒绝
    "X2 更新后不启动",             # 重复，去重
]
slots = {
    "change": ("更新", "升级"),
    "failure": ("转圈", "不启动", "无响应"),
    "negative": ("不", "无"),
}
queries = validate_queries("X2", slots, candidates)
assert queries == ["X2 更新后不启动", "X2 升级后加载无响应"]

rankings = {"q1": ["A", "B", "C"], "q2": ["B", "A", "D"]}
order, scores, sources = rrf(rankings)
assert order[:2] == ["A", "B"] or order[:2] == ["B", "A"]
assert len(order) == 4  # 文档 ID 去重
assert len(sources["A"]) == 2

try:
    validate_queries("X2", slots, ["X1 可以启动", "X2 更新后天气"])
    raise AssertionError("drifted queries should fail")
except ValueError:
    pass

print(queries, order, {d: round(scores[d], 5) for d in order})
```

## 实验结果解释

实验限制查询数，用同义槽位检查实体、更新动作、故障现象和否定语义，拒绝“X2 更新后天气”等漂移候选，删除重复查询，再用 RRF 合并文档。它没有调用真实检索器，不能证明两种表达一定带来新证据；真实收益必须与单查询基线在相同候选预算下比较。

## 质量延迟与成本影响

- 串行延迟近似累加，并行可降低墙钟时间但不减少调用量和限流压力。
- 查询数从 1 增至 $m$，最坏检索工作量约增至 $m$ 倍。
- 多查询通常提高候选 Recall，也扩大重排窗口和噪声。
- 先记录新增唯一相关文档数；边际收益接近零时应停止扩展。

## 数据评测与安全风险

对实体、否定、数字、时间和权限范围做逐条约束检查。所有查询共享同一认证身份和允许数据源，生成文本不能扩大权限。评测报告 Query Recall、唯一候选数、最终 Recall@k、答案支持率、P95 延迟与单问成本，并防止用测试答案生成扩展查询造成污染。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 查询变多但候选不变 | 扩展缺乏多样性 | 查询去重率、新增文档数 |
| 相关文档被噪声淹没 | 扩展过宽 | 意图约束、重排窗口、Precision |
| 排名异常 | 直接混加异构分数 | 融合公式、每路名次 |
| 延迟成倍增长 | 串行检索或查询过多 | 并行度、最大查询数、超时 |
| 召回越权文档 | 扩展选择了新数据源 | 服务端 ACL、允许源白名单 |

## 适用与不适用场景

适合术语多样、单查询存在召回盲区且可接受额外成本的场景。不适合精确 ID 查找、低延迟强约束请求，以及单查询已经饱和的知识库。

## 学习收益

你应能限制和校验扩展查询，用 RRF 融合不同排名，衡量新增唯一证据，并说明 Recall、噪声、延迟与成本的交换。

## 给别人讲清楚

“同一个问题派几位用不同关键词的检索员去找，再按名次合并；但每个人都必须找同一个实体、遵守同一张门禁卡。”

## 自检问题

1. 为什么不能直接相加不同检索器的原始分数？
2. 多查询数翻倍时，哪些成本随之增长？
3. 怎样判断新增查询只是在重复已有表达？

## 相关主题

- [RAG 查询改写](13-RAG%20查询改写.md)
- [混合检索 Hybrid Search](02-混合检索%20Hybrid%20Search.md)
- [RAG 重排序](11-RAG%20重排序.md)
- [RAG 检索评测](37-RAG%20检索评测.md)

## 资料来源

- Cormack 等, [Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://dl.acm.org/doi/10.1145/1571941.1572114)，访问日期：2026-09-10。
- LangChain, [How to use the MultiQueryRetriever](https://python.langchain.com/docs/how_to/MultiQueryRetriever/)，访问日期：2026-09-10。
