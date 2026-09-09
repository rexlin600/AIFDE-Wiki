---
type: moc
domain:
  - Projects
  - FDE
depth: L4
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 实战项目
tags:
  - projects
  - evidence
---

# 实战项目 MOC

## 边界

实践代码、测试与发布记录放在独立 GitHub 仓库；本目录只保存项目档案，连接业务问题、设计、固定版本、评测、运行证据与复盘。没有公开仓库或可复现实验时，不把设想写成已完成成果；受保密约束的项目只保留获准公开的脱敏结构。

## 六级项目阶梯

| 层级 | 项目 | 要证明的能力 |
| --- | --- | --- |
| 1 | `ai-foundations-labs` | 数学、机器学习与可复现实验基础 |
| 2 | `llm-engineering-lab` | Tokenizer、Attention、Prompt、模型调用和基础评测 |
| 3 | `production-rag-system` | 摄取、检索、重排、引用与端到端评测 |
| 4 | `enterprise-workflow-agent` | 状态、工具、审批、恢复和企业接口集成 |
| 5 | RAG 或 Agent 生产化加固 | SLO、观测、成本、安全、灰度、回滚与 Runbook |
| 6 | 独立 FDE 综合项目 | Discovery、价值验证、生产交付、采用、交接与复用 |

阶梯表示证据逐步变完整，不要求仓库数量严格等于六。若一个项目能提供多个层级的独立证据，应在档案中逐项链接，不用重复造项目。

## 项目档案最低证据

1. 业务问题、目标用户、基线、成功指标和明确非目标。
2. 架构边界、关键决策、数据与安全约束。
3. 公开 Repository、固定提交、Release 或可复现运行说明；尚不存在时明确标注。
4. 固定评测集、指标口径、失败样例与回归方法，不只展示最好结果。
5. 运行期质量、延迟、成本、可靠性和采用证据。
6. 故障、错误假设、范围变化、交接与可复用结论。

## 当前档案

- [AIFDE Wiki 项目档案](01-PRJ-AIFDE%20Wiki.md)：以本 Wiki 自身示范公开知识产品的边界、架构和质量门禁。

## 路线连接

- [AI/FDE 七阶段路线](../B-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/00-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF-MOC.md)定义各阶段项目增量。
- [FDE 综合项目](../B-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/07-%E9%98%B6%E6%AE%B5%206-FDE%20%E7%BB%BC%E5%90%88%E9%A1%B9%E7%9B%AE.md)定义最终证据包。
- [FDE 能力模型](../A-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/02-FDE%20%E8%83%BD%E5%8A%9B%E6%A8%A1%E5%9E%8B.md)用于判断证据对应的能力维度和深度。
- [开源研究](../N-%E5%BC%80%E6%BA%90/00-%E5%BC%80%E6%BA%90-MOC.md)补充依赖选择、调用链和最小复刻证据。
