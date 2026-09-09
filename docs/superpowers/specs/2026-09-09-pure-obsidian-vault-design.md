# 纯 Obsidian 知识库精简设计

## 目标

将仓库精简为无需 Node.js、Python 或 CI 工具链即可使用的 Obsidian 知识库，同时保留知识内容、Vault 配置、根目录说明与既有 `docs/superpowers/` 过程记录。

## 保留内容

- 编号知识库目录、`90-Templates`、`99-Assets`。
- `README.md`、`CHANGELOG.md`、`CONTRIBUTING.md`、许可证与 `.gitignore`。
- `.obsidian/` 配置及 `docs/superpowers/` 设计和计划文档。

## 删除内容

- 已跟踪的工程化文件：`.github/`、`tests/`、`scripts/`、`package.json`、`package-lock.json`、`requirements-dev.txt`、`.markdownlint-cli2.jsonc`、`.editorconfig`。
- 本地生成的依赖和缓存：`node_modules/`、`.venv/`、`.pytest_cache/`。

## 约束与验证

- 不修改任何知识库笔记的正文、标题、文件名或链接。
- 不触碰当前未提交的 `.obsidian` 和 `.claudian` 内容。
- 删除后使用 `git diff --check` 与目录清单确认：上述工程化路径不存在，保留内容仍在。
