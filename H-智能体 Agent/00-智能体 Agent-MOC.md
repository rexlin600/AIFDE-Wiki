---
type: moc
domain:
  - Agent
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 智能体工程
tags:
  - core
  - agent
---

# Agent MOC

## 领域边界

本领域覆盖模型在受控循环中读取状态、选择工具、观察结果并推进任务的系统。重点是 Workflow/Agent 边界、可恢复执行、评测与权限；确定性流程足够时不为追求自主性引入 Agent。

## 前置知识

- [LLM](../F-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM/00-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM-MOC.md)中的结构化输出、Function Calling、上下文和模型选型。
- [RAG](../G-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG/00-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md)中的证据检索、引用、权限与失败分类。
- API 契约、状态机、超时、重试、幂等、持久化和基本分布式系统知识。

## 推荐顺序

1. 先区分 Workflow 与 Agent，用严格 Tool Schema 和显式 State 实现单 Agent。
2. 加入 Session、Memory、HITL、Checkpoint、重试、恢复和幂等。
3. 再比较 ReAct、Plan-and-Execute、Reflection 与 Routing，并以 Trace Eval 约束循环。
4. 最后在职责确实可分时引入 Supervisor、多 Agent、MCP 或 A2A。

## 核心主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| Workflow/Agent 边界 | 固定控制流、模型决策权、适用条件、终止与失败边界 | L3 | core |
| Tool 与 Schema | 工具描述、输入输出校验、权限、副作用、超时与错误语义 | L3 | core |
| State、Session 与 Memory | 运行状态、会话隔离、短期/长期记忆、裁剪与生命周期 | L3 | core |
| HITL | 审批、拒绝、参数修改、升级、超时和审计 | L3 | core |
| 可靠执行 | Checkpoint、有限重试、恢复、补偿、幂等键和回放 | L3 | core |
| Trace Eval | 轨迹、工具选择、参数、任务成功、越权、延迟与成本 | L3 | core |

## 常用主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| ReAct | 推理与行动交替、观察回填、循环与终止控制 | L3 | common |
| Plan-and-Execute | 计划生成、步骤执行、重规划与计划漂移 | L2 | common |
| Routing | 意图分类、能力选择、Fallback 和确定性分流 | L3 | common |
| 单/多 Agent 与 Supervisor | 职责、Handoff、共享状态、冲突、聚合和失败隔离 | L2 | common |
| Browser/Code/Data Agent | 页面交互、沙箱执行、数据查询、授权和结果验证 | L2 | common |
| 安全与成本控制 | 最小权限、隔离、步数/Token/时间预算和敏感操作门禁 | L3 | common |

## 拓展视野

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| Reflection | 自检、批评与修订的触发条件、收益和错误放大 | L2 | extension |
| MCP | Client/Server、能力发现、传输、信任边界和授权 | L3 | extension |
| A2A | Agent 间能力声明、任务协作、身份和互操作边界 | L2 | extension |
| 长程与自改进 | 长任务状态、技能积累、版本治理和不可控风险 | L4 | extension |

## 最小实验

- 用普通 Python 实现有限状态执行器，支持三个 Tool、Checkpoint、有限重试和 HITL。
- 对比确定性 Workflow、ReAct 与 Plan-and-Execute 的任务成功率、循环率、延迟和成本。
- 注入工具超时、参数错误、进程中断和重复请求，验证恢复与幂等。

## 项目

- 在 `enterprise-workflow-agent` 中交付状态 Schema、审批、持久化、失败注入、Trace、评测集和威胁模型。
- 以[阶段 4：Agent 工程](../B-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/05-%E9%98%B6%E6%AE%B5%204-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent%20%E5%B7%A5%E7%A8%8B.md)的退出证据约束可靠性与答辩。

## 开源研究

- 跟踪 LangGraph 从节点调度到 Checkpoint 和人工介入的调用链。
- 跟踪 OpenAI Agents SDK 的 Agent 循环、Handoff、Guardrail 和 Trace。
- 运行只读 MCP Server，记录能力发现、参数校验和权限边界。

## 面试入口

- 区分 Workflow、单 Agent 和多 Agent，并说明何时不用 Agent。
- 设计付款或通知工具的审批、幂等、重试、恢复和补偿。
- 用 Trace 排查误选工具、错误参数、循环、越权与恢复后状态不一致。

## 相邻领域

- [RAG](../G-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG/00-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md)：为 Agent 提供受权限约束的外部证据。
- [生产 AI](../J-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI/00-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI-MOC.md)：提供网关、可观测性、部署和容量控制。
- [安全治理](../K-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86/00-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86-MOC.md)：限定工具、数据和多 Agent 的信任边界。
- [FDE 实践](../L-FDE%20%E5%AE%9E%E8%B7%B5/00-FDE%20%E5%AE%9E%E8%B7%B5-MOC.md)：把 Agent 设计嵌入真实客户流程与验收指标。
