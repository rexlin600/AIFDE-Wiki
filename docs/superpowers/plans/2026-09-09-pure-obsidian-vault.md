# 纯 Obsidian 知识库精简实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 删除项目工程化工具与本地依赖，使仓库成为可直接在 Obsidian 中使用的纯知识库。

**Architecture:** 仅从版本库移除 CI、测试、校验脚本与开发依赖清单；仅从本地移除依赖和缓存目录。知识内容、Vault 配置、根目录说明、许可证及 `docs/superpowers/` 全部保留。

**Tech Stack:** Git、POSIX shell、Obsidian。

## Global Constraints

- 不修改任何知识库笔记的正文、标题、文件名或链接。
- 保留 `docs/superpowers/`。
- 不暂存或修改现有 `.obsidian` 与 `.claudian` 未提交内容。
- 保留 `.gitignore`，以避免未来本地缓存或依赖目录被意外提交。

---

### Task 1：删除已跟踪的工程化文件

**Files:**
- Delete: `.github/workflows/wiki-quality.yml`
- Delete: `tests/test_validate_wiki.py`
- Delete: `scripts/validate_wiki.py`
- Delete: `.editorconfig`
- Delete: `.markdownlint-cli2.jsonc`
- Delete: `package.json`
- Delete: `package-lock.json`
- Delete: `requirements-dev.txt`

**Interfaces:**
- Produces: 无 CI、测试、Node.js 或 Python 开发依赖声明的 Git 仓库。

- [ ] **Step 1: 用 Git 删除已跟踪文件**

```bash
git rm -r .github tests scripts
git rm .editorconfig .markdownlint-cli2.jsonc package.json package-lock.json requirements-dev.txt
```

Expected: `git status --short` 只显示上述路径为删除，且不包括 `.obsidian` 或 `.claudian`。

### Task 2：清除本地生成的依赖与缓存

**Files:**
- Delete locally: `node_modules/`、`.venv/`、`.pytest_cache/`。

**Interfaces:**
- Consumes: Task 1 完成后的纯内容仓库。
- Produces: 无本地包管理或 Python 测试缓存的 Vault 工作目录。

- [ ] **Step 1: 删除本地生成目录**

```bash
rm -rf node_modules .venv .pytest_cache
```

Expected: `find . -maxdepth 1 -name node_modules -o -name .venv -o -name .pytest_cache` 无输出。

### Task 3：验证范围并提交

**Files:**
- Verify: Vault 内容和保留文件。

**Interfaces:**
- Consumes: Tasks 1–2 的删除结果。
- Produces: 已提交的纯 Obsidian 知识库。

- [ ] **Step 1: 检查删除和保留范围**

```bash
test ! -e .github && test ! -e tests && test ! -e scripts
test ! -e node_modules && test ! -e .venv && test ! -e .pytest_cache
test -d .obsidian && test -d docs/superpowers
git diff --check
```

Expected: 全部命令以 exit code 0 结束。

- [ ] **Step 2: 仅暂存删除项并提交**

```bash
git add -u .github tests scripts .editorconfig .markdownlint-cli2.jsonc package.json package-lock.json requirements-dev.txt
git commit -m "chore: simplify repository into Obsidian vault"
```

Expected: 提交不包含 `.obsidian` 和 `.claudian` 的未提交内容。
