---
type: concept
domain:
  - RAG
depth: L3
importance: core
maturity: draft
created: 2026-09-09
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Hybrid Search, 混合召回]
tags: [retrieval, fusion]
---

# 混合检索 Hybrid Search

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

企业问答既有错误码 `E1047` 这类精确词，也有“登录凭证失效”与“密码过期”这类语义改写。BM25 擅长前者，Dense 检索常擅长后者。混合检索合并两路候选，降低单一检索器的盲区。

## 不理解会造成什么错误

- 直接相加 BM25 分数与余弦相似度，让数值尺度较大的分支支配排序。
- 只在融合后过滤权限，让越权文档进入候选和日志。
- 把融合当作精排，忽略两个分支都没召回相关文档的情况。
- 只看平均 Recall，掩盖编号查询或同义表达切片退化。

## 它在 RAG 链路中的位置

`查询 → Sparse Top-N + Dense Top-N → 去重融合 → 可选重排序 → 上下文`。两个分支必须使用同一语料版本与权限条件；融合输入是文档 ID 和名次，不是生成答案。

## 从客服检索开始

查询“E1047 怎样处理”时，只用 Dense 是简单基线；查询“登录凭证失效怎么办”时，只用 BM25 也是基线。先分别评测，再确认两者命中样例互补，才值得承担双索引成本。

## RRF 怎样绕开分数尺度

对文档 $d$，倒数排名融合为：

$$
\operatorname{RRF}(d)=\sum_{i=1}^{m}\frac{w_i}{c+r_i(d)}
$$

$m$ 是结果列表数，$r_i(d)$ 是从 1 开始的名次，$c>0$ 平滑低名次影响，$w_i$ 是可选分支权重。文档不在某列表时，该列表贡献为 0。公式只使用排名，因此不会把 BM25 的 `12.4` 与余弦的 `0.82` 当成同一单位。

## 最小手算

取 $c=10$。BM25 排名为 `A,B,C`，Dense 为 `C,A,D`：

- $A=1/11+1/12\approx0.1742$；
- $C=1/13+1/11\approx0.1678$；
- $B=1/12\approx0.0833$；$D=1/13\approx0.0769$。

所以融合顺序是 `A,C,B,D`。A 在两路都靠前，累积贡献最大。

## 可执行实验

```python
def rrf(rankings, constant=10):
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (constant + rank)
    return sorted(scores, key=lambda doc: (-scores[doc], doc)), scores

bm25 = ["A", "B", "C"]
dense = ["C", "A", "D"]
order, scores = rrf([bm25, dense])
print(order, {key: round(value, 4) for key, value in scores.items()})
assert order == ["A", "C", "B", "D"]

raw_bm25 = {"A": 12.0, "C": 1.0}
raw_dense = {"A": 0.7, "C": 0.9}
bad = sorted(raw_bm25, key=lambda d: -(raw_bm25[d] + raw_dense[d]))
rescaled = sorted(raw_bm25, key=lambda d: -(raw_bm25[d] / 100 + raw_dense[d]))
assert bad != rescaled  # 异构分数直接相加依赖任意尺度
assert rrf([bm25, dense])[0] == order
```

## 实验结果边界

实验只证明 RRF 对原始分数缩放不敏感，并验证一次名次计算。它不证明 $c=10$ 最优，也不证明 Hybrid 一定优于单路检索；这些结论需要真实 qrels、统一候选窗口和查询切片。

## 质量延迟与成本影响

混合检索可能提高 Recall@k，却需要倒排与向量双索引、双路查询和融合 Trace。两路可并行降低等待时间；总延迟仍受较慢分支约束。扩大 Top-N 常提高召回上限，也会增加网络、融合和重排序成本。

## 数据评测与安全风险

每路都要在候选读取边界执行租户、ACL、时效过滤。索引版本、分词器、Embedding 版本、名次与过滤原因必须可追踪。评测集按精确编号、语义改写、语言和不可回答问题切片，避免只优化热门查询。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 某分支长期支配 | 直接相加异构分数 | 融合公式、原始分数是否进入 RRF |
| 相关文档融合前消失 | 分支 Top-N 太小 | 各分支 Recall@N、截断位置 |
| 结果突然接近随机 | 向量模型与索引不兼容 | 模型、维度、归一化和索引版本 |
| 融合后结果为空 | 权限过滤条件不一致 | 两分支过滤条件与过滤计数 |
| p95 延迟升高 | 慢分支或候选过多 | 分支耗时、Top-N、重排序窗口 |

## 适用与不适用场景

适合精确词项和语义改写并存、两路错误互补的语料。若 BM25 已满足目标、语料很小可精确扫描，或系统无法维护双索引，则先不使用。RRF 是稳健基线，不替代有标注数据支持的校准或学习排序。

## 学习收益

你应能说清两路候选的生命周期位置，手算 RRF，解释为何不直接加分，并设计含消融、权限和延迟的评测。

## 给别人讲清楚

“混合检索像让文字匹配和语义匹配各自投票。RRF 按名次计票，不把两种不同单位的分数硬加；但候选里没有的文档，融合也救不回来。”

## 自检问题

1. 为什么余弦与 BM25 原始分数不能直接相加？
2. 文档不在某一分支时，RRF 怎样处理？
3. 权限过滤为什么必须进入每个召回分支？

## 相关主题

- [BM25 稀疏检索](08-BM25%20稀疏检索.md)
- [Dense 向量检索](09-Dense%20向量检索.md)
- [RAG 重排序](11-RAG%20重排序.md)
- [检索基线实验](01-EXP-20260909-检索基线.md)

## 资料来源

- Cormack 等, [Reciprocal Rank Fusion](https://dl.acm.org/doi/10.1145/1571941.1572114), 2009，访问日期：2026-09-10。
- Elasticsearch, [Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)，访问日期：2026-09-10。
- Thakur 等, [BEIR](https://openreview.net/forum?id=wCu6T5xFjeJ), 2021，访问日期：2026-09-10。
