---
type: moc
domain:
  - Roadmap
  - Agent
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 阶段 4 Agent 工程
tags:
  - core
  - roadmap
---

# 阶段 4：Agent 工程

## 建议周期与进入条件

**建议周期：8～12 周，每周 5～10 小时。** 时间是建议；优先把一个受控工作流做可靠，而不是增加 Agent 数量。

进入条件是能实现可靠的 LLM 结构化输出，理解 RAG 的检索、引用和权限失败，能为外部 API 设计超时、重试、幂等和测试替身。

## 推荐深度与核心知识

单 Agent/工作流、Tool 与状态管理达到 L3；多 Agent 与协议互操作至少达到 L2：

领域入口：[Agent](../L-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent/00-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent-MOC.md)，并按需回到 [RAG](../K-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG/00-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md)或进入[安全治理](../O-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86/00-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86-MOC.md)明确证据与工具权限。

- Workflow 与 Agent 的控制权差异，以及何时不用 Agent。
- Tool Schema、权限、副作用、超时、错误语义、幂等和补偿操作。
- 显式 State、短期/长期 Memory、上下文裁剪和数据生命周期。
- 路由、循环、终止条件、预算、并发与确定性节点。
- Human-in-the-Loop（人在回路，HITL）的审批、拒绝、修改与升级。
- Checkpoint、重试、恢复、Fallback、Trace 和回放。
- Agent Eval：轨迹、工具选择、参数、任务成功、安全和成本。
- MCP Servers 的信任边界；多 Agent 只在职责与信息边界明确时采用。

## 必做实验

构建 `enterprise-workflow-agent`，模拟一个具有读取、分析、写入和通知步骤的企业流程。系统必须包含：

1. 至少三个具有严格 Schema 的 Tool，其中一个有副作用。
2. 显式 State 和 Memory 生命周期，不把全部历史无限塞入上下文。
3. 副作用前人工审批，支持批准、拒绝和修改参数。
4. 超时、限流、瞬时失败和不可重试错误的差异化处理。
5. Checkpoint 与进程重启后的恢复，副作用操作使用幂等键。
6. 端到端 Tracing，以及覆盖成功、误选工具、错误参数、循环和越权的 Agent Eval。

## 外部 GitHub 项目

- [LangGraph](https://github.com/langchain-ai/langgraph)：研究显式状态、节点、边、Checkpoint 与人工介入。
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)：研究 Agent 循环、Handoff、Guardrail 与 Tracing。
- [MCP Servers](https://github.com/modelcontextprotocol/servers)：分析标准化工具服务器、输入边界与安全注意事项。

## 开源实践：使用、源码跟踪、最小复刻、可选贡献

- **开源使用：** 分别运行 LangGraph 或 Agents SDK 的状态/工具示例，以及一个只读 MCP Server；固定版本和权限。
- **源码跟踪：** 从一次 Agent run 入口跟踪到模型决策、工具执行、状态更新与 Trace 记录。
- **最小复刻：** 用普通 Python 实现一个有限状态工作流执行器，支持工具注册、Checkpoint、有限重试和人工审批。
- **可选贡献：** 为工具 Schema、Checkpoint 恢复或错误处理的文档/测试问题提供可复现改进。

## 项目增量

独立仓库 `enterprise-workflow-agent` 必须包含工作流图、Tool 契约、状态 Schema、持久化、审批界面或 API、失败注入、Trace、评测集和威胁模型。默认使用单 Agent 或确定性工作流；若采用多 Agent，设计记录必须证明职责分离带来的收益。

## 评测与复盘

报告任务成功率、正确工具选择率、参数正确率、无效循环率、恢复成功率、越权率、p95 延迟和成本。对失败按模型决策、工具、状态、权限、外部系统和人类审批分类；比较 Workflow 与更开放 Agent 的可靠性差异。

## 面试训练

- 区分 Workflow、Agent 和多 Agent，并给出不应使用 Agent 的场景。
- 设计具有副作用工具的审批、幂等、重试和补偿机制。
- 排查 Agent 重复发起付款/通知、陷入循环或恢复后状态不一致。
- 解释 Memory 与 State 的边界，以及 MCP Server 的信任和权限模型。
- 使用 Trace 和评测数据答辩框架选择与控制权设计。

## 退出证据

- `enterprise-workflow-agent` 的固定版本、架构图、测试、威胁模型和复现说明。
- Tool、State、Memory、审批、重试、恢复、Tracing 和 Agent Eval 的运行证据。
- 至少一次进程中断恢复和一次越权/失败注入演练。
- 一条开源 Agent 调用链和有限状态执行器最小复刻。
- 能在面试中解释控制权、安全、可靠性和多 Agent 取舍。

证据齐全后进入 [阶段 5：生产 AI](06-%E9%98%B6%E6%AE%B5%205-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI.md)，并以[生产 AI MOC](../N-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI/00-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI-MOC.md)组织加固能力。
