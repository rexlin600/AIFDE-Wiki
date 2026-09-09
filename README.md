# AIFDE Wiki

## 项目定位

AIFDE Wiki 是一个面向公开阅读的 AI 应用工程与前沿部署工程（Forward Deployed Engineering，FDE）知识库。仓库采用稳定领域目录、内容地图（Map of Content，MOC）和证据化笔记组织知识；GitHub 直接阅读是最低体验基线，Obsidian 仅用于增强本地编辑。

本项目不建设个人 Dashboard、日记、私人待办或学习完成率，也不在仓库内保存完整实战项目代码。内容建设追求清晰的知识依赖、可复现证据和可解释的工程取舍，不承诺所有主题达到同等深度；标记为 `extension` 的内容默认只要求达到视野层的 L1 理解。

## 目标读者

- 已有后端或全栈经验、准备转向 AI 应用工程的研发人员。
- 需要补齐交付、治理和客户现场能力的 FDE 候选人。
- 希望用公开、可验证方式维护 AI 工程知识的贡献者。

## 阅读入口

- 初次访问：先读[使用指南](00-Guide/How-To-Use.md)和[术语表](00-Guide/Glossary.md)。
- 建立全局视角：进入[AI 全局知识地图](00-Guide/AI-Knowledge-Map.md)。
- 规划学习顺序：进入[AI/FDE 七阶段路线](01-Roadmap/Roadmap-MOC.md)。
- 评估交付能力：进入[FDE 能力模型](00-Guide/FDE-Competency-Model.md)。

所有内部入口均使用 GitHub 可直接打开的相对 Markdown 链接，不依赖 Obsidian Wiki Link 或 Dataview。

## AI 知识地图

[AI 全局知识地图](00-Guide/AI-Knowledge-Map.md)描述各知识领域的依赖关系、建议深度和实践连接。它是按问题定位内容的首选入口，而不是个人学习进度面板。

## FDE 能力模型

[FDE 能力模型](00-Guide/FDE-Competency-Model.md)覆盖发现与定义、AI 系统设计、实施集成、评测、安全治理、可靠性运营以及沟通交接，并说明每项能力需要什么公开证据。

## 七阶段路线

[路线总览](01-Roadmap/Roadmap-MOC.md)按进入条件、学习目标、实践任务和退出证据组织七个阶段：

1. [Phase 0：现状基线](01-Roadmap/Phase-0-Baseline.md)
2. [Phase 1：AI/ML 基础](01-Roadmap/Phase-1-AI-ML-Foundations.md)
3. [Phase 2：LLM 工程](01-Roadmap/Phase-2-LLM-Engineering.md)
4. [Phase 3：RAG 工程](01-Roadmap/Phase-3-RAG-Engineering.md)
5. [Phase 4：Agent 工程](01-Roadmap/Phase-4-Agent-Engineering.md)
6. [Phase 5：生产 AI](01-Roadmap/Phase-5-Production-AI.md)
7. [Phase 6：FDE 综合项目](01-Roadmap/Phase-6-FDE-Capstone.md)

## 领域导航

| 领域 | 入口 |
| --- | --- |
| AI 基础 | [AI Foundations MOC](02-AI-Foundations/AI-Foundations-MOC.md) |
| 机器学习 | [Machine Learning MOC](03-Machine-Learning/Machine-Learning-MOC.md) |
| 深度学习 | [Deep Learning MOC](04-Deep-Learning/Deep-Learning-MOC.md) |
| 大语言模型 | [LLM MOC](05-LLM/LLM-MOC.md) |
| 检索增强生成 | [RAG MOC](06-RAG/RAG-MOC.md) |
| 智能体 | [Agent MOC](07-Agent/Agent-MOC.md) |
| 多模态 AI | [Multimodal AI MOC](08-Multimodal-AI/Multimodal-AI-MOC.md) |
| 生产 AI | [Production AI MOC](09-Production-AI/Production-AI-MOC.md) |
| AI 安全与治理 | [AI Safety & Governance MOC](10-AI-Safety-Governance/AI-Safety-Governance-MOC.md) |
| FDE 实践 | [FDE Practice MOC](11-FDE-Practice/FDE-Practice-MOC.md) |
| 岗位市场 | [Job Market MOC](15-Job-Market/Job-Market-MOC.md) |

## 代表性项目与实验

- [AIFDE Wiki 项目档案](12-Projects/PRJ-AIFDE-Wiki.md)：展示公开知识产品的范围、架构、验证证据与复盘连接。
- [检索基线实验设计](06-RAG/EXP-20260909-Retrieval-Baseline.md)：展示可证伪假设、变量、指标和复现要求。
- [实战项目 MOC](12-Projects/Projects-MOC.md)：索引外部项目仓库及其版本化证据。

## 开源研究

[开源研究 MOC](13-Open-Source/Open-Source-MOC.md)组织仓库筛选、源码调用链、最小复刻和贡献记录；[LangGraph 仓库研究](13-Open-Source/Repo-LangGraph.md)提供 `source` 类型样例。研究第三方项目时必须先检查其许可证，并将原始项目、许可证和版本记录清楚。

## 面试准备

[面试准备 MOC](14-Interview/Interview-MOC.md)按能力组织问题、回答结构、追问和项目证据；[如何评测一个 RAG 系统](14-Interview/%E5%A6%82%E4%BD%95%E8%AF%84%E6%B5%8B%E4%B8%80%E4%B8%AARAG%E7%B3%BB%E7%BB%9F.md)展示从指标、数据集到上线监控的回答方式。

## 内容状态

每篇笔记通过 `maturity` 标记状态：`draft` 表示仍需补齐或复核，`reviewed` 表示主要来源和结论已检查，`stable` 表示已有可复现证据，`needs-update` 表示已知内容需要重新核验。深度 `L1`～`L4` 描述掌握证据，重要程度 `core`、`common`、`extension` 描述默认投入，两者均不等同于成熟度。版本变化见[变更记录](CHANGELOG.md)。

## 贡献方式

提交 Issue 或 Pull Request 前请阅读[贡献指南](CONTRIBUTING.md)。贡献应保持单一主题，补充权威来源，遵守 Properties 和文件命名规则，并通过仓库的本地检查。任何文件都不得包含 API Key、账号信息、客户数据、前雇主私有信息或其他未获授权公开的材料。

## 许可证

本仓库采用按材料类型区分的双许可证：

- 仓库贡献者原创的 Markdown 正文和图表适用 [Creative Commons Attribution 4.0 International](LICENSE-CONTENT)。
- 仓库贡献者原创的可执行代码片段和脚本适用 [MIT License](LICENSE-CODE)。
- 引用、截图、数据、商标及其他第三方内容仍遵循其原许可证或使用条款，不因收录在本仓库而重新授权；文件中的单独声明优先。
