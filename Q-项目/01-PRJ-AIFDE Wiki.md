---
type: project
domain:
  - Projects
  - Knowledge Management
depth: L3
importance: core
maturity: draft
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - AIFDE Wiki 项目档案
tags:
  - projects
  - documentation
github:
demo:
phase: foundation
tech:
  - Markdown
  - Obsidian
  - Python
  - GitHub Actions
---

# AIFDE Wiki 项目档案

## 业务问题

AI 与前沿部署工程（Forward Deployed Engineering，FDE）的学习资料容易按工具堆积，难以回答“先学什么、做到什么深度、用什么证据证明”。本项目建立公开、可审查的知识地图，把概念、路线、实践、源码研究和面试证据连接起来。

## 目标用户

- 希望从软件工程走向 AI 应用与 FDE 交付的学习者。
- 需要以 GitHub 直接阅读、以 Obsidian 编辑的维护者。
- 希望用项目、评测、决策和复盘而非工具清单呈现能力的求职者。

## 成功指标

当前基础阶段只定义验收口径，不声明尚未测得的结果：

- 结构质量：全部 Wiki 笔记通过 Front Matter、枚举、命名和内部链接校验。
- 阅读质量：核心入口使用标准相对 Markdown 链接，在 GitHub 上无需插件即可导航。
- 内容覆盖：领域 MOC、七阶段路线和九类文档模板均有明确入口与用途。
- 公开安全：提交内容不含密钥、账号、客户数据和前雇主私有信息。
- 可维护性：Markdown lint 与 Python 校验能在本地和持续集成中重复执行。

首次公开发布后再记录校验运行、发布版本和读者反馈；不以计划值代替实测值。

## 约束与假设

- 中文为主，重要术语首次出现时附标准英文名称。
- Python 是实践主线，Vue 和 TypeScript 为辅助技术栈。
- 核心导航不得依赖 Dataview 或本地 Obsidian 状态。
- 实战代码属于独立仓库，本仓库只保存档案与证据链接。
- 原创文章与图表采用 CC BY 4.0，原创可执行代码片段采用 MIT License。

## 架构

仓库采用“稳定领域目录 + MOC 导航 + 适度原子化笔记”。`00-Guide` 提供总入口与能力模型，`01-Roadmap` 组织阶段，知识领域目录保存内容，`12-Projects` 至 `15-Job-Market` 保存证据；`Z-模板` 统一九类笔记结构。Python 校验器、markdownlint 与 GitHub Actions 形成质量门禁，Obsidian 只承担编辑增强。

## 关键决策

- 以 GitHub 阅读为最低体验基线，统一相对 Markdown 链接。
- 用固定类型、深度、重要程度和成熟度属性支持长期维护。
- 将个人进度、日记和待办排除在公开知识产品之外。
- 对岗位只做结构化摘要，对外部项目只记录可核验链接。

详细理由见[基础建设设计文档](../docs/superpowers/specs/2026-09-09-aifde-wiki-design.md)。

## 仓库与 Demo

远程地址将在首次公开发布时记录；在此之前 `github` 和 `demo` 保持为空，成熟度保持 `draft`。本档案不虚构远程 URL、Commit、Release 或演示入口。

## 评测

本地验收命令为 `.venv/bin/python scripts/validate_wiki.py .`、`.venv/bin/python -m pytest` 和 `npm run lint:md`。结果应由实际运行记录或持续集成链接证明；本页不预填通过率、覆盖率或性能数字。

## 安全与可靠性

忽略设备工作区、环境文件和依赖目录；校验器检查结构与链接，Markdown lint 检查文档格式。发布前仍需人工检查隐私、来源许可、岗位摘要范围和任何可能被误认为真实客户证据的模拟内容。

## 故障复盘

尚无公开发布后的故障记录。出现失效链接、错误引用、敏感信息暴露或质量门禁漏检时，另建复盘并链接影响、根因、修复和预防措施。

## 交付材料

- [使用指南](../E-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/00-%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97.md)
- [AI 全局知识地图](../E-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/01-AI%20%E7%9F%A5%E8%AF%86%E5%9C%B0%E5%9B%BE.md)
- [FDE 能力模型](../E-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/02-FDE%20%E8%83%BD%E5%8A%9B%E6%A8%A1%E5%9E%8B.md)
- [路线总览](../F-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/00-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF-MOC.md)
- [文档模板目录](../Z-模板/Template-MOC.md)

## 面试追问

- 为什么选择稳定目录与 MOC，而不是完全原子化或完全层级化？
- 如何证明 GitHub 与 Obsidian 两种阅读路径没有分叉？
- 哪些质量问题适合自动校验，哪些必须人工评审？
- 公开安全与可验证证据冲突时，如何决定披露边界？
