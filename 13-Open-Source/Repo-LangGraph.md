---
type: source
domain:
  - Agent
  - Open Source
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - LangGraph 源码研究
tags:
  - langgraph
  - source-code
source_type: repository
url: https://github.com/langchain-ai/langgraph
authors:
  - LangChain Inc.
published: 2024
accessed: 2026-09-09
---

# LangGraph 源码研究

## 资料信息

- **官方仓库：** [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **官方文档：** [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- **资料类型：** Python 开源仓库与官方文档
- **许可证：** [MIT License](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)
- **访问日期：** 2026-09-09

本笔记针对访问日的 `main` 分支解释公开结构，不声称对应某个未记录的固定 Commit；复现实验前应选择具体 Release 或 Commit。

## 项目定位

LangGraph 是构建长时运行、有状态工作流与 Agent 的低层编排框架。它提供持久化执行、人工介入和状态管理，但不替代业务工作流建模、工具权限、模型评测或生产运维决策。

## 核心抽象

- `StateGraph`：声明共享状态的 schema、节点、边和条件分支。
- 节点：读取状态并返回局部更新；更新如何合并由状态 channel/reducer 语义决定。
- `START` 与 `END`：描述图的入口和终止边界。
- `CompiledStateGraph`：`compile()` 产出的可运行对象，提供同步、异步、批处理和流式接口。
- Checkpointer：按 `thread_id` 保存版本化检查点，使流程能够暂停、恢复和回放。

## 一次 StateGraph 调用链

以 `graph.invoke(input, config)` 为入口，一条可复查的高层调用链是：

1. 调用方用 `StateGraph(StateSchema)` 建立图，通过 `add_node` 和 `add_edge`/条件边注册状态转换。
2. `StateGraph.compile()` 先校验图，再把节点、边、channel、输入输出与可选 checkpointer 装配为 `CompiledStateGraph`。
3. `CompiledStateGraph` 继承 Pregel 运行时接口；`invoke()` 消费 `stream()` 产生的执行更新，并按所选 `stream_mode` 汇总最终输出。
4. 运行时按超步推进可执行节点：节点读取当前 channel 值，返回状态更新；更新在步边界合并后触发下一批节点，直到到达 `END`、中断或错误。
5. 启用 checkpointer 时，调用配置用唯一 `thread_id` 标识独立运行；复用同一标识可继续该线程的状态。

源码入口：[StateGraph 与 compile](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/state.py)、[Pregel 的 invoke/stream](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/pregel/main.py)。这是结构性摘要，不替代对固定版本源码的逐行跟踪。

## 可靠性设计

- **持久化执行：** Checkpointer 保存执行状态，为失败恢复、暂停与回放提供基础。
- **显式状态更新：** 节点返回更新而不是任意修改隐藏全局状态，便于追踪状态演进；并发写入仍需正确 reducer 或冲突处理。
- **人工介入：** Interrupt 可在节点前后或工作流中暂停，但恢复需要稳定的线程标识和持久化后端。
- **可观测执行：** 流式输出可暴露状态值、更新和事件；能否形成生产证据取决于调用方如何保存 Trace、指标和错误分类。
- **失败边界：** 框架不能自动保证工具幂等。恢复时涉及外部副作用的节点必须自行设计幂等键、确认步骤或补偿操作。

## 值得复刻的最小子集

用纯 Python 复刻一个只支持字典状态的微型执行器：节点返回局部更新；普通边决定下一节点；一个条件路由选择分支；每一步把状态快照写入内存 checkpointer；以 `thread_id` 从中断点恢复。验收重点是状态合并、确定性路由、错误传播与重复恢复，不复刻远程执行、SDK、可视化或完整 Pregel 优化。

## 局限

- 框架抽象会增加状态、channel 和恢复语义的学习成本，小型线性流程可能不值得引入。
- Checkpointer 提供机制，不自动满足数据驻留、加密、保留期、审计和多租户隔离要求。
- Agent 结果质量仍依赖模型、工具、上下文与评测；图执行成功不等于业务结果正确。
- 上游 `main` 会变化；做性能、兼容或源码结论时必须固定版本，不能把本页访问日当成代码版本。

## 与 Wiki 的关系

本仓库是 [Agent](../07-Agent/Agent-MOC.md) 中状态、工作流、审批与恢复的代表性研究对象，也为[生产 AI](../09-Production-AI/Production-AI-MOC.md)中的持久化、Trace 和失败恢复提供源码入口。

## 引用

- [LangGraph 官方仓库](https://github.com/langchain-ai/langgraph)，访问于 2026-09-09。
- [Graph API 官方文档](https://docs.langchain.com/oss/python/langgraph/graph-api)，访问于 2026-09-09。
- [Durable execution 官方文档](https://docs.langchain.com/oss/python/langgraph/durable-execution)，访问于 2026-09-09。
