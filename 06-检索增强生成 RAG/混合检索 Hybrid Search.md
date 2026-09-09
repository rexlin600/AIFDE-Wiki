---
type: pattern
domain:
  - RAG
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - Hybrid Search
  - 混合召回
tags:
  - core
  - rag
---

# 混合检索（Hybrid Search）

## 要解决的问题

单一检索器难以同时稳定处理精确词项与语义改写。BM25 擅长匹配产品编号、专有名词、错误码和原文措辞，却可能漏掉没有共享关键词的同义表达；Dense Retrieval 能用向量相似度找出释义和近义表达，却可能弱化罕见标识符、数字或细粒度否定。混合检索并行生成两类候选，再融合为一个排序列表。

## 上下文

该模式位于 [RAG MOC](./%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md) 的候选召回阶段。语料已经过统一切分、权限过滤和版本管理；同一查询可送入词法检索与向量检索；评测集包含相关文档标注，并按精确词项、释义、中文/英文、代码或编号等查询类型分组。

## 方案

1. **Sparse 分支**：在倒排索引上运行 BM25，利用词频、逆文档频率与文档长度归一化给出候选。
2. **Dense 分支**：用与文档侧兼容的编码器生成查询向量，在向量索引中执行近似或精确近邻搜索。
3. **融合层**：对两组 Top-N 候选做去重，并通过校准后的分数加权或 Reciprocal Rank Fusion（RRF）形成统一排名。
4. **可选 Reranker**：只对融合后的较小候选集计算更昂贵的查询—文档相关度，再截取提供给生成模型的 Top-k。

融合不应直接相加原始 BM25 分数与向量相似度：两者尺度、分布和查询间可比性不同。若采用线性加权，应先在固定评测集上选择归一化方法（如 Min-Max 或 Z-score）并校准权重；Min-Max 容易受极端值和候选窗口影响，Z-score 在候选很少或分布异常时也不稳定。

RRF 绕过原始分数尺度，按每个列表中的名次累计：

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

其中 `rank_i(d)` 是文档 `d` 在第 `i` 个结果列表中的名次，`k` 控制低排名候选的影响。RRF 易于建立基线，但分支权重、候选窗口与常数仍应记录并评测，而不是假设默认值适合所有语料。

## 数据流

```text
查询
 ├─→ BM25 Top-N ─┐
 └─→ Dense Top-N ├─→ 去重与融合 ─→ 可选 Rerank ─→ Top-k 上下文
                 ┘
```

权限与租户约束必须进入每个召回分支，不能等生成后再过滤。索引版本、分词策略、Embedding 模型和候选窗口应随一次检索 Trace 一起记录，便于复现错误。

## 适用条件

- 查询同时包含精确标识符和自然语言描述，例如错误码加故障现象。
- 用户表述与文档用词存在同义、缩写、跨语言或口语差异。
- 错误分析已证明 Sparse 与 Dense 的成功样例有互补性。
- 系统能承担双索引、双路查询和可选 Rerank 的额外延迟与维护成本。

若单一 BM25 已满足质量、延迟和成本目标，或语料规模很小且可直接扫描，则没有必要引入该模式。

## 代价与风险

- 同时维护倒排索引、向量索引、Embedding 版本和删除传播，存储与运维成本上升。
- 双路召回扩大查询开销；Reranker 还增加模型推理延迟和按候选计费的成本。
- 融合权重或候选窗口可能过拟合某个评测集，掩盖某一分支持续退化。
- Dense 分支的模型升级需要重建或迁移文档向量，并验证新旧索引兼容性。

## 失败模式

| 失败模式 | 可观察信号 | 处理方式 |
| --- | --- | --- |
| 直接相加异构分数 | 某分支长期支配最终排名 | 改用 RRF，或固定归一化与权重后重测 |
| 候选窗口过小 | 两个分支各自命中，但融合前已截断 | 提高分支 Top-N，并观察延迟与 Recall@k |
| Dense 模型与文档向量不匹配 | 向量召回突然接近随机或报维度错误 | 绑定模型与索引版本，阻止不兼容发布 |
| 只在融合后做权限过滤 | Top-k 变空、越权文档进入中间结果 | 在每个分支查询边界内执行过滤 |
| Rerank 输入过多 | p95 延迟和成本快速增长 | 依据消融实验缩小融合候选集 |
| 平均指标掩盖退化 | 总分改善但错误码/中文切片下降 | 按查询类型报告指标与失败样例 |

## 实现提示

先建立 BM25、Dense、RRF Hybrid 三组可复现基线，再决定是否增加 Rerank。三组必须共用语料版本、查询集、相关性标注、过滤条件和 `k`，并分别报告 Recall@k、MRR、nDCG、p50/p95 延迟、索引大小与单查询成本。Rerank 是融合之后的精排阶段，不应用它掩盖召回集根本没有相关文档的问题。

线上 Trace 至少记录两个分支的候选及名次、融合贡献、最终文档 ID、过滤原因和耗时。发布前用消融验证“去掉 Sparse”“去掉 Dense”“去掉 Rerank”各自造成的变化。

## 替代方案

- **仅 BM25**：领域词稳定、精确匹配占主导且预算严格时更简单。
- **仅 Dense Retrieval**：释义匹配为主、已有领域适配编码器且精确标识符不重要时可采用。
- **学习排序或单一稀疏神经检索器**：有足够标注、训练与监控能力时可能减少手工融合，但引入训练数据偏差和模型运维。
- **长上下文直接输入**：语料规模可控、单次材料明确且无需独立检索审计时可考虑。

## 相关证据

- [检索基线实验设计](./EXP-20260909-%E6%A3%80%E7%B4%A2%E5%9F%BA%E7%BA%BF.md)：定义 BM25、Dense 与 Hybrid 的同口径对照，不预填实验结果。
- Karpukhin 等，[Dense Passage Retrieval for Open-Domain Question Answering](https://aclanthology.org/2020.emnlp-main.550/)，EMNLP 2020；Dense Retrieval 原始研究证据，访问于 2026-09-09。
- Elastic，[Hybrid search](https://www.elastic.co/docs/solutions/search/hybrid-search)与[Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)；官方实现文档与 RRF 公式，访问于 2026-09-09。
- Thakur 等，[BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://openreview.net/forum?id=wCu6T5xFjeJ)，NeurIPS 2021 Datasets and Benchmarks；异构检索评测基准，访问于 2026-09-09。
