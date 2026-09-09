# AIFDE Wiki 设计文档

**日期：** 2026-09-09

**状态：** 已确认，可进入实施计划阶段

**仓库：** `AIFDE-Wiki`

**主要编辑环境：** Obsidian

**主要发布环境：** GitHub 公开仓库

## 1. 建设目标

`AIFDE-Wiki` 是一个公开知识产品，面向已经具备后端或全栈研发经验，希望转向 AI 应用工程和前沿部署工程（Forward Deployed Engineering，FDE）的软件工程师。

Wiki 需要连接以下五类能力：

1. AI 基础概念、算法和模型原理。
2. LLM、RAG、Agent、多模态及相关应用工程能力。
3. 评测、安全、可观测性、部署及其他生产工程能力。
4. 开源项目的使用、源码学习、最小复刻、二次开发和贡献。
5. FDE 交付与面试能力，包括模糊需求处理、企业集成、客户沟通、系统设计和项目答辩。

本仓库不是个人效率系统，不管理私有学习任务、日记、个人完成率或私人 Dashboard。

## 2. 目标读者

主要读者包括：

- 已经具备软件工程经验的后端或全栈工程师；
- 希望学习生产级 AI，而非以纯模型研究为目标的工程师；
- 准备应聘 AI 应用工程师、Agent 工程师、AI 解决方案工程师、Applied AI Engineer 或 FDE 的工程师；
- 未来的仓库维护者，需要一份长期有效的概念、实验、项目和资料地图。

实践技术栈以 Python 为主，以 Vue 和 TypeScript 作为界面开发及系统集成的辅助技术。

## 3. 设计原则

### 3.1 公开知识产品优先

- GitHub 可以直接渲染的 Markdown 是最低体验基线。
- Obsidian 用于增强编辑和导航，但阅读核心内容不应依赖 Obsidian。
- 根目录 `README.md` 是稳定的公开入口。
- Dataview 可以辅助作者查询，但任何关键导航都不能依赖 Dataview。

### 3.2 广泛覆盖，按需深入

Wiki 覆盖常见 AI 领域及其重要细分方向，但不对所有主题平均投入。

| 深度 | 达成标准 |
|---|---|
| L1——认知 | 能解释原理、应用场景、局限，以及它与相邻技术的关系。 |
| L2——实验 | 能实现或复现最小实验，并解释重要参数。 |
| L3——工程 | 能将技术集成到经过测试的项目中，并用证据说明取舍。 |
| L4——生产/FDE | 能在业务约束下部署、评测、监控、保护、治理、交接并答辩。 |

每个主题还需要标记重要程度：

- `core`：建议达到 L3 或 L4；
- `common`：建议达到 L2 或 L3；
- `extension`：默认达到 L1，项目确有需要时再深入。

LLM 应用工程、RAG、Agent、评测、安全、可观测性、部署和 FDE 交付属于核心主线。不常见或当前实用价值较低的方向仍保留为拓展主题，介绍原理和应用场景，但不默认安排专项项目。

### 3.3 用证据代替“学完”

读完一篇资料不代表已经掌握主题。高质量内容应将概念关联到至少一种证据：

- 可复现实验；
- 最小复刻；
- 面向生产的项目；
- 源码调用链分析；
- 评测报告；
- 故障或失败分析；
- 能经受追问的面试回答。

### 3.4 一个概念只有一篇权威笔记

跨领域概念通过链接复用，不复制内容。MOC 负责导航和学习顺序，权威概念笔记负责解释正文。

### 3.5 明确资料来源和时效性

- 优先使用论文、官方文档、官方仓库和招聘原文。
- 明确区分资料结论、维护者理解和实验发现。
- 对变化较快的技术和招聘观察记录访问或核验日期。
- 招聘资料只做摘要和统计，不转载完整岗位描述。

## 4. 信息架构

Wiki 采用混合内容地图（Map of Content，MOC）模式：稳定目录定义领域边界，MOC 表达主题关系和推荐路线，适度原子化的笔记负责内容复用。

```text
AIFDE-Wiki/
├── README.md
├── LICENSE-CONTENT
├── LICENSE-CODE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── 00-Guide/
│   ├── How-To-Use.md
│   ├── AI-Knowledge-Map.md
│   ├── FDE-Competency-Model.md
│   └── Glossary.md
├── 01-Roadmap/
│   ├── Roadmap-MOC.md
│   ├── Phase-0-Baseline.md
│   ├── Phase-1-AI-ML-Foundations.md
│   ├── Phase-2-LLM-Engineering.md
│   ├── Phase-3-RAG-Engineering.md
│   ├── Phase-4-Agent-Engineering.md
│   ├── Phase-5-Production-AI.md
│   └── Phase-6-FDE-Capstone.md
├── 02-AI-Foundations/
├── 03-Machine-Learning/
├── 04-Deep-Learning/
├── 05-LLM/
├── 06-RAG/
├── 07-Agent/
├── 08-Multimodal-AI/
├── 09-Production-AI/
├── 10-AI-Safety-Governance/
├── 11-FDE-Practice/
├── 12-Projects/
├── 13-Open-Source/
├── 14-Interview/
├── 15-Job-Market/
├── 90-Templates/
├── 99-Assets/
└── docs/superpowers/
    ├── specs/
    └── plans/
```

每个主要知识目录包含一个 `<Domain>-MOC.md` 文件。只有当 MOC 已难以浏览，或某个稳定的细分领域已积累足够内容时，才继续增加子目录。

## 5. 笔记模型

Wiki 采用适度原子化：一篇笔记回答一个可以独立引用的问题，但细小参数和紧密相关的术语不强行拆分。

### 5.1 文档类型

| 类型 | 职责 |
|---|---|
| `moc` | 定义领域范围、主题关系、推荐顺序及实践入口。 |
| `concept` | 解释原理、算法、模型或基础概念。 |
| `pattern` | 解释可组合的工程架构或解决方案模式。 |
| `experiment` | 记录可复现的假设、环境、变量、指标、结果和结论。 |
| `project` | 描述外部 GitHub 实践项目及其交付证据。 |
| `source` | 分析论文、开源仓库、官方文档或招聘样本。 |
| `interview` | 记录问题、回答框架、常见误区和追问。 |
| `decision` | 记录技术选择、备选方案、证据和后果。 |
| `retrospective` | 记录项目、实验集合或重要内容修订的复盘。 |

### 5.2 公共 Properties

```yaml
---
type: concept
domain:
  - RAG
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - Hybrid Retrieval
tags: []
---
```

`maturity` 使用四种状态：

- `draft`：已有可用内容，但尚未通过质量检查；
- `reviewed`：已核对主要来源，内容内部一致；
- `stable`：具有可复现证据，适合作为长期参考；
- `needs-update`：已知需要检查时效性或正确性。

只在确有需要时添加文档类型专属字段：

```yaml
# 资料
source_type: paper
url: https://example.com/source
authors: []
published: 2024-01-01
accessed: 2026-09-09

# 项目
github: https://github.com/example/project
demo: https://example.com/demo
phase: RAG
tech:
  - Python
  - Vue
  - TypeScript

# 实验
repository: https://github.com/example/project
commit: abc1234
dataset: evaluation-set-v1
metrics:
  - recall_at_10
```

## 6. 命名、语言和链接规则

### 6.1 语言

- 正文以中文为主。
- 重要术语首次出现时给出标准英文名称。
- 缩写、产品名和业界固定名称保留英文。

示例：

```text
混合检索 (Hybrid Search).md
重排序 (Reranking).md
上下文工程 (Context Engineering).md
GraphRAG.md
BM25.md
LoRA.md
```

### 6.2 文件命名

```text
领域导航：RAG-MOC.md
实验：EXP-20260909-Chunk-Size-Comparison.md
项目：PRJ-Production-RAG.md
架构决策：ADR-001-Vector-Database-Selection.md
复盘：RETRO-Production-RAG-V1.md
论文笔记：Paper-Self-RAG.md
仓库笔记：Repo-LangGraph.md
岗位样本：Job-Company-Role-20260909.md
```

文件名不得包含 `/`、`\`、`:`、`?`、`#` 等影响跨平台兼容性的字符。

### 6.3 链接

- 仓库内链接统一使用相对 Markdown 链接，确保 GitHub 和 Obsidian 均能正常打开。
- Obsidian 配置为使用 Markdown 链接，不使用仅在 Obsidian 内解析的 Wiki Link。
- 外部资料使用标准 Markdown 链接。
- 每篇知识笔记至少链接到一个上级 MOC。
- 标签仅描述 `core`、`extension`、`interview`、`needs-review` 等横向语境；领域分类放在 `domain` 属性中。
- 附件统一存放于 `99-Assets/`。

内部链接示例：

```markdown
[混合检索](./Retrieval/混合检索%20(Hybrid%20Search).md)
[重排序](./Retrieval/重排序%20(Reranking).md)
```

## 7. 知识覆盖范围

### 7.1 数学与 AI 基础

- 线性代数：向量、矩阵、张量、特征值和相似度；
- 概率统计：常见分布、贝叶斯推理、期望、方差和不确定性；
- 梯度、链式法则、优化方法、数值稳定性和自动微分；
- 熵、交叉熵、KL 散度及信息论直觉。

### 7.2 传统机器学习

- 回归与分类；
- 决策树、随机森林、梯度提升和集成学习；
- 聚类、降维和异常检测；
- 推荐系统和时间序列基础；
- 特征工程、类别不平衡、数据泄漏、校准、验证和指标选择。

### 7.3 深度学习

- MLP、反向传播、初始化、优化器和正则化；
- CNN、RNN、LSTM、Attention、Transformer 和 Embedding；
- PyTorch 张量、Autograd、Dataset、训练循环、评估和模型序列化。

### 7.4 NLP 与 LLM 工程

- Tokenization、Embedding、语言模型训练目标和 Transformer 架构；
- 预训练、监督微调、PEFT/LoRA、RLHF、DPO、蒸馏和模型适配；
- 采样、推理行为、上下文窗口、KV Cache、量化、批处理和推理成本；
- Prompt Engineering、Context Engineering、结构化输出、Function Calling 和模型选型；
- 幻觉、不确定性、Grounding 和模型局限。

### 7.5 RAG

RAG 被视为可组合的设计空间，而不是单一的向量检索流水线。

- Naive RAG 和 Modular RAG；
- Sparse、Dense 和 Hybrid Retrieval；
- Metadata Filtering、Reranking、Parent-Child Retrieval 和 Small-to-Big Retrieval；
- Query Rewriting、Multi-Query、Query Decomposition、Routing 和 HyDE；
- Conversational RAG、Multi-hop RAG、Adaptive RAG 和 Iterative RAG；
- Corrective RAG 和 Self-RAG；
- Agentic RAG/Agent RAG；
- GraphRAG 和 Knowledge Graph RAG；
- Hierarchical RAG 和 RAPTOR；
- SQL 与结构化数据 RAG；
- Multimodal RAG；
- 权限感知、多租户、时效性和流式数据 RAG；
- 索引、检索、生成、引用及端到端评测；
- RAG、长上下文、工具调用和微调之间的选型边界。

以上名称不是互斥类别。笔记需要解释它们如何组合，以及各自的运行成本、失败模式和选择标准。

### 7.6 Agent 系统

- Workflow 与 Agent 的边界；
- ReAct、Plan-and-Execute、Reflection 和 Routing 模式；
- Tool、Schema、State、Memory、Session 和上下文管理；
- 人工审批、升级、重试、恢复和幂等；
- 单 Agent、Supervisor、Hierarchical 和 Multi-Agent 模式；
- MCP、A2A 和企业工具集成；
- Browser、Code、Data 和 Workflow Agent；
- Trace 评测、安全边界和失控成本治理。

### 7.7 多模态及相邻 AI 领域

- 计算机视觉、OCR 和文档智能；
- 语音识别、语音合成和 Voice Agent；
- 视觉语言模型和多模态检索；
- 推荐、预测、优化、机器人、专家系统、进化算法和生成模型。

最后一组内容主要用于拓展知识视野。只有当相关技术常见于 FDE 工作，或被具体项目需要时，才深入到 L1 以上。

### 7.8 生产级 AI

- 数据采集、ETL/ELT、质量、血缘和治理；
- 模型网关、供应商抽象、路由、Fallback、缓存、限流和密钥管理；
- 离线、在线、检索、生成及 Agent 评测；
- LLM-as-Judge 设计、校准、数据集、回归测试和 CI 评测；
- Trace、日志、指标、反馈闭环、成本、延迟和可靠性；
- 模型服务、vLLM、容器、Kubernetes、CI/CD、回滚和容量规划；
- API 设计、异步工作流、消息队列和企业集成。

### 7.9 AI 安全与治理

- Prompt Injection、间接注入、数据外泄、过度代理和不安全工具调用；
- 知识库投毒、不安全输出处理和供应链风险；
- 认证、授权、最小权限、隔离、审计和人工审核；
- PII、数据驻留、保留策略、合规、红队测试和事件响应。

### 7.10 FDE 实践

- 技术需求发现和业务流程建模；
- 将模糊业务目标转化为可度量结果；
- PoC 范围、验收标准、ROI 和上线条件；
- 遗留系统、API、数据平台、身份系统、VPC、混合云和本地部署集成；
- 利益相关者沟通、演示、需求变化和故障应对；
- 生产交接、Runbook、用户采用、反馈和可复用交付组件。

### 7.11 面试准备

- Python 实用编码和数据处理；
- AI、ML、LLM、RAG、Agent、评测和安全基础；
- 成本、延迟、数据、隐私和部署约束下的 AI 系统设计；
- 项目深挖、架构取舍、失败分析和指标；
- 模糊客户场景、范围协商、现场调试和行为案例。

## 8. 推荐学习路线

路线提供建议而非强制期限。时间估算以每周投入 5～10 小时为基础。

| 阶段 | 建议周期 | 主要产出 |
|---|---:|---|
| 阶段 0：基线与环境 | 1～2 周 | 建立 AI 工程工具链、Wiki 规范和最小模型/API 基线。 |
| 阶段 1：AI/ML 基础 | 6～8 周 | 理解必要数学、传统 ML、深度学习、PyTorch、指标和数据失败模式。 |
| 阶段 2：LLM 工程 | 6～8 周 | 理解并实验 Transformer 行为、Prompt、结构化输出、模型适配、推理和模型 API。 |
| 阶段 3：RAG 工程 | 8～12 周 | 构建并评测面向生产的 RAG 系统，对比有代表性的检索架构。 |
| 阶段 4：Agent 工程 | 8～12 周 | 构建具有状态、记忆、审批、恢复、Tracing 和评测的可靠工具调用工作流。 |
| 阶段 5：生产级 AI | 6～10 周 | 用安全、可观测性、成本、部署、CI/CD 和运行证据加固已有系统。 |
| 阶段 6：FDE 综合项目 | 8～12 周 | 从需求发现到生产交接，端到端交付一个客户型 AI 系统。 |

每个阶段都应形成以下闭环：

```text
概念 -> 最小实验 -> 开源学习/复刻 -> 生产项目增量
     -> 评测/失败复盘 -> 面试表达 -> Wiki 沉淀
```

路线不设置独立且靠后的开源阶段。开源实践和面试准备作为横向轨道贯穿所有阶段。

## 9. 开源实践

每个相关阶段采用四层开源实践：

1. **使用和评测：** 跑通项目，记录安装过程、架构、优势、限制和运行表现。
2. **跟踪和解释：** 沿源码追踪一条有意义的调用链或子系统。
3. **最小复刻：** 独立实现核心机制的最小版本，用于验证理解。
4. **改造或贡献：** 在确有价值时进行二次开发、发布对比结果、提交高质量 Issue，或贡献文档、测试、Bug Fix 和功能。

有代表性的学习对象包括：

| 领域 | 代表项目 | 最小复刻目标 |
|---|---|---|
| AI/ML | scikit-learn、PyTorch | 核心模型、反向传播和训练循环。 |
| LLM | Transformers、nanoGPT、OpenAI Cookbook | Tokenizer、Attention、简化 Transformer 和模型调用层。 |
| RAG | LlamaIndex、RAGFlow、GraphRAG、pgvector、Qdrant | 数据摄取、混合检索、重排序、评测及一种高级 RAG 方法。 |
| Agent | LangGraph、OpenAI Agents SDK、MCP Servers | Agent Loop、Tool Registry、状态、记忆、审批和恢复。 |
| 生产工程 | LiteLLM、vLLM、DeepEval、promptfoo | 模型网关、路由/Fallback、评测运行器、Tracing 和安全测试。 |
| 端到端产品 | Dify、RAGFlow | 学习完整架构，并独立设计客户解决方案。 |

每篇开源仓库笔记都要记录许可证。复刻项目必须标明灵感来源，并明确区分学习性复刻和原创产品。

## 10. 实战项目模型

实践代码存放于独立 GitHub 仓库，Wiki 只保存项目档案，不复制源码树。

每份项目档案包含：

1. 业务问题和目标用户。
2. 成功指标和验收标准。
3. 约束、假设和需求发现问题。
4. 架构及关键决策。
5. Repository、Demo、API 文档、Issue、Commit 和 Release 链接。
6. 数据集和评测设计。
7. 质量、成本、延迟、安全和可靠性结果。
8. 失败、故障及改进记录。
9. 面试表达和可能的追问。
10. 可复用组件和开源机会。

推荐的项目阶梯：

- `ai-foundations-labs`；
- `llm-engineering-lab`；
- `production-rag-system`；
- `enterprise-workflow-agent`；
- 对 RAG 或 Agent 系统进行生产化加固；
- 一个独立的 FDE 综合项目仓库。

## 11. 招聘市场与面试证据

岗位研究不能只搜索字面上的 `FDE`，还应覆盖：

- Forward Deployed Engineer；
- Forward Deployed AI Engineer；
- Applied AI Engineer；
- AI Application Engineer；
- Agent Engineer；
- AI Solution Engineer；
- 具有大量 AI 实际交付工作的 Customer Engineer 和 Solution Architect。

岗位样本来自企业官方招聘页、BOSS 直聘及其他招聘平台。每个样本记录公司、岗位、地点、级别、职责、技能要求、来源链接和访问日期。遇到自动访问失败时应如实记录，不把未经核验的搜索摘要当作岗位原文证据。

本设计调研的岗位样本体现出一些反复出现的能力组合：端到端交付责任、Python 和生产级软件工程、RAG 与 Agent、评测、企业数据和 API 集成、云或混合部署、安全治理，以及直接与客户利益相关者合作。代表性来源包括：

- [OpenAI——Forward Deployed Engineer, Healthcare](https://openai.com/careers/forward-deployed-engineer-%28fde%29-healthcare-sf-san-francisco/)
- [NextLink Labs——Forward Deployed Engineer, AI](https://jobs.ashbyhq.com/nextlinklabs/cb0bf55f-055a-489e-b982-4aa321036423/)
- [Hippocratic AI——Forward Deployed Engineer](https://jobs.ashbyhq.com/hippocratic%20ai/af528529-1c4b-4cc4-b073-4e4522fd2ab6)
- [Nextdata——Forward Deployed Engineer](https://jobs.ashbyhq.com/nextdata/4feeb725-13e9-440b-984b-b173f943317b)

面试内容按照能力组织，而不是只积累背诵答案：

- 实用编码和调试；
- 数据与 AI 系统设计；
- LLM、RAG 和 Agent 技术深度；
- 生产可靠性、评测、安全和治理；
- 项目深挖；
- 客户需求发现、模糊问题、优先级和沟通。

## 12. 公开仓库体验

### 12.1 根目录 README

根目录 `README.md` 包含：

1. Wiki 定位和目标读者。
2. AI 全局知识地图。
3. FDE 能力模型。
4. 推荐学习路线。
5. 领域导航。
6. 代表性实验和项目。
7. 开源项目研究。
8. 面试准备。
9. 内容状态、许可证和贡献入口。

仓库不包含个人 Dashboard 或个人学习完成率。

### 12.2 Obsidian 插件

默认配置保持轻量：

- Templater：统一创建笔记；
- Linter：统一 Markdown 和 Properties 格式；
- Dataview：仅作为可选的作者辅助工具；
- Obsidian Git：为不使用命令行 Git 的贡献者提供可选界面。

不引入 Tasks，因为本仓库不管理个人学习任务。

### 12.3 版本管理

- 仓库在 GitHub 上公开。
- 普通内容更新可以直接提交到 `main`。
- 结构调整、模板变更和大规模内容改写使用分支及 Pull Request。
- Commit 描述具体内容产出，例如 `docs(rag): explain hybrid retrieval trade-offs`。
- 设备相关 Workspace 状态、缓存、回收站、环境文件、密钥和私有数据必须忽略。
- 可复用 Obsidian 配置、插件 ID、模板和公开内容需要提交。

## 13. 内容质量与维护

### 13.1 正式笔记的最低质量

一篇达到 `reviewed` 状态的笔记必须：

- 回答一个明确问题；
- 标记领域、重要程度、深度、成熟度和日期；
- 解释技术的适用和不适用场景；
- 为重要事实引用可靠来源；
- 区分资料结论、个人理解和实验依据；
- 核心主题至少包含一个示例、实验或项目链接；
- 链接到至少一个 MOC 和相关概念；
- 不包含隐私、密钥或未经许可复制的内容。

### 13.2 维护机制

- `CHANGELOG.md` 记录重要分类、路线和内容变化。
- GitHub Issues 跟踪缺失主题、错误、死链和改进建议。
- `last_verified` 标记时效性强的内容。
- 在持续维护期间，招聘观察至少每季度重新采样一次。
- 框架或模型发生重大变化时，检查受影响的 MOC 和笔记。

### 13.3 自动检查

实施阶段应添加轻量 GitHub Actions，检查：

- Markdown 格式；
- YAML Properties；
- 内部和外部链接；
- 意外提交的密钥；
- 初始内容稳定后，可选增加中英文拼写检查。

## 14. 许可证与公开安全规则

- 原创文章和图表采用知识共享署名 4.0 协议（`CC BY 4.0`）。
- 原创可执行代码片段采用 MIT License。
- 第三方内容继续遵循其原始许可证并明确署名。
- 招聘岗位只做摘要和链接，不转载原文。
- 不转载付费书籍、课程、面试题库和专有材料。
- 项目复盘不得泄露前雇主、客户、凭证或私有系统信息。

## 15. 初始资料集合

以下一手资料作为初始锚点，但不构成固定不变的依赖清单：

- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
- [OpenAI Agents SDK for Python](https://github.com/openai/openai-agents-python)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LlamaIndex](https://github.com/run-llama/llama_index)
- [RAGFlow](https://github.com/infiniflow/ragflow)
- [Dify](https://github.com/langgenius/dify)
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [pgvector](https://github.com/pgvector/pgvector)
- [Qdrant](https://github.com/qdrant/qdrant)
- [vLLM](https://github.com/vllm-project/vllm)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [DeepEval](https://github.com/confident-ai/deepeval)
- [promptfoo](https://github.com/promptfoo/promptfoo)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers)
- [Self-RAG 论文](https://arxiv.org/abs/2310.11511)
- [Corrective RAG 论文](https://arxiv.org/abs/2401.15884)
- [RAPTOR 论文](https://arxiv.org/abs/2401.18059)

## 16. 实施边界

首次实施负责建立仓库骨架、规范、模板、导航、校验机制和路线图，不试图一次性写完整个 AI 知识库。

初始内容需要覆盖所有文档类型，以验证信息架构和导航模型。后续按照领域和阶段增量建设；每次增量都应能在 GitHub 中直接阅读，并从对应 MOC 到达。

## 17. 设计验收标准

满足以下条件即表示本设计实施成功：

1. GitHub 访客可以从根目录 README 理解仓库目标、读者、知识范围和推荐路线。
2. 每个主要 AI/FDE 领域都有可发现的 MOC 和明确的建议深度。
3. 仓库为九种文档类型提供可用模板。
4. 不依赖 Dataview，内部导航也能同时在 Obsidian 和 GitHub 工作。
5. 至少有一篇有代表性的概念、实验、项目、资料、面试、决策和复盘笔记，用于演示内容模型。
6. 项目档案能够正确链接到外部 GitHub 实践仓库及交付证据。
7. 开源使用、调用链跟踪、最小复刻和可选贡献贯穿学习路线。
8. 自动检查能够发现错误 Properties、死链、Markdown 问题和意外密钥。
9. 许可证、署名和公开安全规则可见，并通过贡献指南落实。
10. 公开知识产品中不包含个人 Dashboard、日记、私人进度跟踪或秘密信息。
