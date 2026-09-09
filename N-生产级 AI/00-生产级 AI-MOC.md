---
type: moc
domain:
  - Production AI
depth: L4
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 生产 AI
  - AI 生产工程
tags:
  - core
  - production-ai
---

# 生产 AI MOC

## 领域边界

本领域覆盖 AI 系统从数据管道、模型访问、评测与可观测性到部署、扩缩容和运行响应的生命周期。目标是让质量、可靠性、延迟与成本可度量和可回滚；不取代具体 RAG、Agent 或安全领域设计。

## 前置知识

- 至少一个可运行的 [RAG](../K-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG/00-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md) 或 [Agent](../L-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent/00-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent-MOC.md) 项目及固定评测集。
- HTTP 服务、异步任务、队列、容器、指标、日志、Trace 与 CI/CD 基础。
- [安全治理](../O-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86/00-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86-MOC.md)中的最小权限、秘密与审计要求。

## 推荐顺序

1. 建立数据质量、版本、离线 Evals、线上指标和错误分类。
2. 引入模型网关、路由、缓存、限流、超时与 Fallback。
3. 用 Tracing、成本和延迟分解定义 SLI/SLO，并做负载与故障实验。
4. 最后完成 vLLM、Docker、Kubernetes、CI/CD、容量规划和回滚演练。

## 核心主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| 数据工程 | 契约、质量、血缘、版本、批流处理、回填和删除传播 | L3 | core |
| 模型网关与路由 | 供应商抽象、能力路由、Fallback、错误映射和退出策略 | L3 | core |
| Evals | 固定集、回归、分群错误、发布门禁、在线反馈与漂移 | L4 | core |
| Tracing | 跨模型/检索/工具 Span、关联 ID、采样、回放与隐私 | L3 | core |
| 成本与延迟 | Token、GPU、缓存、p50/p95/p99、首 Token 与吞吐 | L3 | core |
| 容量规划 | 并发、到达率、队列、资源瓶颈、负载模型和余量 | L3 | core |

## 常用主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| 缓存与限流 | Key、TTL、失效、陈旧风险、配额、背压和公平性 | L3 | common |
| LLM-as-Judge | Rubric、成对比较、位置偏差、校准、人工抽检和成本 | L3 | common |
| vLLM | 模型加载、连续批处理、KV Cache、量化、吞吐与显存 | L3 | common |
| Docker 与 Kubernetes | 镜像、秘密、资源、探针、伸缩、调度和滚动更新 | L3 | common |
| CI/CD | 测试、评测、安全扫描、灰度、审批、回滚和制品追踪 | L3 | common |

## 拓展视野

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| 分布式推理 | 张量/流水线并行、批调度、多节点通信和故障恢复 | L4 | extension |
| 多区域与边缘 | 数据一致性、驻留、容灾、网络延迟和有限资源 | L4 | extension |
| GPU 平台与 FinOps | 配额、调度、利用率、采购和单位经济性 | L3 | extension |

## 最小实验

- 在统一网关后比较主模型与 Fallback，注入超时、限流和供应商错误。
- 建立离线 Evals 与 LLM-as-Judge 校准集，验证其与人工判断的一致性。
- 执行正常、突发、持续和故障负载，输出容量拐点、SLO 与成本曲线。

## 项目

- 对既有 RAG 或 Agent 项目增加网关、缓存、Telemetry、负载测试、容器部署、CI/CD、Runbook 和回滚。
- 以[阶段 5：生产 AI](../F-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/06-%E9%98%B6%E6%AE%B5%205-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI.md)的退出证据完成加固。

## 开源研究

- 跟踪 LiteLLM 的请求路由、Fallback 和成本记录路径。
- 跟踪 OpenTelemetry Span 的创建、传播、导出和脱敏。
- 跟踪 vLLM 请求调度、批处理、KV Cache 与服务入口。

## 面试入口

- 设计多模型网关，解释路由、缓存、限流、Fallback 与预算。
- 定义质量、可用性、p95 延迟和单请求成本 SLO。
- 排查长尾延迟、成本翻倍、容量不足与回归评测失败。

## 相邻领域

- [RAG](../K-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG/00-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md)、[Agent](../L-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent/00-%E6%99%BA%E8%83%BD%E4%BD%93%20Agent-MOC.md)和[多模态 AI](../M-%E5%A4%9A%E6%A8%A1%E6%80%81%20AI/00-%E5%A4%9A%E6%A8%A1%E6%80%81%20AI-MOC.md)：提供被生产化的应用链路。
- [安全治理](../O-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86/00-AI%20%E5%AE%89%E5%85%A8%E4%B8%8E%E6%B2%BB%E7%90%86-MOC.md)：提供发布与运行的安全门禁。
- [FDE 实践](../P-FDE%20%E5%AE%9E%E8%B7%B5/00-FDE%20%E5%AE%9E%E8%B7%B5-MOC.md)：把 SLO、Runbook 与运行证据纳入客户验收。
