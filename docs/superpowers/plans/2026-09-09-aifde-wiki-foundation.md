# AIFDE Wiki 基础建设实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建成一个以 Obsidian 编辑、以公开 GitHub 阅读为优先，覆盖 AI/FDE 知识地图、阶段路线、开源实践、项目档案和面试准备的 Wiki 基础版本。

**Architecture:** 仓库采用“稳定领域目录 + MOC 导航 + 适度原子化笔记”的混合结构。所有关键导航使用相对 Markdown 链接；Obsidian 只提供编辑增强，Python 校验器和 GitHub Actions 负责 Properties、链接、格式与敏感信息检查。

**Tech Stack:** Markdown、YAML Front Matter、Obsidian、Python 3.12、PyYAML 6.0.3、pytest 9.1.1、Node.js、markdownlint-cli2 0.23.2、GitHub Actions

## Global Constraints

- 正文以中文为主，重要术语首次出现时给出标准英文名称。
- 实践技术栈以 Python 为主，以 Vue 和 TypeScript 为辅。
- GitHub 直接阅读是最低体验基线，核心导航不得依赖 Dataview。
- 仓库内链接统一使用相对 Markdown 链接，不使用 Obsidian Wiki Link。
- 不建设个人 Dashboard、日记、私人待办或个人学习完成率。
- 文档类型固定为 `moc`、`concept`、`pattern`、`experiment`、`project`、`source`、`interview`、`decision`、`retrospective`。
- 内容深度固定为 `L1`、`L2`、`L3`、`L4`；重要程度固定为 `core`、`common`、`extension`。
- 内容成熟度固定为 `draft`、`reviewed`、`stable`、`needs-update`。
- 原创文章和图表使用 CC BY 4.0；原创可执行代码片段使用 MIT License。
- 招聘内容只做结构化摘要和链接，不复制岗位全文。
- 实战代码存放在独立 GitHub 仓库，本仓库只保存项目档案及证据链接。
- 任何文件都不得包含 API Key、账号信息、客户数据或前雇主私有信息。

## 文件结构与职责

| 路径 | 职责 |
|---|---|
| `README.md` | GitHub 顶层入口及稳定导航。 |
| `00-Guide/` | 使用指南、全局知识地图、FDE 能力模型和术语表。 |
| `01-Roadmap/` | 七个阶段及横向开源、面试轨道。 |
| `02-AI-Foundations/`～`11-FDE-Practice/` | 各知识领域的权威笔记和 MOC。 |
| `12-Projects/` | 外部实战仓库的项目档案。 |
| `13-Open-Source/` | 开源仓库研究、源码调用链及复刻记录。 |
| `14-Interview/` | 面试能力地图和题目笔记。 |
| `15-Job-Market/` | 岗位样本、能力统计及季度观察。 |
| `90-Templates/` | 九种文档模板。 |
| `99-Assets/` | 图片和附件。 |
| `scripts/validate_wiki.py` | 校验 Front Matter、枚举值、内部链接和文件命名。 |
| `tests/test_validate_wiki.py` | 校验器回归测试。 |
| `.github/workflows/wiki-quality.yml` | 在 Pull Request 和 push 上执行质量检查。 |

---

### Task 1：建立公开仓库基础与忽略规则

**Files:**
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `requirements-dev.txt`
- Create: `package.json`
- Create: `package-lock.json`
- Create: `.markdownlint-cli2.jsonc`
- Create: `CHANGELOG.md`
- Create: `99-Assets/README.md`

**Interfaces:**
- Produces: 后续所有任务共用的忽略规则、编辑格式、开发依赖和检查命令。

- [ ] **Step 1: 写入仓库忽略规则**

创建 `.gitignore`：

```gitignore
.DS_Store
.env
.env.*
!.env.example
.venv/
node_modules/
.pytest_cache/
__pycache__/
*.py[cod]
.trash/
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache/
.obsidian/plugins/
```

- [ ] **Step 2: 写入统一编辑格式**

创建 `.editorconfig`：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
max_line_length = off

[*.{json,yml,yaml,py}]
indent_style = space
indent_size = 2

[*.py]
indent_size = 4
```

- [ ] **Step 3: 固定本地质量工具版本**

创建 `requirements-dev.txt`：

```text
PyYAML==6.0.3
pytest==9.1.1
```

创建 `package.json`：

```json
{
  "name": "aifde-wiki",
  "private": true,
  "scripts": {
    "lint:md": "markdownlint-cli2 \"**/*.md\" \"#node_modules\""
  },
  "devDependencies": {
    "markdownlint-cli2": "0.23.2"
  }
}
```

创建 `.markdownlint-cli2.jsonc`：

```jsonc
{
  "config": {
    "MD013": false,
    "MD024": { "siblings_only": true },
    "MD033": false,
    "MD041": false
  },
  "ignores": [
    "node_modules/**"
  ]
}
```

生成锁文件：

```bash
npm install --package-lock-only
```

Expected: 创建 `package-lock.json`，其中锁定 `markdownlint-cli2@0.23.2`。

- [ ] **Step 4: 建立变更记录**

创建 `CHANGELOG.md`，首个条目为 `2026-09-09`，记录：建立混合 MOC 架构、公开知识产品定位、九类笔记模型、L1～L4 深度标准，以及 Python 主导的实践路线。

创建 `99-Assets/README.md`，说明该目录只存放允许公开发布的图片和附件，文件必须使用描述性名称，并记录原创、许可或来源信息。

- [ ] **Step 5: 验证忽略和配置文件**

Run:

```bash
git check-ignore .obsidian/workspace.json .env node_modules/example
python3 -m json.tool package.json >/dev/null
npm ci
```

Expected: 三个路径均由 `git check-ignore` 输出，JSON 检查退出码为 0，Node 依赖按锁文件安装成功。

- [ ] **Step 6: 提交基础配置**

```bash
git add .gitignore .editorconfig requirements-dev.txt package.json package-lock.json .markdownlint-cli2.jsonc CHANGELOG.md 99-Assets/README.md
git commit -m "chore: establish wiki repository tooling"
```

### Task 2：配置 Obsidian 为 GitHub 兼容编辑器

**Files:**
- Modify: `.obsidian/app.json`
- Modify: `.obsidian/core-plugins.json`
- Create: `.obsidian/templates.json`
- Create: `.obsidian/community-plugins.json`

**Interfaces:**
- Consumes: Task 1 的 `.gitignore`。
- Produces: Markdown 相对链接、统一附件目录、模板目录和推荐插件列表。

- [ ] **Step 1: 配置 Markdown 链接和附件目录**

将 `.obsidian/app.json` 改为：

```json
{
  "newLinkFormat": "relative",
  "useMarkdownLinks": true,
  "alwaysUpdateLinks": true,
  "attachmentFolderPath": "99-Assets",
  "showUnsupportedFiles": true
}
```

- [ ] **Step 2: 精简核心插件**

将 `.obsidian/core-plugins.json` 改为：

```json
{
  "file-explorer": true,
  "global-search": true,
  "switcher": true,
  "graph": true,
  "backlink": true,
  "canvas": true,
  "outgoing-link": true,
  "tag-pane": true,
  "footnotes": true,
  "properties": true,
  "page-preview": true,
  "daily-notes": false,
  "templates": true,
  "note-composer": true,
  "command-palette": true,
  "slash-command": false,
  "editor-status": true,
  "bookmarks": true,
  "markdown-importer": false,
  "zk-prefixer": false,
  "random-note": false,
  "outline": true,
  "word-count": true,
  "slides": false,
  "audio-recorder": false,
  "workspaces": false,
  "file-recovery": true,
  "publish": false,
  "sync": false,
  "bases": true,
  "webviewer": false
}
```

不得提交设备相关 `workspace.json`。

- [ ] **Step 3: 配置模板和社区插件清单**

创建 `.obsidian/templates.json`：

```json
{
  "folder": "90-Templates"
}
```

创建 `.obsidian/community-plugins.json`：

```json
[
  "templater-obsidian",
  "obsidian-linter",
  "dataview",
  "obsidian-git"
]
```

插件本体仍由 `.gitignore` 排除；Dataview 和 Obsidian Git 均为可选能力。

- [ ] **Step 4: 验证 Obsidian 配置**

Run:

```bash
for file in .obsidian/app.json .obsidian/core-plugins.json .obsidian/templates.json .obsidian/community-plugins.json; do python3 -m json.tool "$file" >/dev/null; done
git check-ignore .obsidian/workspace.json
```

Expected: 所有 JSON 解析成功，`workspace.json` 被忽略。

- [ ] **Step 5: 提交 Obsidian 配置**

```bash
git add .obsidian/app.json .obsidian/core-plugins.json .obsidian/templates.json .obsidian/community-plugins.json
git commit -m "chore(obsidian): configure public wiki authoring"
```

### Task 3：以测试驱动方式实现 Wiki 校验器

**Files:**
- Create: `scripts/validate_wiki.py`
- Create: `tests/test_validate_wiki.py`

**Interfaces:**
- Consumes: Markdown 文件和 YAML Front Matter。
- Produces: `validate(root: Path) -> list[str]`；命令退出码 0 表示通过，1 表示存在问题。

- [ ] **Step 1: 编写失败测试**

测试必须覆盖：合法笔记、缺少属性、非法枚举、非法文件名、失效相对链接，以及忽略 `README.md`、`90-Templates/`、`docs/superpowers/` 的行为。

```python
from pathlib import Path

from scripts.validate_wiki import validate


VALID = """---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
---
# 混合检索
"""


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_valid_note_passes(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID)
    assert validate(tmp_path) == []


def test_missing_property_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID.replace("depth: L3\n", ""))
    assert any("depth" in error for error in validate(tmp_path))


def test_invalid_enum_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID.replace("importance: core", "importance: rare"))
    assert any("importance" in error for error in validate(tmp_path))


def test_invalid_filename_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/坏#文件.md", VALID)
    assert any("文件名" in error for error in validate(tmp_path))


def test_broken_relative_link_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID + "\n[缺失](./missing.md)\n")
    assert any("失效链接" in error for error in validate(tmp_path))


def test_public_meta_files_and_templates_are_ignored(tmp_path: Path) -> None:
    write(tmp_path, "README.md", "# Home\n")
    write(tmp_path, "90-Templates/Template-Concept.md", "# Template\n")
    write(tmp_path, "docs/superpowers/specs/design.md", "# Design\n")
    assert validate(tmp_path) == []
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python3 -m pytest tests/test_validate_wiki.py -q`

Expected: FAIL，原因为 `scripts.validate_wiki` 尚不存在。

- [ ] **Step 3: 实现最小校验器**

实现要求：

- 使用 `yaml.safe_load` 解析 Front Matter；
- 校验九种 `type`、四种 `depth`、三种 `importance` 和四种 `maturity`；
- 校验公共字段 `type`、`domain`、`depth`、`importance`、`maturity`、`created`、`updated`；
- 扫描标准 Markdown 相对链接，忽略 `http`、`https`、`mailto` 和页内锚点；
- 对 URL 解码后检查目标文件是否存在；
- 跳过根目录元文件、`90-Templates/`、`99-Assets/`、`docs/superpowers/`、`.github/` 和隐藏目录；
- 打印每个错误，成功时打印 `Wiki validation passed`。

主接口必须保持：

```python
def validate(root: Path) -> list[str]:
    """返回仓库内全部 Wiki 结构错误；无错误时返回空列表。"""
```

`scripts/validate_wiki.py` 的完整实现为：

```python
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


TYPES = {
    "moc",
    "concept",
    "pattern",
    "experiment",
    "project",
    "source",
    "interview",
    "decision",
    "retrospective",
}
DEPTHS = {"L1", "L2", "L3", "L4"}
IMPORTANCE = {"core", "common", "extension"}
MATURITY = {"draft", "reviewed", "stable", "needs-update"}
REQUIRED = {"type", "domain", "depth", "importance", "maturity", "created", "updated"}
SKIP_DIRS = {".git", ".github", ".obsidian", "90-Templates", "99-Assets", "docs"}
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
INVALID_NAME = re.compile(r"[\\:#?]")


def wiki_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if len(relative.parts) == 1:
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in relative.parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def load_properties(path: Path) -> tuple[dict[str, object] | None, str | None]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        return None, "缺少 YAML Front Matter"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, f"YAML 无法解析: {exc}"
    if not isinstance(data, dict):
        return None, "YAML Front Matter 必须是对象"
    return data, None


def validate_properties(path: Path, properties: dict[str, object]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - properties.keys())
    if missing:
        errors.append(f"{path}: 缺少属性 {', '.join(missing)}")
    if properties.get("type") not in TYPES:
        errors.append(f"{path}: type 非法")
    if properties.get("depth") not in DEPTHS:
        errors.append(f"{path}: depth 非法")
    if properties.get("importance") not in IMPORTANCE:
        errors.append(f"{path}: importance 非法")
    if properties.get("maturity") not in MATURITY:
        errors.append(f"{path}: maturity 非法")
    domain = properties.get("domain")
    if not isinstance(domain, list) or not domain:
        errors.append(f"{path}: domain 必须是非空列表")
    return errors


def validate_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        decoded = unquote(target)
        resolved = (path.parent / decoded).resolve()
        if not resolved.exists():
            errors.append(f"{path}: 失效链接 {raw_target}")
    return errors


def validate(root: Path) -> list[str]:
    """返回仓库内全部 Wiki 结构错误；无错误时返回空列表。"""
    errors: list[str] = []
    for path in wiki_files(root):
        if INVALID_NAME.search(path.name):
            errors.append(f"{path}: 文件名包含非法字符")
        properties, parse_error = load_properties(path)
        if parse_error:
            errors.append(f"{path}: {parse_error}")
        elif properties is not None:
            errors.extend(validate_properties(path, properties))
        errors.extend(validate_links(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AIFDE Wiki content")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Wiki validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `python3 -m pytest tests/test_validate_wiki.py -q`

Expected: `6 passed`。

- [ ] **Step 5: 提交校验器**

```bash
git add scripts/validate_wiki.py tests/test_validate_wiki.py
git commit -m "test: add wiki structure validator"
```

### Task 4：创建九类标准笔记模板

**Files:**
- Create: `90-Templates/Template-MOC.md`
- Create: `90-Templates/Template-Concept.md`
- Create: `90-Templates/Template-Pattern.md`
- Create: `90-Templates/Template-Experiment.md`
- Create: `90-Templates/Template-Project.md`
- Create: `90-Templates/Template-Source.md`
- Create: `90-Templates/Template-Interview.md`
- Create: `90-Templates/Template-Decision.md`
- Create: `90-Templates/Template-Retrospective.md`

**Interfaces:**
- Consumes: Task 2 的模板目录设置。
- Produces: 九种文档的统一 Front Matter 和写作骨架。

- [ ] **Step 1: 创建公共模板头**

每个模板均使用 Templater 日期表达式，并将 `type` 固定为对应类型：

```yaml
---
type: concept
domain: []
depth: L1
importance: common
maturity: draft
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
last_verified:
aliases: []
tags: []
---
```

- [ ] **Step 2: 写入各类型的强制章节**

模板章节必须完整采用下表，不得以“同上”代替：

| 模板 | 强制章节 |
|---|---|
| MOC | 领域边界、推荐学习顺序、核心主题、常用主题、拓展视野、实验与项目、开源研究、面试入口、相邻领域 |
| Concept | 一句话定义、为什么重要、工作原理、最小示例、适用场景、不适用场景、常见误区、工程实践、相关概念、资料来源 |
| Pattern | 要解决的问题、上下文、方案、数据流、适用条件、代价与风险、失败模式、实现提示、替代方案、相关证据 |
| Experiment | 假设、环境、数据集、变量、步骤、指标、结果、结论、有效性威胁、复现信息、后续行动 |
| Project | 业务问题、目标用户、成功指标、约束与假设、架构、关键决策、仓库与 Demo、评测、安全与可靠性、故障复盘、交付材料、面试追问 |
| Source | 资料信息、为什么值得读、核心观点、关键机制、证据与限制、与 Wiki 的关系、可复现实验、引用 |
| Interview | 问题、考察能力、回答结构、参考答案、常见错误、追问、项目证据、相关知识 |
| Decision | 状态、背景、决策驱动因素、候选方案、最终决策、正面影响、负面影响、验证方式、复审条件 |
| Retrospective | 范围、目标与结果、做得好的地方、失败与根因、数据证据、改进措施、可复用经验、知识库更新 |

- [ ] **Step 3: 为类型增加专属 Properties**

- `experiment`：`repository`、`commit`、`dataset`、`metrics`；
- `project`：`github`、`demo`、`phase`、`tech`；
- `source`：`source_type`、`url`、`authors`、`published`、`accessed`；
- `decision`：`decision_status`，允许 `proposed`、`accepted`、`superseded`；
- 其他模板不增加空泛字段。

- [ ] **Step 4: 检查模板数量和类型**

Run:

```bash
test "$(find 90-Templates -name 'Template-*.md' | wc -l | tr -d ' ')" = "9"
rg '^type: (moc|concept|pattern|experiment|project|source|interview|decision|retrospective)$' 90-Templates | wc -l
```

Expected: 第一条命令退出码为 0；第二条输出 `9`。

- [ ] **Step 5: 提交模板**

```bash
git add 90-Templates
git commit -m "docs: add canonical wiki note templates"
```

### Task 5：建立公共使用指南和 FDE 能力模型

**Files:**
- Create: `00-Guide/How-To-Use.md`
- Create: `00-Guide/AI-Knowledge-Map.md`
- Create: `00-Guide/FDE-Competency-Model.md`
- Create: `00-Guide/Glossary.md`

**Interfaces:**
- Consumes: Task 4 的 MOC、Concept 和 Pattern 模板。
- Produces: 顶层 README 和各领域 MOC 共用的全局说明。

- [ ] **Step 1: 写使用指南**

`How-To-Use.md` 必须说明：目标读者、公开知识产品定位、目录规则、九类文档、L1～L4、`core/common/extension`、成熟度、Markdown 链接方式、Obsidian 推荐设置、如何关联外部 GitHub 项目，以及如何报告错误。

- [ ] **Step 2: 写 AI 全局知识地图**

`AI-Knowledge-Map.md` 必须给出以下主干及相互依赖：数学与 AI 基础、机器学习、深度学习、LLM、RAG、Agent、多模态、生产工程、安全治理、FDE 实践。每个主干列出核心、常用和拓展主题。对应 MOC 尚未创建，因此本任务先使用无链接领域名称；Task 7 和 Task 8 创建 MOC 后立即改为真实相对链接。

- [ ] **Step 3: 写 FDE 能力模型**

`FDE-Competency-Model.md` 使用六维模型：

1. 软件和数据工程；
2. AI/LLM 应用工程；
3. 生产可靠性与安全；
4. 需求发现与业务建模；
5. 客户沟通与交付；
6. 产品化与复用。

每一维均定义 L1～L4 行为证据，并引用设计阶段已核验的 OpenAI、NextLink Labs、Hippocratic AI 和 Nextdata 岗位原文链接。

- [ ] **Step 4: 写术语表**

`Glossary.md` 首批至少收录 40 个术语，覆盖 Token、Embedding、Transformer、Context Window、Function Calling、RAG、Hybrid Search、Reranker、GraphRAG、Agentic RAG、Tool、Memory、MCP、A2A、Evaluation、Guardrail、Tracing、Hallucination、Prompt Injection、Inference、Fine-tuning、LoRA、Quantization、vLLM、FDE 等。已经存在权威笔记的术语添加链接；尚未创建笔记的术语保留为无链接文本，避免故意制造死链。

- [ ] **Step 5: 校验并提交指南**

Run:

```bash
python3 scripts/validate_wiki.py .
npm run lint:md
```

Expected: 输出 `Wiki validation passed`，Markdown lint 无错误。

```bash
git add 00-Guide
git commit -m "docs: add public guide and FDE competency model"
```

### Task 6：编写七阶段路线与横向实践要求

**Files:**
- Create: `01-Roadmap/Roadmap-MOC.md`
- Create: `01-Roadmap/Phase-0-Baseline.md`
- Create: `01-Roadmap/Phase-1-AI-ML-Foundations.md`
- Create: `01-Roadmap/Phase-2-LLM-Engineering.md`
- Create: `01-Roadmap/Phase-3-RAG-Engineering.md`
- Create: `01-Roadmap/Phase-4-Agent-Engineering.md`
- Create: `01-Roadmap/Phase-5-Production-AI.md`
- Create: `01-Roadmap/Phase-6-FDE-Capstone.md`

**Interfaces:**
- Consumes: AI 知识地图和 FDE 能力模型。
- Produces: 按每周 5～10 小时执行的公开推荐路线。

- [ ] **Step 1: 建立路线总览**

`Roadmap-MOC.md` 明确七阶段依赖、建议周期、进入条件和退出证据，并声明时间是建议而非硬期限。每阶段都必须包含“概念 → 最小实验 → 开源使用/源码跟踪/复刻 → 项目增量 → 评测/复盘 → 面试表达”。领域 MOC 尚未创建，本任务对领域名称使用无链接文本；Task 7 和 Task 8 创建目标文件后补充真实相对链接。

- [ ] **Step 2: 编写阶段 0～2**

- 阶段 0（1～2 周）：Python AI 环境、Notebook、FastAPI、模型 API、本地模型、GitHub 项目约定；产出 `ai-engineering-playground` 说明。
- 阶段 1（6～8 周）：必要数学、传统 ML、深度学习、PyTorch、验证与数据问题；产出 `ai-foundations-labs` 说明。
- 阶段 2（6～8 周）：Tokenizer、Embedding、Transformer、Prompt、结构化输出、微调和推理；产出 `llm-engineering-lab` 说明。

每篇都列出推荐深度、必做实验、开源研究对象、面试题类型和验收证据。

- [ ] **Step 3: 编写阶段 3～4**

- 阶段 3（8～12 周）：构建 `production-rag-system`，至少比较 Naive、Hybrid、Rerank 和一种高级 RAG；评测检索、生成、引用、成本和延迟。
- 阶段 4（8～12 周）：构建 `enterprise-workflow-agent`，包含 Tool、State、Memory、审批、重试、恢复、Tracing 和 Agent Eval。

开源实践分别覆盖 LlamaIndex/RAGFlow/GraphRAG 与 LangGraph/OpenAI Agents SDK/MCP Servers，不设置独立开源阶段。

- [ ] **Step 4: 编写阶段 5～6**

- 阶段 5（6～10 周）：对 RAG 或 Agent 项目做网关、缓存、Fallback、可观测性、安全、负载、Docker/Kubernetes 和 CI/CD 加固。
- 阶段 6（8～12 周）：完成一个客户型 FDE 综合项目，包括需求访谈问题、业务指标、PoC 范围、企业集成、评测、上线、Runbook、交接和演示。

- [ ] **Step 5: 校验路线闭环并提交**

Run:

```bash
rg -l '开源' 01-Roadmap/Phase-*.md | wc -l
rg -l '面试' 01-Roadmap/Phase-*.md | wc -l
python3 scripts/validate_wiki.py .
```

Expected: 两次计数均为 `7`，Wiki 校验通过。

```bash
git add 01-Roadmap
git commit -m "docs: publish staged AI FDE roadmap"
```

### Task 7：建立基础、ML、深度学习和 LLM 的领域 MOC

**Files:**
- Create: `02-AI-Foundations/AI-Foundations-MOC.md`
- Create: `03-Machine-Learning/Machine-Learning-MOC.md`
- Create: `04-Deep-Learning/Deep-Learning-MOC.md`
- Create: `05-LLM/LLM-MOC.md`
- Modify: `00-Guide/AI-Knowledge-Map.md`
- Modify: `01-Roadmap/Roadmap-MOC.md`
- Modify: `01-Roadmap/Phase-1-AI-ML-Foundations.md`
- Modify: `01-Roadmap/Phase-2-LLM-Engineering.md`

**Interfaces:**
- Consumes: 全局知识地图和阶段 1～2 路线。
- Produces: 四个领域的稳定知识分类和后续笔记清单。

- [ ] **Step 1: 为每个 MOC 使用统一导航结构**

每个 MOC 包含：领域边界、前置知识、推荐顺序、核心主题、常用主题、拓展视野、最小实验、项目、开源研究、面试入口和相邻领域。

- [ ] **Step 2: 填充精确主题范围**

- AI Foundations：线性代数、概率统计、微积分与梯度、信息论、优化和数值稳定性。
- Machine Learning：回归、分类、树与 Boosting、聚类、降维、异常检测、推荐、时间序列、特征工程、泄漏、校准和指标。
- Deep Learning：MLP、反向传播、初始化、优化器、正则化、CNN、RNN/LSTM、Attention、Transformer 和 PyTorch 工程。
- LLM：Tokenizer、Embedding、预训练目标、Transformer、SFT、PEFT/LoRA、RLHF/DPO、采样、KV Cache、量化、蒸馏、Prompt、Context、结构化输出、Function Calling、幻觉、模型选型和服务。

每个主题标记建议深度和重要程度，尚未创建的笔记使用无链接文本，避免产生故意死链。

将 AI 全局知识地图、路线总览、阶段 1 和阶段 2 中对应的无链接领域名称替换为指向这四个 MOC 的真实相对 Markdown 链接。

- [ ] **Step 3: 校验并提交基础 MOC**

Run: `python3 scripts/validate_wiki.py . && npm run lint:md`

Expected: 两项检查均通过。

```bash
git add 00-Guide/AI-Knowledge-Map.md 01-Roadmap/Roadmap-MOC.md 01-Roadmap/Phase-1-AI-ML-Foundations.md 01-Roadmap/Phase-2-LLM-Engineering.md 02-AI-Foundations 03-Machine-Learning 04-Deep-Learning 05-LLM
git commit -m "docs: map AI foundations and LLM domains"
```

### Task 8：建立 RAG、Agent、多模态、生产、安全和 FDE 的领域 MOC

**Files:**
- Create: `06-RAG/RAG-MOC.md`
- Create: `07-Agent/Agent-MOC.md`
- Create: `08-Multimodal-AI/Multimodal-AI-MOC.md`
- Create: `09-Production-AI/Production-AI-MOC.md`
- Create: `10-AI-Safety-Governance/AI-Safety-Governance-MOC.md`
- Create: `11-FDE-Practice/FDE-Practice-MOC.md`
- Modify: `00-Guide/AI-Knowledge-Map.md`
- Modify: `01-Roadmap/Roadmap-MOC.md`
- Modify: `01-Roadmap/Phase-3-RAG-Engineering.md`
- Modify: `01-Roadmap/Phase-4-Agent-Engineering.md`
- Modify: `01-Roadmap/Phase-5-Production-AI.md`
- Modify: `01-Roadmap/Phase-6-FDE-Capstone.md`

**Interfaces:**
- Consumes: 阶段 3～6 路线。
- Produces: FDE 核心能力领域的完整分类。

- [ ] **Step 1: 编写 RAG MOC**

必须按以下维度组织，而不是平铺名词：

1. 数据摄取与索引；
2. Sparse、Dense、Hybrid 检索；
3. Metadata、Rerank、Parent-Child 和 Small-to-Big；
4. Query Rewrite、Multi-Query、Decomposition、Routing 和 HyDE；
5. Conversational、Multi-hop、Adaptive 和 Iterative RAG；
6. Corrective RAG、Self-RAG、Agentic RAG；
7. GraphRAG、Knowledge Graph RAG、Hierarchical RAG 和 RAPTOR；
8. SQL、结构化、多模态、权限、多租户、时效和流式 RAG；
9. 检索、生成、引用、端到端评测；
10. RAG、长上下文、工具和微调的选型边界。

明确说明这些类别可以组合，并给出至少三条组合示例。

- [ ] **Step 2: 编写 Agent MOC**

覆盖 Workflow/Agent 边界、ReAct、Plan-and-Execute、Reflection、Routing、Tool、Schema、State、Memory、Session、HITL、重试、恢复、幂等、单/多 Agent、Supervisor、MCP、A2A、Browser/Code/Data Agent、Trace Eval、安全和成本控制。

- [ ] **Step 3: 编写其余四个 MOC**

- Multimodal：CV、OCR、文档智能、ASR、TTS、Voice Agent、VLM、多模态检索；推荐、预测、机器人、专家系统和进化算法列为拓展视野。
- Production AI：数据工程、模型网关、路由、缓存、限流、Evals、LLM-as-Judge、Tracing、成本、延迟、vLLM、Docker、Kubernetes、CI/CD 和容量规划。
- Safety & Governance：Prompt Injection、数据外泄、过度代理、知识库投毒、供应链、认证授权、隔离、审计、PII、数据驻留、红队和事件响应。
- FDE Practice：Discovery、流程建模、指标、PoC、ROI、Legacy/API/SSO/VPC/混合云集成、客户演示、需求变化、故障处理、Runbook、交接和产品化复用。

将 AI 全局知识地图、路线总览和阶段 3～6 中对应的无链接领域名称替换为指向这六个 MOC 的真实相对 Markdown 链接。

- [ ] **Step 4: 校验并提交核心 MOC**

Run: `python3 scripts/validate_wiki.py . && npm run lint:md`

Expected: 两项检查均通过。

```bash
git add 00-Guide/AI-Knowledge-Map.md 01-Roadmap/Roadmap-MOC.md 01-Roadmap/Phase-3-RAG-Engineering.md 01-Roadmap/Phase-4-Agent-Engineering.md 01-Roadmap/Phase-5-Production-AI.md 01-Roadmap/Phase-6-FDE-Capstone.md 06-RAG 07-Agent 08-Multimodal-AI 09-Production-AI 10-AI-Safety-Governance 11-FDE-Practice
git commit -m "docs: map production AI and FDE domains"
```

### Task 9：建立项目、开源、面试和招聘证据区

**Files:**
- Create: `12-Projects/Projects-MOC.md`
- Create: `12-Projects/PRJ-AIFDE-Wiki.md`
- Create: `13-Open-Source/Open-Source-MOC.md`
- Create: `13-Open-Source/Repo-LangGraph.md`
- Create: `14-Interview/Interview-MOC.md`
- Create: `14-Interview/如何评测一个RAG系统.md`
- Create: `15-Job-Market/Job-Market-MOC.md`
- Create: `15-Job-Market/Job-OpenAI-FDE-Healthcare-20260909.md`

**Interfaces:**
- Consumes: Project、Source、Interview 模板和 FDE 能力模型。
- Produces: 可验证的实践、源码、面试和岗位样例。

- [ ] **Step 1: 建立项目区**

`Projects-MOC.md` 解释外部仓库边界和六级项目阶梯。`PRJ-AIFDE-Wiki.md` 将当前 Wiki 本身作为公开知识产品案例，记录目标、架构、质量指标、公开安全要求和设计文档链接；`github` 字段在远程仓库创建后填写，在此之前成熟度保持 `draft`，并在正文明确“远程地址将在首次公开发布时记录”，不使用虚假 URL。

- [ ] **Step 2: 建立开源研究区**

`Open-Source-MOC.md` 定义“使用与评测 → 调用链跟踪 → 最小复刻 → 改造或贡献”，按阶段列出代表仓库和许可证检查要求。

`Repo-LangGraph.md` 使用官方仓库作为首个 Source 示例，至少记录：项目定位、许可证、核心抽象、一次 StateGraph 调用链、可靠性设计、值得复刻的最小子集、局限、访问日期和官方链接。

- [ ] **Step 3: 建立面试区**

`Interview-MOC.md` 按实用编码、AI 原理、RAG/Agent、系统设计、生产故障、项目答辩、客户场景和行为面试分类。

`如何评测一个RAG系统.md` 必须区分检索、生成、引用和端到端业务指标，给出离线/在线评测、数据集构建、LLM-as-Judge 风险、追问和项目证据结构。

- [ ] **Step 4: 建立招聘证据区**

`Job-Market-MOC.md` 定义岗位名称集合、样本字段、季度采样方法、技能归一化词表和自动访问失败处理规则。

`Job-OpenAI-FDE-Healthcare-20260909.md` 只根据已核验的官方页面摘要职责和要求，记录访问日期、来源 URL、能力标签及其对路线的影响，不复制岗位全文。

- [ ] **Step 5: 校验类型样例并提交**

Run:

```bash
for type in project source interview; do rg -l "^type: $type$" 12-Projects 13-Open-Source 14-Interview 15-Job-Market; done
python3 scripts/validate_wiki.py .
```

Expected: project、source、interview 均至少输出一个文件，Wiki 校验通过。

```bash
git add 12-Projects 13-Open-Source 14-Interview 15-Job-Market
git commit -m "docs: add project open-source interview and job evidence"
```

### Task 10：补齐 Pattern、Experiment、Decision 和 Retrospective 样例

**Files:**
- Create: `05-LLM/词元化 (Tokenization).md`
- Create: `06-RAG/混合检索 (Hybrid Search).md`
- Create: `06-RAG/EXP-20260909-Retrieval-Baseline.md`
- Create: `09-Production-AI/ADR-001-Wiki-Link-Format.md`
- Create: `11-FDE-Practice/RETRO-AIFDE-Wiki-Foundation.md`

**Interfaces:**
- Consumes: Task 4 模板和 Task 7～9 的 MOC。
- Produces: `concept`、`pattern`、`experiment`、`decision` 和 `retrospective` 五类真实示例，连同前序任务覆盖全部九种文档类型。

- [ ] **Step 1: 写 Concept 示例**

`词元化 (Tokenization).md` 解释字符、词和子词粒度，覆盖 BPE、WordPiece、Unigram、特殊 Token、词表大小、中文与代码场景、长度和成本影响，以及 Tokenizer 与模型权重必须匹配的原因；链接 LLM MOC，并引用至少一个官方 Tokenizer 文档或原始论文。

- [ ] **Step 2: 写 Pattern 示例**

`混合检索 (Hybrid Search).md` 解释 BM25 与 Dense Retrieval 的互补性、分数归一化和融合方法、RRF、Rerank 位置、适用条件、成本、失败模式及评测方法，并链接 RAG MOC。

- [ ] **Step 3: 写 Experiment 示例**

`EXP-20260909-Retrieval-Baseline.md` 是实验设计而非虚构结果。明确假设、公开数据集选择标准、BM25/Dense/Hybrid 三组变量、Recall@k、MRR、nDCG、延迟和成本指标、复现命令接口及结果记录表；在真实外部实验仓库建立前保持 `draft`，不填写虚假 Commit。

- [ ] **Step 4: 写 Decision 示例**

`ADR-001-Wiki-Link-Format.md` 记录标准相对 Markdown 链接与 Wiki Link 的比较，最终选择标准 Markdown 链接，原因是 GitHub 兼容性优先；记录对 Obsidian `useMarkdownLinks` 的影响。

- [ ] **Step 5: 写 Retrospective 示例**

`RETRO-AIFDE-Wiki-Foundation.md` 复盘设计阶段：已确认的目标、关键决策、曾发现的 GitHub/Wiki Link 冲突、中文化修订、未完成的远程发布，以及进入下一轮内容建设前的改进事项。

- [ ] **Step 6: 验证九类文档均有样例**

Run:

```bash
for type in moc concept pattern experiment project source interview decision retrospective; do
  test -n "$(rg -l "^type: $type$" 00-Guide 01-Roadmap 02-AI-Foundations 03-Machine-Learning 04-Deep-Learning 05-LLM 06-RAG 07-Agent 08-Multimodal-AI 09-Production-AI 10-AI-Safety-Governance 11-FDE-Practice 12-Projects 13-Open-Source 14-Interview 15-Job-Market | head -1)" || exit 1
done
python3 scripts/validate_wiki.py .
```

Expected: 命令退出码为 0，Wiki 校验通过。

```bash
git add '05-LLM/词元化 (Tokenization).md' '06-RAG/混合检索 (Hybrid Search).md' 06-RAG/EXP-20260909-Retrieval-Baseline.md 09-Production-AI/ADR-001-Wiki-Link-Format.md 11-FDE-Practice/RETRO-AIFDE-Wiki-Foundation.md
git commit -m "docs: demonstrate evidence-driven note types"
```

### Task 11：完成公开入口、贡献规范和双许可证

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `LICENSE-CONTENT`
- Create: `LICENSE-CODE`

**Interfaces:**
- Consumes: 所有 Guide、Roadmap、MOC 和样例内容。
- Produces: GitHub 访客无需 Obsidian 即可使用的公开入口。

- [ ] **Step 1: 编写根 README**

按以下固定顺序写入：项目定位、目标读者、阅读入口、AI 知识地图、FDE 能力模型、七阶段路线、领域导航、代表性项目与实验、开源研究、面试准备、内容状态、贡献方式和许可证。

README 必须明确：不承诺所有主题同等深度；`extension` 只要求视野层理解；所有内部入口使用可在 GitHub 打开的相对 Markdown 链接。

- [ ] **Step 2: 编写贡献规范**

`CONTRIBUTING.md` 包含：环境准备、文件命名、Properties 枚举、九类模板、来源优先级、招聘摘要版权规则、开源许可证检查、公开安全检查、本地测试命令、分支/PR 规则和 Commit 示例。

本地检查命令固定为：

```bash
python3 -m pytest -q
python3 scripts/validate_wiki.py .
npm run lint:md
```

- [ ] **Step 3: 添加双许可证**

- `LICENSE-CONTENT` 使用 CC BY 4.0 官方法律文本，并声明适用于原创 Markdown 正文和图表。
- `LICENSE-CODE` 使用 MIT License 官方文本，版权年份为 2026，适用于仓库中的原创可执行代码片段和脚本。
- README 和 CONTRIBUTING 清楚解释适用范围；第三方内容仍遵循原许可证。

- [ ] **Step 4: 检查公开入口链接**

Run:

```bash
python3 scripts/validate_wiki.py .
npm run lint:md
test ! -e 00-Home/Dashboard.md
test ! -d Daily
```

Expected: 四项检查均以退出码 0 通过。

- [ ] **Step 5: 提交公开入口**

```bash
git add README.md CONTRIBUTING.md LICENSE-CONTENT LICENSE-CODE
git commit -m "docs: publish AIFDE Wiki entry point"
```

### Task 12：接入 CI 并执行最终验收

**Files:**
- Create: `.github/workflows/wiki-quality.yml`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: Task 1 的依赖、Task 3 的校验器和完整 Wiki 内容。
- Produces: Pull Request 与 `main` push 的自动质量门禁。

- [ ] **Step 1: 创建质量工作流**

`.github/workflows/wiki-quality.yml` 必须：

- 在 `pull_request` 和向 `main` push 时触发；
- 使用 `actions/checkout@v7`；
- 使用 `actions/setup-python@v7` 和 Python `3.12`；
- 使用 `actions/setup-node@v7` 和 Node.js `26`；
- 安装 `requirements-dev.txt` 并运行 pytest 与 Wiki validator；
- 使用 Node.js 安装 `package-lock.json` 中的依赖并运行 markdownlint；
- 使用 `lycheeverse/lychee-action@v2.9.0` 检查 Markdown 外部链接；
- 使用 `gitleaks/gitleaks-action@v3.0.0` 扫描密钥；
- 为偶发限流站点配置明确的 lychee 排除清单，不得用全局忽略失败掩盖死链。

完整工作流为：

```yaml
name: Wiki quality

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  content:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip

      - name: Set up Node.js
        uses: actions/setup-node@v7
        with:
          node-version: "26"
          cache: npm

      - name: Install dependencies
        run: |
          python -m pip install -r requirements-dev.txt
          npm ci

      - name: Run validator tests
        run: python -m pytest -q

      - name: Validate Wiki structure
        run: python scripts/validate_wiki.py .

      - name: Lint Markdown
        run: npm run lint:md

      - name: Check links
        uses: lycheeverse/lychee-action@v2.9.0
        with:
          args: >-
            --verbose
            --no-progress
            --exclude-mail
            --exclude 'https://www.zhipin.com/.*'
            './**/*.md'
          fail: true

      - name: Scan secrets
        uses: gitleaks/gitleaks-action@v3.0.0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: 验证 Node 锁文件**

Run: `npm ci && npm ls markdownlint-cli2`

Expected: 安装成功，依赖树输出 `markdownlint-cli2@0.23.2`，且 `package-lock.json` 不发生变化。

- [ ] **Step 3: 更新变更记录**

在 `CHANGELOG.md` 的 `2026-09-09` 条目中列出：公开入口、七阶段路线、十个领域 MOC、九类模板、代表性样例、校验器和 CI。

- [ ] **Step 4: 执行完整本地验收**

Run:

```bash
python3 -m pip install -r requirements-dev.txt
npm ci
python3 -m pytest -q
python3 scripts/validate_wiki.py .
npm run lint:md
git diff --check
git status --short
```

Expected:

- pytest 全部通过；
- 输出 `Wiki validation passed`；
- Markdown lint 无错误；
- `git diff --check` 无输出；
- `git status --short` 只显示本任务计划提交的 `.github/workflows/wiki-quality.yml` 和 `CHANGELOG.md`。

- [ ] **Step 5: 提交 CI**

```bash
git add .github/workflows/wiki-quality.yml CHANGELOG.md
git commit -m "ci: enforce public wiki quality checks"
```

- [ ] **Step 6: 核对设计验收标准**

逐项对照 `docs/superpowers/specs/2026-09-09-aifde-wiki-design.md` 第 17 节，确认十条验收标准均有对应文件或检查命令。运行：

```bash
find 00-Guide 01-Roadmap 02-AI-Foundations 03-Machine-Learning 04-Deep-Learning 05-LLM 06-RAG 07-Agent 08-Multimodal-AI 09-Production-AI 10-AI-Safety-Governance 11-FDE-Practice 12-Projects 13-Open-Source 14-Interview 15-Job-Market 90-Templates -type f -name '*.md' | sort
git log --oneline --decorate -12
```

Expected: 所有规划文件均存在，提交历史按任务形成可审查的独立提交。

## 远程发布边界

本计划不猜测 GitHub Owner，也不自动创建远程仓库。完成本地验收后，执行者应向仓库所有者确认准确的公开 GitHub 地址，再添加 `origin`、推送 `main`，并将真实地址回填到 `12-Projects/PRJ-AIFDE-Wiki.md`。创建公开仓库和首次推送属于单独的发布动作，不应使用虚假 URL 代替。
