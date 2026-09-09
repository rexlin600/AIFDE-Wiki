# 知识库中文命名实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `00`–`15` 知识库目录及其中 Markdown 文件名中文化，并保持知识库内 Markdown 链接有效。

**Architecture:** 先以 Git 重命名保留历史，再只在知识库 Markdown 链接目标中替换路径组件。不会修改正文、标题、根目录文档、模板或资产目录。

**Tech Stack:** Git、Python 3 标准库、Markdown、现有 `scripts/validate_wiki.py`。

## Global Constraints

- 仅处理 `00`–`15` 目录与其 Markdown 文件。
- 保留目录编号及 AI、LLM、RAG、FDE、MOC、ADR、EXP、RETRO、PRJ 等缩写。
- 不修改 Markdown 标题与正文；链接显示文本保持原样。
- 不改根目录、`90-Templates`、`99-Assets` 或已有 `.obsidian` / `.claudian` 未提交文件。

## 文件结构与职责

| 路径 | 变更 |
|---|---|
| `00-用户指南/`～`15-就业市场/` | 取代原编号知识库目录。 |
| 其下 `*.md` | 使用中文优先文件名；仅更新 Markdown 链接目标。 |
| `scripts/validate_wiki.py` | 不修改；用于验证改名后的目录和链接。 |

---

### Task 1：执行目录与文件重命名

**Files:**
- Modify by rename: 所有 `00-Guide/`～`15-Job-Market/` 目录及其 35 个 Markdown 文件。

**Interfaces:**
- Produces: 下表所列的新路径，供 Task 2 替换链接目标。

| 原路径 | 新路径 |
|---|---|
| `00-Guide` | `00-用户指南` |
| `01-Roadmap` | `01-学习路线` |
| `02-AI-Foundations` | `02-AI 基础` |
| `03-Machine-Learning` | `03-机器学习` |
| `04-Deep-Learning` | `04-深度学习` |
| `05-LLM` | `05-大模型 LLM` |
| `06-RAG` | `06-检索增强生成 RAG` |
| `07-Agent` | `07-智能体 Agent` |
| `08-Multimodal-AI` | `08-多模态 AI` |
| `09-Production-AI` | `09-生产级 AI` |
| `10-AI-Safety-Governance` | `10-AI 安全与治理` |
| `11-FDE-Practice` | `11-FDE 实践` |
| `12-Projects` | `12-项目` |
| `13-Open-Source` | `13-开源` |
| `14-Interview` | `14-面试` |
| `15-Job-Market` | `15-就业市场` |
| `AI-Knowledge-Map.md` | `AI 知识地图.md` |
| `FDE-Competency-Model.md` | `FDE 能力模型.md` |
| `Glossary.md` | `术语表.md` |
| `How-To-Use.md` | `使用指南.md` |
| `Phase-0-Baseline.md` | `阶段 0-基础基线.md` |
| `Phase-1-AI-ML-Foundations.md` | `阶段 1-AI 与机器学习基础.md` |
| `Phase-2-LLM-Engineering.md` | `阶段 2-大模型 LLM 工程.md` |
| `Phase-3-RAG-Engineering.md` | `阶段 3-RAG 工程.md` |
| `Phase-4-Agent-Engineering.md` | `阶段 4-智能体 Agent 工程.md` |
| `Phase-5-Production-AI.md` | `阶段 5-生产级 AI.md` |
| `Phase-6-FDE-Capstone.md` | `阶段 6-FDE 综合项目.md` |
| `Roadmap-MOC.md` | `学习路线-MOC.md` |
| `AI-Foundations-MOC.md` | `AI 基础-MOC.md` |
| `Machine-Learning-MOC.md` | `机器学习-MOC.md` |
| `Deep-Learning-MOC.md` | `深度学习-MOC.md` |
| `LLM-MOC.md` | `大模型 LLM-MOC.md` |
| `词元化 (Tokenization).md` | `词元化 Tokenization.md` |
| `EXP-20260909-Retrieval-Baseline.md` | `EXP-20260909-检索基线.md` |
| `RAG-MOC.md` | `检索增强生成 RAG-MOC.md` |
| `混合检索 (Hybrid Search).md` | `混合检索 Hybrid Search.md` |
| `Agent-MOC.md` | `智能体 Agent-MOC.md` |
| `Multimodal-AI-MOC.md` | `多模态 AI-MOC.md` |
| `ADR-001-Wiki-Link-Format.md` | `ADR-001-Wiki 链接格式.md` |
| `Production-AI-MOC.md` | `生产级 AI-MOC.md` |
| `AI-Safety-Governance-MOC.md` | `AI 安全与治理-MOC.md` |
| `FDE-Practice-MOC.md` | `FDE 实践-MOC.md` |
| `RETRO-AIFDE-Wiki-Foundation.md` | `RETRO-AIFDE Wiki 基础建设.md` |
| `PRJ-AIFDE-Wiki.md` | `PRJ-AIFDE Wiki.md` |
| `Projects-MOC.md` | `项目-MOC.md` |
| `Open-Source-MOC.md` | `开源-MOC.md` |
| `Repo-LangGraph.md` | `开源项目-LangGraph.md` |
| `Interview-MOC.md` | `面试-MOC.md` |
| `如何评测一个RAG系统.md` | `如何评测 RAG 系统.md` |
| `Job-Market-MOC.md` | `就业市场-MOC.md` |
| `Job-OpenAI-FDE-Healthcare-20260909.md` | `招聘-OpenAI FDE 医疗健康-20260909.md` |

- [ ] **Step 1: 检查目标路径无冲突**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path('/Users/rexlin600/git_workspace/ai-repo/AIFDE-Wiki')
for path in root.glob('[0-1][0-9]-*'):
    print(path.name)
PY
```

Expected: 当前仅有英文或混合命名的 `00`–`15` 源目录，不存在表中的目标目录。

- [ ] **Step 2: 使用 `git mv` 重命名**

Run the `git mv` commands matching the table, first for each directory and then for every Markdown filename.

Expected: `git status --short` 将所有 35 个 Markdown 文件识别为 rename，且无新建或删除的知识库内容。

### Task 2：仅更新知识库内链接目标

**Files:**
- Modify: `00-用户指南/**/*.md` 至 `15-就业市场/**/*.md` 中含有指向已改名路径的 Markdown 链接。

**Interfaces:**
- Consumes: Task 1 的目录和文件映射。
- Produces: 可由 `validate_wiki.py` 解析的相对 Markdown 链接。

- [ ] **Step 1: 编写受限路径替换脚本**

Use a Python standard-library script that:
1. scans only `00`–`15` directories and `*.md` files;
2. matches Markdown link targets with `(?<!!)\[[^\]]+\]\(([^)]+)\)`;
3. skips `http://`、`https://`、`mailto:` targets;
4. URL-decodes the path segment, substitutes only mapped directory and filename components, then URL-encodes it with `/`, `#`, `?`, `&`, `=`, `+`, `,`, `-`, `.`, `_`, `~`, `:` as safe characters;
5. leaves all non-link text and link labels untouched.

- [ ] **Step 2: 运行替换并检查无旧路径**

Run:

```bash
grep -RInE '\]\((\.\./|[0-9][0-9]-)' 00-用户指南 01-学习路线 02-AI\ 基础 03-机器学习 04-深度学习 05-大模型\ LLM 06-检索增强生成\ RAG 07-智能体\ Agent 08-多模态\ AI 09-生产级\ AI 10-AI\ 安全与治理 11-FDE\ 实践 12-项目 13-开源 14-面试 15-就业市场
```

Expected: 改名后的链接目标存在；输出中不出现任何旧目录名或旧文件名。

### Task 3：验证并提交

**Files:**
- Verify: 已改名的知识库目录与文件。

**Interfaces:**
- Consumes: Tasks 1–2 的重命名和链接更新。
- Produces: 通过项目既有质量校验的中文命名知识库。

- [ ] **Step 1: 运行 Wiki 校验器**

Run:

```bash
python3 scripts/validate_wiki.py /Users/rexlin600/git_workspace/ai-repo/AIFDE-Wiki
```

Expected: `Wiki validation passed`。

- [ ] **Step 2: 运行 Markdown lint**

Run:

```bash
npm run lint:md
```

Expected: exit code 0。

- [ ] **Step 3: 审核变更范围并提交**

Run:

```bash
git diff --check
git status --short
git add 00-* 01-* 02-* 03-* 04-* 05-* 06-* 07-* 08-* 09-* 10-* 11-* 12-* 13-* 14-* 15-* docs/superpowers/plans/2026-09-09-knowledge-base-chinese-naming.md
git commit -m "docs: localize knowledge-base names to Chinese"
```

Expected: 仅知识库重命名、其中链接目标更新与本计划文件被提交；原有 `.obsidian` 和 `.claudian` 变动不被暂存。
