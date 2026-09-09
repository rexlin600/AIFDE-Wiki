---
type: moc
domain:
  - Roadmap
  - Production AI
  - AI Safety Governance
depth: L4
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 阶段 5 生产 AI
tags:
  - core
  - roadmap
---

# 阶段 5：生产 AI

## 建议周期与进入条件

**建议周期：6～10 周，每周 5～10 小时。** 时间是建议；本阶段不是重写项目，而是用指标和演练加固一个已经能端到端运行的 RAG 或 Agent 系统。

进入条件是拥有阶段 3 或阶段 4 的可运行项目、固定评测集、基础 Trace 和明确的失败分类。若项目仍无法稳定复现，应先补齐前一阶段退出证据。

## 推荐深度与核心知识

核心生产能力达到 L3，并用一次受控上线/演练向 L4 证据推进：

- 模型网关、供应商抽象、路由、限流、预算、缓存和 Fallback。
- 超时、重试、熔断、背压、幂等、队列与优雅降级。
- Logs、Metrics、Traces、评测结果关联和 SLI/SLO。
- Prompt Injection、数据外泄、越权、内容风险、审计与最小权限。
- 容量模型、负载测试、长尾延迟、成本上限与性能剖析。
- Docker 镜像、Kubernetes 资源/探针/伸缩、配置和秘密管理。
- CI/CD、回归评测门禁、灰度、回滚、Runbook 和事故复盘。

## 必做实验

选择 `production-rag-system` 或 `enterprise-workflow-agent` 进行生产加固：

1. 在统一模型网关后接入主模型与 Fallback，验证超时、限流和供应商错误。
2. 为安全且适合缓存的请求设计 Key、TTL 和失效条件，并测量命中收益与陈旧风险。
3. 建立质量、流量、错误、延迟、Token/成本和安全事件的可观测性。
4. 执行正常、突发、持续和故障注入负载测试，确定容量拐点。
5. 容器化并部署到本地或测试 Kubernetes，验证探针、资源限制和滚动更新。
6. 让 CI/CD 执行测试、评测、安全检查和部署门禁，并完成一次回滚演练。

## 外部 GitHub 项目

- [LiteLLM](https://github.com/BerriAI/litellm)：研究模型网关、供应商抽象、路由与成本控制。
- [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python)：建立跨服务 Trace 与指标关联。
- [Prometheus Python Client](https://github.com/prometheus/client_python)：暴露应用与模型工作流指标。
- [Kubernetes Examples](https://github.com/kubernetes/examples)：对照部署、服务、探针和资源配置。

## 开源实践：使用、源码跟踪、最小复刻、可选贡献

- **开源使用：** 固定版本接入 LiteLLM、OpenTelemetry 和 Prometheus 客户端中的必要组件，保留最小配置与数据流说明。
- **源码跟踪：** 跟踪一次网关请求的路由/Fallback，或一个 Span 从创建、传播到导出的调用链。
- **最小复刻：** 实现一个只覆盖当前项目需求的模型适配层，支持超时、有限重试、Fallback、预算记录和结构化指标。
- **可选贡献：** 为供应商错误映射、Telemetry 示例或部署文档的可复现问题补充测试/文档。

## 项目增量

不创建只为展示工具的新系统；在既有 RAG 或 Agent 仓库增加网关、缓存、Fallback、可观测性、安全控制、负载测试、Docker/Kubernetes、CI/CD、Runbook 和回滚脚本。基础设施配置与应用版本共同审查，秘密通过外部注入。

## 评测与复盘

设定质量、可用性、p95 延迟和单请求成本 SLO，展示加固前后与正常/降级路径的对比。至少复盘一次模型超时、检索/工具依赖失败、恶意输入或部署回滚；说明检测、响应、恢复时间与防复发措施。

## 面试训练

- 设计多模型网关，解释路由、Fallback、限流、缓存和成本预算。
- 定义一个 AI 系统的 SLI/SLO，并关联离线评测与线上 Trace。
- 应对 Prompt Injection、敏感数据泄漏、越权工具调用和审计要求。
- 排查 p95 延迟激增或 Token 成本翻倍，给出验证顺序。
- 讲述一次负载/故障演练和回滚决策，量化可靠性变化。

## 退出证据

- 既有项目的生产加固版本和可审查配置，不另建空壳演示仓库。
- 网关、缓存、Fallback、Telemetry、安全、负载和 CI/CD 的测试证据。
- Docker/Kubernetes 可复现部署、容量报告、SLO 仪表盘或导出快照。
- Runbook、一次故障注入、一次回滚和一份无责复盘。
- 一条开源生产调用链、最小适配层和完整系统设计答辩。

证据齐全后进入 [阶段 6：FDE 综合项目](Phase-6-FDE-Capstone.md)。
