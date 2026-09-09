# 字母目录与笔记排序实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用 A–P 排序知识库一级目录，并以两位数字排序其内部笔记。

**Architecture:** 目录从数字前缀改为字母前缀，笔记从语义名改为数字前缀加原名。重命名后仅变换知识库 Markdown 链接的目标路径，保持正文、标题和链接标签不变。

**Tech Stack:** Git、Python 3 标准库、Markdown。

## Global Constraints

- 只改 A–P 对应的知识库目录和其中 Markdown 文件。
- 仅更新这些笔记中的相对 Markdown 链接目标。
- 不修改根目录、`90-Templates`、`99-Assets`、`docs/superpowers/`、`.gitignore` 或 `.obsidian`。
- 保留 AI、LLM、RAG、FDE、MOC、ADR、EXP、RETRO、PRJ 缩写。

---

### Task 1：执行目录和笔记排序重命名

**Files:**
- Rename: `00-用户指南/`–`15-就业市场/` 及其中 35 个 Markdown 文件。

**Interfaces:**
- Produces: A–P 目录，以及以下完整的目录内排序名称。

```text
A-用户指南: 00-使用指南.md, 01-AI 知识地图.md, 02-FDE 能力模型.md, 03-术语表.md
B-学习路线: 00-学习路线-MOC.md, 01-阶段 0-基础基线.md, 02-阶段 1-AI 与机器学习基础.md, 03-阶段 2-大模型 LLM 工程.md, 04-阶段 3-RAG 工程.md, 05-阶段 4-智能体 Agent 工程.md, 06-阶段 5-生产级 AI.md, 07-阶段 6-FDE 综合项目.md
C-AI 基础: 00-AI 基础-MOC.md
D-机器学习: 00-机器学习-MOC.md
E-深度学习: 00-深度学习-MOC.md
F-大模型 LLM: 00-大模型 LLM-MOC.md, 01-词元化 Tokenization.md
G-检索增强生成 RAG: 00-检索增强生成 RAG-MOC.md, 01-EXP-20260909-检索基线.md, 02-混合检索 Hybrid Search.md
H-智能体 Agent: 00-智能体 Agent-MOC.md
I-多模态 AI: 00-多模态 AI-MOC.md
J-生产级 AI: 00-生产级 AI-MOC.md, 01-ADR-001-Wiki 链接格式.md
K-AI 安全与治理: 00-AI 安全与治理-MOC.md
L-FDE 实践: 00-FDE 实践-MOC.md, 01-RETRO-AIFDE Wiki 基础建设.md
M-项目: 00-项目-MOC.md, 01-PRJ-AIFDE Wiki.md
N-开源: 00-开源-MOC.md, 01-开源项目-LangGraph.md
O-面试: 00-面试-MOC.md, 01-如何评测 RAG 系统.md
P-就业市场: 00-就业市场-MOC.md, 01-招聘-OpenAI FDE 医疗健康-20260909.md
```

- [ ] **Step 1: 检查所有目标路径无冲突**

Run a Python script that stores the exact directory and file mapping above, asserts each source exists, and asserts each destination does not exist.

Expected: 16 source directories and 35 source files exist; all 51 destination paths are absent.

- [ ] **Step 2: 重命名目录和文件**

Use `git mv` for the 16 directories in order `00-用户指南` → `A-用户指南` through `15-就业市场` → `P-就业市场`; then use `Path.rename()` for the mapped filenames within the new directories.

Expected: Filesystem displays only A–P directories, and every Markdown filename begins with a two-digit prefix.

### Task 2：更新知识库内部链接

**Files:**
- Modify: A–P directory Markdown files whose relative Markdown link targets include a renamed directory or filename.

**Interfaces:**
- Consumes: Task 1 mapping.
- Produces: Valid URL-encoded relative Markdown links to A–P paths.

- [ ] **Step 1: 用受限替换更新链接目标**

Use a Python standard-library script that scans only `A-*` through `P-*` directories and matches `(?<!!)\[[^\]]+\]\(([^)]+)\)`. For non-HTTP/non-email targets, URL-decode the path portion, replace only mapped directory and filename components, URL-encode the rewritten path, and preserve labels and fragments.

Expected: No prose, headings or link display labels change.

### Task 3：验证并提交

**Files:**
- Verify: A–P knowledge-base directories and their Markdown files.

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: Stable Obsidian alphabetical ordering with valid knowledge-base links.

- [ ] **Step 1: 验证顺序与链接**

Run a Python script that verifies every A–P directory exists, every Markdown filename matches `^\d{2}-`, and every relative Markdown link in those directories resolves to an existing path.

Expected: exit code 0 with `Knowledge-base ordering validation passed`.

- [ ] **Step 2: 检查并提交范围**

```bash
git diff --check
git add -A -- A-* B-* C-* D-* E-* F-* G-* H-* I-* J-* K-* L-* M-* N-* O-* P-*
git commit -m "docs: order knowledge base with letters and prefixes"
```

Expected: 提交仅包括知识库目录与笔记重命名、内部链接目标更新；不会包含 `.gitignore` 或 `.obsidian`。
