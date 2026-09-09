---
type: moc
domain:
  - Roadmap
  - AI Engineering
depth: L2
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 阶段 0 工程基线
tags:
  - core
  - roadmap
---

# 阶段 0：AI 工程基线

## 建议周期与进入条件

**建议周期：1～2 周，每周 5～10 小时。** 时间是建议，不是硬期限。

进入本阶段前，应能使用至少一种编程语言完成小型程序，理解文件、进程、HTTP 和 JSON 的基本概念，并能执行 Git clone、commit 和 branch。Python 经验不足可以在本阶段补齐，不要求先掌握机器学习。

## 推荐深度与核心知识

目标是达到 L2（可复现实验）：

- Python 虚拟环境、依赖锁定、类型标注、异常处理、日志和 pytest。
- Notebook 的探索用途与脚本/包的可复现边界。
- FastAPI、HTTP 请求、流式响应、超时、重试和结构化错误。
- 模型 API 的消息、Token、结构化输出、速率限制与费用记录。
- 本地模型运行的模型文件、量化、内存/显存和服务接口。
- GitHub 项目的 README、许可证、Issue、Release、Commit 固定和最小 CI。

## 必做实验

建立一个相同任务的双路径实验：路径 A 调用一个模型 API，路径 B 调用本地模型。两条路径使用同一输入 Schema 和输出 Schema，由 FastAPI 暴露 `/generate` 与 `/health`，并完成以下验证：

1. 正常输入得到可解析的结构化结果。
2. 无效输入返回明确的 4xx 错误。
3. 上游超时触发有限重试并留下不含敏感信息的日志。
4. 记录首次 Token 延迟、总延迟、输入输出 Token 和估算成本。
5. 在干净环境中按 README 从安装到测试完整复现。

Notebook 只用于探索请求和结果；最终可运行路径必须进入 Python 包、测试和命令行脚本。

## 外部 GitHub 项目

- [FastAPI](https://github.com/fastapi/fastapi)：研究请求校验、依赖注入和异常处理入口。
- [JupyterLab](https://github.com/jupyterlab/jupyterlab)：理解交互式环境的组成与可复现边界。
- [Ollama](https://github.com/ollama/ollama)：运行本地模型，观察模型加载、服务 API 与资源占用。

## 开源实践：使用、源码跟踪、最小复刻、可选贡献

- **开源使用：** 固定 FastAPI 与 Ollama 的版本，跑通一个 API 服务和一个本地模型请求，保存版本与复现命令。
- **源码跟踪：** 从 FastAPI 路由装饰器跟踪到请求校验或异常响应；记录入口、关键对象和错误传播。
- **最小复刻：** 仅用 Python 标准库写一个接受 JSON、校验字段并调用可替换模型适配器的最小 HTTP 服务，对比它与 FastAPI 的边界。
- **可选贡献：** 复现一个文档或最小示例 Issue，提交可验证的文档澄清或测试修复；没有合适问题时只保留研究记录。

## 项目增量

创建独立仓库 `ai-engineering-playground`，至少包含 API 与本地模型两个适配器、FastAPI 服务、一个 Notebook、单元测试、环境示例、许可证和从零运行说明。配置由环境变量注入，只提交 `.env.example`，不得提交真实凭据。

## 评测与复盘

用不少于 10 条正常、边界和无效输入比较两条路径的成功率、Schema 合规率、延迟和成本。复盘 Notebook 到服务代码的迁移、最难复现的环境问题，以及何时应选远程 API 或本地模型。

## 面试训练

- 解释 Notebook、脚本、服务三种形态的适用边界。
- 设计一个可替换模型供应商的 Python API，并说明超时、重试和密钥管理。
- 排查“本地模型可运行但 FastAPI 请求持续超时”的问题。
- 用 3 分钟展示 `ai-engineering-playground` 的复现路径和一项量化结果。

## 退出证据

- 一个带版本标签的公开 `ai-engineering-playground` 仓库和通过的测试/CI。
- API 与本地模型各一条可复现命令、样例输入输出及环境说明。
- 包含 Schema 合规率、延迟、Token/成本的对比表和至少三个失败样例。
- 一份 FastAPI 关键调用链记录和一个独立最小复刻。
- 一段能回答方案取舍、失败排查与安全边界的项目演示。

证据齐全后进入 [阶段 1：AI/ML 基础](Phase-1-AI-ML-Foundations.md)。
