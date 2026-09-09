---
type: decision
domain:
  - Production AI
  - Knowledge Management
depth: L2
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - Wiki 链接格式决策
tags:
  - documentation
  - architecture-decision
decision_status: accepted
---

# ADR-001：Wiki 链接格式

## 状态

`accepted`。该决策自 2026-09-09 起适用于仓库内全部导航和正文链接。

## 背景

AIFDE Wiki 使用 Obsidian 编辑，同时以 GitHub 公开阅读为最低体验基线。Obsidian 支持 `[[目标笔记]]` 形式的 Wiki Link，也支持标准 Markdown 链接；GitHub 对标准 Markdown 链接的目标和路径语义更直接，而 Obsidian 专用解析不能作为公开阅读的前提。

仓库还需要用脚本在不启动 Obsidian 的环境中检查相对路径是否存在。链接格式若分叉，会增加作者选择、迁移和校验规则的复杂度。

## 决策驱动因素

优先级从高到低为：

1. GitHub 访客无需 Obsidian 或插件即可打开内部导航。
2. 链接目标在代码评审中可见，并能由通用 Markdown 工具静态检查。
3. Obsidian 仍可创建、重命名和维护链接。
4. 对空格、括号、中文文件名和跨目录路径有统一写法。
5. 不维护两套等价链接或依赖 Dataview 生成核心导航。

## 候选方案

### 标准相对 Markdown 链接

示例：

```markdown
[词元化](../J-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM/01-%E8%AF%8D%E5%85%83%E5%8C%96%20Tokenization.md)
```

优点是 GitHub、Obsidian 和常见 Markdown 工具都能识别；目标路径可直接审查和校验。代价是文件名含空格或括号时需要 URL 编码，手写路径比 Wiki Link 稍长。

### Obsidian Wiki Link

示例：

```text
[[词元化 (Tokenization)]]
```

优点是输入简短，并可依赖 Obsidian 的笔记名补全。缺点是公开渲染和目标解析依赖宿主行为，路径在文本中不明确，也要求校验器理解 Obsidian 的别名、重名与嵌入语法。

### 两种格式并存

作者可按场景选择，但会产生不一致的评审与自动检查结果；批量迁移、重命名和贡献指南都需要覆盖两套规则。没有证据表明这份灵活性能抵消维护成本。

## 最终决策

选择**标准相对 Markdown 链接**。仓库内链接必须相对于当前文件书写，并在含空格或括号的目标中使用 URL 编码；外部链接同样使用标准 Markdown 语法。核心导航不得使用 Wiki Link。

Obsidian 的 `.obsidian/app.json` 设置 `"useMarkdownLinks": true`，使编辑器创建 Markdown 链接；`"newLinkFormat": "relative"` 使新链接使用相对路径；`"alwaysUpdateLinks": true` 允许重命名笔记时更新目标。配置只是作者体验增强，不能替代仓库校验。

## 正面影响

- GitHub 成为可验证的最低阅读基线，无需安装 Obsidian。
- Python 校验器可解析目标路径并报告失效链接。
- 链接差异在普通 Git diff 中清晰可见。
- MOC、路线和证据笔记共享一种导航约定。

## 负面影响

- 手写路径更长，中文、空格与括号需要正确编码。
- 移动文件会改变相对路径；虽然 Obsidian 可自动更新，外部编辑器中仍需人工或工具修订。
- 暂不使用 Wiki Link 的短语法、块引用和宿主特有解析能力。

## 验证方式

- `python3 scripts/validate_wiki.py .` 必须能解析所有仓库内标准 Markdown 链接且无失效目标。
- `npm run lint:md` 必须通过。
- 评审新增笔记时，从 GitHub 文件视图人工抽查至少一个上级 MOC 链接。
- `.obsidian/app.json` 中 `useMarkdownLinks` 必须为 `true`，`newLinkFormat` 必须为 `relative`。

## 复审条件

出现以下任一情况时重新评估：GitHub 原生支持并稳定解析本仓库所需的 Wiki Link；标准 Markdown 路径在批量重命名中造成持续且无法由工具控制的错误；或主要发布环境不再是 GitHub。复审前保持单一格式，不以局部例外提前形成第二套规范。

## 相关记录

- [生产 AI MOC](./00-%E7%94%9F%E4%BA%A7%E7%BA%A7%20AI-MOC.md)
- [使用指南](../E-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/00-%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97.md)
- [基础建设设计文档](../docs/superpowers/specs/2026-09-09-aifde-wiki-design.md)
