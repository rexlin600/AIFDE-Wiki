# 贡献指南

感谢你帮助改进 AIFDE Wiki。仓库首先是可在 GitHub 直接阅读的公开知识产品；贡献应提升内容的准确性、可验证性和可导航性，不加入个人 Dashboard、日记、私人待办或学习完成率。

## 环境准备

需要 Python 3.12、Node.js 和 npm。建议在虚拟环境中安装固定版本依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci
```

## 文件命名

- 普通知识笔记使用稳定、可读的主题名；不得包含 `\\`、`:`、`#` 或 `?`。
- 概念文件可使用中文名称，并在首次出现时给出标准英文名称。
- 实验使用 `EXP-YYYYMMDD-Topic.md`，项目使用 `PRJ-Topic.md`，决策使用 `ADR-NNN-Topic.md`，复盘使用 `RETRO-Topic.md`。
- 一个概念只保留一篇权威笔记；跨目录关系用相对 Markdown 链接表达。
- 图片和附件放在 `99-Assets`，使用描述性名称，并记录原创、许可或来源。

## Properties 枚举

知识笔记必须包含 YAML Front Matter，并使用以下固定枚举：

| 属性 | 允许值或格式 |
| --- | --- |
| `type` | `moc`、`concept`、`pattern`、`experiment`、`project`、`source`、`interview`、`decision`、`retrospective` |
| `domain` | 非空列表 |
| `depth` | `L1`、`L2`、`L3`、`L4` |
| `importance` | `core`、`common`、`extension` |
| `maturity` | `draft`、`reviewed`、`stable`、`needs-update` |
| `created`、`updated` | `YYYY-MM-DD` |
| `last_verified` | 建议用于容易变化或依赖外部来源的内容，格式为 `YYYY-MM-DD` |

修改正文结论时同步更新 `updated`；重新核验易变来源时同步更新 `last_verified`。不要用更高深度或成熟度代替尚不存在的证据。

## 九类模板

从对应模板开始创建内容：[MOC](90-Templates/Template-MOC.md)、[Concept](90-Templates/Template-Concept.md)、[Pattern](90-Templates/Template-Pattern.md)、[Experiment](90-Templates/Template-Experiment.md)、[Project](90-Templates/Template-Project.md)、[Source](90-Templates/Template-Source.md)、[Interview](90-Templates/Template-Interview.md)、[Decision](90-Templates/Template-Decision.md)和[Retrospective](90-Templates/Template-Retrospective.md)。提交前替换全部模板变量，并删除无意义的空字段和占位段落。

## 来源优先级

按以下顺序选择能够直接支持结论的来源：

1. 标准、论文、官方文档、官方仓库和正式发布说明。
2. 作者或维护者的技术说明，以及可验证的一手演讲材料。
3. 可信工程团队的实践文章和可复现实验。
4. 社区讨论和聚合内容，仅用于发现线索或补充观点，不作为关键结论的唯一依据。

记录来源标题、原始 HTTPS 链接、访问日期和适用版本。优先总结和连接证据，不大段复制原文；技术结论应区分事实、实验结果与作者判断。

## 招聘摘要版权规则

岗位内容只记录职位、公司、地点、时间、职责与技能的结构化摘要、分析结论和招聘原文链接，不复制岗位全文。保留访问日期；页面失效时只更新状态，不把缓存全文或截图补进仓库。公司名称、商标和招聘原文仍归其权利人所有。

## 开源许可证检查

分析或复刻开源项目之前，先确认仓库根许可证、相关文件头、依赖许可证和目标版本。`source` 或项目档案须链接原仓库并记录版本与许可证；不要将第三方代码改写后当作本仓库原创内容。引入任何片段时保留其版权与许可证通知，并确认许可证兼容性；无法确认授权范围时只写结构化分析和链接。

## 公开安全检查

提交前检查当前差异和历史来源，确保不含 API Key、Token、账号、内部地址、客户数据、前雇主私有信息、个人敏感信息或未获授权的附件。示例一律使用明显的虚构值。发现安全问题时不要在公开 Issue 粘贴秘密或原始数据，只描述影响和安全的复现范围，并先撤销或轮换已暴露的凭据。

## 本地测试

在仓库根目录依次运行：

```bash
python3 -m pytest -q
python3 scripts/validate_wiki.py .
npm run lint:md
```

全部命令通过后再提交 Pull Request。新增或重命名文件时，还要在 GitHub 预览中逐一检查相对 Markdown 链接。

## 分支与 Pull Request

- 从最新主分支创建短生命周期、单一主题分支。
- 一个 Pull Request 只解决一个明确问题，说明动机、范围、证据和本地检查结果。
- 不夹带无关格式化、设备专属 Obsidian 文件或私人工作区状态。
- 回应评审时优先补充证据；改变技术结论后同步更新日期、来源和相关链接。
- 合并前保持提交历史可读，并确认所有自动检查通过。

## Commit 示例

提交信息遵循 Conventional Commits，使用简洁的中文或英文摘要，例如：

```text
docs: 补充混合检索评测方法
fix: 修复 RAG MOC 的失效链接
test: 增加非法 Properties 回归用例
```

## 许可证与贡献授权

提交贡献即表示你有权提供相关材料，并同意按材料类型授权：原创 Markdown 正文和图表适用 [CC BY 4.0](LICENSE-CONTENT)，原创可执行代码片段和脚本适用 [MIT License](LICENSE-CODE)。引用、数据、截图、商标及其他第三方内容仍遵循其原许可证或使用条款；应清楚标注来源与适用许可证，文件中的单独声明优先。
