---
type: moc
domain:
  - RAG
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 检索增强生成
tags:
  - core
  - rag
---

# RAG MOC

## 领域边界

本领域覆盖检索增强生成（Retrieval-Augmented Generation，RAG）从数据进入、候选召回、上下文构造到带依据生成和评测的完整链路。目标是按查询、数据与风险选择可验证的组合；不把向量数据库等同于 RAG，也不展开通用 Agent 编排和平台运维。

## 前置知识

- [LLM](../05-LLM/LLM-MOC.md)中的 Embedding、上下文、结构化输出、幻觉与模型选型。
- [机器学习](../03-Machine-Learning/Machine-Learning-MOC.md)中的数据拆分、排序指标、基线和错误分析。
- 能处理文档、SQL 与 API 数据，并理解身份、权限、版本和删除传播。

## 推荐顺序

1. 先完成数据摄取、索引、Sparse/Dense 基线和可回答性评测。
2. 再用 Hybrid、Metadata、Rerank 与上下文策略解决可定位的召回或排序错误。
3. 按查询复杂度加入改写、路由、迭代或图结构，不默认堆叠高级方法。
4. 最后补齐权限、时效、多租户、引用与端到端运行证据，并与长上下文、工具和微调比较。

## 核心主题

### 1. 数据摄取与索引

解析、清洗、切分、去重、元数据、Embedding、倒排/向量索引、增量更新、版本和删除传播；核心证据是索引可重建且来源可追踪。

### 2. Sparse、Dense、Hybrid 检索

用 Sparse 处理精确词项、Dense 处理语义近似，以分数归一化或 Reciprocal Rank Fusion 组合 Hybrid；比较 Recall@k、nDCG、延迟与成本。

### 3. Metadata、Rerank、Parent-Child 和 Small-to-Big

Metadata 在召回前后约束候选，Rerank 改善排序，Parent-Child 与 Small-to-Big 分离检索粒度和生成上下文；选择应由错误分析驱动。

### 4. Query Rewrite、Multi-Query、Decomposition、Routing 和 HyDE

Rewrite 修正表达，Multi-Query 扩大召回，Decomposition 拆解复合问题，Routing 选择数据源或检索器，HyDE 用假设文档辅助语义检索；均需防止意图漂移和成本失控。

## 常用主题

### 5. Conversational、Multi-hop、Adaptive 和 Iterative RAG

Conversational RAG 管理指代与会话边界，Multi-hop 聚合多份证据，Adaptive RAG 按查询决定是否及如何检索，Iterative RAG 依据中间结果继续检索；必须设置终止与预算条件。

### 6. Corrective RAG、Self-RAG 和 Agentic RAG

Corrective RAG 在低质量证据时纠正或换源，Self-RAG 让模型判断检索与答案支持度，Agentic RAG 以工具循环规划检索；复杂度增加前先证明静态流程不足。

### 8. SQL、结构化、多模态、权限、多租户、时效和流式 RAG

按数据形态选择 SQL、结构化查询或多模态检索；把租户与行级权限置于检索边界内，处理数据驻留、时间过滤、增量索引和流式更新，不能只在生成后过滤。

### 9. 检索、生成、引用和端到端评测

检索看 Recall@k、MRR 或 nDCG，生成看正确性与 Faithfulness，引用看覆盖、归属和可打开性，端到端看任务成功、拒答、延迟和成本；按查询类型保留失败样例。

## 拓展视野

### 7. GraphRAG、Knowledge Graph RAG、Hierarchical RAG 和 RAPTOR

GraphRAG 面向实体关系与全局主题，Knowledge Graph RAG 使用显式本体或图查询，Hierarchical RAG 按层级缩小范围，RAPTOR 用递归聚类与摘要建立树；收益必须覆盖建图、更新和查询成本。

### 10. RAG、长上下文、工具和微调的选型边界

RAG 适合动态、可引用知识；长上下文适合规模可控且单次相关的材料；工具适合实时查询与确定性动作；微调适合稳定行为、格式或领域模式，不用于记忆频繁变化事实。可组合，但要分别评测贡献。

## 组合示例

- 企业政策问答：增量摄取 + Hybrid + Metadata 租户过滤 + Rerank + Parent-Child + 引用评测，先保证权限与依据，再优化回答。
- 多轮故障排查：Conversational + Query Rewrite + Routing + Iterative RAG，在日志、Runbook 与工单间逐步补证，并用预算和终止条件限制循环。
- 跨文档研究：Decomposition + Multi-hop + GraphRAG + Corrective RAG，分别验证子问题召回、关系证据和纠错是否带来净收益。
- 实时经营分析：SQL 工具 + 结构化 RAG + 时效过滤 + 权限控制，文档解释走检索，实时数值走工具，避免用旧文本回答动态事实。

## 最小实验

- 在同一语料和问题集上比较 Dense、Hybrid、Rerank 与一种高级方案，报告质量、引用、延迟和成本。
- 注入删除、权限、跨文档、时效与不可回答样例，验证索引传播、过滤和拒答。
- 对一种查询改写或分解方法做消融，记录其改善与意图漂移样例。

## 项目

- 在 `production-rag-system` 中实现版本化摄取、四类检索配置、权限过滤、引用、离线评测、API 和可重建索引。
- 以[阶段 3：RAG 工程](../01-Roadmap/Phase-3-RAG-Engineering.md)的退出证据约束方案对比与复盘。

## 开源研究

- 跟踪 LlamaIndex 从摄取到检索和响应合成的一条调用链。
- 跟踪 RAGFlow 的文档解析、索引、检索与服务边界。
- 复刻 BM25、向量召回与 Reciprocal Rank Fusion 的最小链路，再比较 GraphRAG 的额外成本。

## 面试入口

- 解释“召回好但答案差”和“答案对但引用错”的定位顺序。
- 设计带租户权限、删除传播、时效与审计的企业 RAG。
- 用消融数据说明何时选择 Hybrid、Rerank、GraphRAG、长上下文、工具或微调。

## 相邻领域

- [LLM](../05-LLM/LLM-MOC.md)：提供 Embedding、生成、上下文和模型接口。
- [Agent](../07-Agent/Agent-MOC.md)：把检索作为受控工具，并处理多步决策。
- [多模态 AI](../08-Multimodal-AI/Multimodal-AI-MOC.md)：扩展图像、文档和音频检索。
- [生产 AI](../09-Production-AI/Production-AI-MOC.md)与[安全治理](../10-AI-Safety-Governance/AI-Safety-Governance-MOC.md)：提供运行、评测、权限和防护边界。
