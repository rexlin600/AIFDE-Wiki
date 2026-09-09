---
type: moc
domain:
  - Guide
depth: L1
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - Wiki 使用指南
tags:
  - core
---

# 如何使用 AIFDE Wiki

## 目标读者与定位

AIFDE Wiki 面向已有后端或全栈研发经验、希望转向 AI 应用工程和前沿部署工程（Forward Deployed Engineering，FDE）的工程师，也服务于需要维护公开技术知识的贡献者。

本仓库是一个公开知识产品，而不是个人学习打卡或任务管理系统。它以 GitHub 可直接阅读的 Markdown 为最低体验基线，用 Obsidian 增强本地编辑；内容应帮助读者建立知识依赖、产出可验证证据，并能在项目、交付和面试中解释取舍。

## 从哪里开始

按目标选择入口：

- 想了解全貌：从 AI 全局知识地图开始，再进入路线总览。
- 想补齐某一领域：进入该领域的 MOC（Map of Content，内容地图），按推荐顺序学习。
- 想转向 FDE：先阅读 FDE 能力模型，找出证据缺口，再选择路线阶段和项目。
- 想解决具体问题：搜索术语、概念、模式、实验或面试问题；不要按文件数量衡量进度。

AI 全局知识地图、路线总览、各领域 MOC 和项目入口会在后续建设任务中逐步创建；在文件存在前，本页不创建占位链接。

## 目录规则

| 目录 | 内容边界 |
| --- | --- |
| `00-Guide` | 使用方法、全局知识地图、能力模型和术语表。 |
| `01-Roadmap` | 阶段路线、进入条件、退出标准和跨阶段实践要求。 |
| `02-AI-Foundations`～`11-FDE-Practice` | 稳定领域目录；每个目录由一个领域 MOC 组织权威笔记。 |
| `12-Projects` | 外部实战仓库的项目档案与交付证据，不存放完整项目代码。 |
| `13-Open-Source` | 开源项目使用、源码调用链、最小复刻和贡献记录。 |
| `14-Interview` | 按能力组织的问题、回答结构、追问和项目证据。 |
| `15-Job-Market` | 岗位样本和趋势摘要；不复制招聘全文。 |
| `90-Templates` | 九类文档的标准模板。 |
| `99-Assets` | 允许公开发布且已记录来源或许可的附件。 |

新增内容前先搜索：一个概念只保留一篇权威笔记，跨领域内容通过标准 Markdown 链接复用。只有当现有 MOC 已难以浏览、且细分领域拥有足够稳定内容时，才新增子目录。

## 九类文档

| 类型 | 何时使用 | 最低完成证据 |
| --- | --- | --- |
| `moc` | 划定领域边界、表达依赖和推荐顺序。 | 清晰的主题层次、实践入口和相邻领域。 |
| `concept` | 解释一个可独立引用的原理、算法或模型。 | 准确定义、机制、边界、示例和权威来源。 |
| `pattern` | 总结可重复使用的工程方案。 | 上下文、数据流、代价、失败模式和替代方案。 |
| `experiment` | 验证一个可证伪的技术假设。 | 环境、变量、指标、原始结果和复现信息。 |
| `project` | 索引独立 GitHub 项目及其交付价值。 | 代码版本、架构、评测、运行说明和复盘链接。 |
| `source` | 分析论文、官方文档、仓库或岗位样本。 | 原始链接、访问日期、关键结论与适用边界。 |
| `interview` | 训练问题拆解和证据化表达。 | 回答结构、常见错误、追问和项目证据。 |
| `decision` | 记录重要技术选择及后果。 | 候选方案、驱动因素、结论、验证和复审条件。 |
| `retrospective` | 复盘项目、实验集合或内容修订。 | 目标与结果差异、根因、数据和有责任人的改进。 |

创建笔记时复制对应模板：[MOC](../90-Templates/Template-MOC.md)、[Concept](../90-Templates/Template-Concept.md)、[Pattern](../90-Templates/Template-Pattern.md)、[Experiment](../90-Templates/Template-Experiment.md)、[Project](../90-Templates/Template-Project.md)、[Source](../90-Templates/Template-Source.md)、[Interview](../90-Templates/Template-Interview.md)、[Decision](../90-Templates/Template-Decision.md) 或 [Retrospective](../90-Templates/Template-Retrospective.md)。提交前须将模板变量替换为真实值，并删除无意义的空属性。

## 深度与重要程度

深度描述可证明的掌握程度，不是文章难度：

| 深度 | 达成标准 |
| --- | --- |
| `L1` 认知 | 能解释原理、用途、局限及与相邻技术的关系。 |
| `L2` 实验 | 能复现最小实验，解释关键参数并记录结果。 |
| `L3` 工程 | 能集成到有测试的项目中，以指标解释设计取舍。 |
| `L4` 生产/FDE | 能在业务约束下部署、评测、监控、保护、治理、交接并答辩。 |

重要程度决定默认投入：

- `core`：主线能力，建议达到 L3 或 L4。
- `common`：高频工程能力，建议达到 L2 或 L3。
- `extension`：拓展视野，默认达到 L1，实际项目需要时再深入。

一篇标记为 `depth: L3` 的笔记应包含或指向 L3 证据；仅列定义和链接不能宣称已达到 L3。

## 内容成熟度

- `draft`：已有可读内容，尚未完成来源、链接或技术复核。
- `reviewed`：主要来源已核对，结构和结论内部一致。
- `stable`：拥有可复现证据，适合作为长期参考。
- `needs-update`：已知时效性、依赖版本或正确性需要重新核验。

成熟度不等于深度。一篇 L1 术语说明可以是 `stable`，一篇完整但尚未复现的 L4 设计仍应是 `draft` 或 `reviewed`。修改技术结论时同步更新 `updated`；核验易变来源时同步更新 `last_verified`。

## 链接与附件

仓库内一律使用相对 Markdown 链接，例如：

```markdown
[Concept 模板](../90-Templates/Template-Concept.md)
```

文件名包含空格或括号时，应使用编辑器生成的百分号编码目标。不要使用 `[[Wiki Link]]`，不要创建尚不存在的目标，也不要把标签当成核心导航。外部资料使用完整 HTTPS 链接，并优先选择论文、官方文档、官方仓库和招聘原文。

图片和附件放入 `99-Assets`，使用可辨识的文件名，并记录原创、许可或来源。严禁提交 API Key、账号、客户数据、前雇主私有信息或无法公开授权的材料。

## Obsidian 推荐设置

仓库已约定以下设置，克隆后应保持一致：

- 新链接格式为相对路径，并使用标准 Markdown 链接。
- 重命名文件时自动更新内部链接。
- 附件目录为 `99-Assets`，模板目录为 `90-Templates`。
- Dataview 只能提供辅助查询，关键导航必须在 GitHub 上可直接使用。
- 设备相关工作区文件、缓存和插件本体不进入版本控制。

这些选项对应 Obsidian 官方说明中的[文件与链接设置](https://help.obsidian.md/settings#Files%20and%20links)和[模板核心插件](https://help.obsidian.md/plugins/templates)。

## 关联外部 GitHub 项目

实战代码保存在独立 GitHub 仓库，本 Wiki 只创建 `project` 档案并连接证据。项目档案至少记录：

1. 业务问题、用户和可量化验收标准；
2. 外部仓库与可复现的 Commit、Tag 或 Release；
3. 架构、接口、数据边界和关键决策；
4. 测试、评测、成本、延迟、安全与可靠性结果；
5. 演示、运行手册、故障记录和复盘；
6. 与路线阶段、概念笔记和面试问题的关系。

远程仓库尚未公开时，不填写虚假 URL；将项目档案保持为 `draft`，正文写明缺少的证据。公开项目时遵循 [GitHub 关于仓库可见性的说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)，先检查历史提交和制品中是否包含敏感信息。

## 报告错误与贡献修订

发现错误时，优先在仓库的 Issues 中报告；若 Issues 未启用，可提交 Pull Request。报告应包含文件路径、问题段落、预期结论、复现步骤或反例、权威来源，以及发现日期。安全或隐私问题不要在公开 Issue 中粘贴秘密或客户数据，应只描述影响和安全的复现范围。

修订内容时保持改动聚焦，更新 Front Matter 日期，检查所有内部链接，并在本地运行：

```bash
.venv/bin/python scripts/validate_wiki.py .
npm run lint:md
```

## 资料来源

- [Obsidian Help：Settings](https://help.obsidian.md/settings)，访问日期：2026-09-09。
- [GitHub Docs：About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)，访问日期：2026-09-09。
- [GitHub Docs：About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)，访问日期：2026-09-09。
