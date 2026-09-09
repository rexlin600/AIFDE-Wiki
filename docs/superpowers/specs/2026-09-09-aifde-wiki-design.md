# AIFDE Wiki Design

**Date:** 2026-09-09  
**Status:** Approved for implementation planning  
**Repository:** `AIFDE-Wiki`  
**Primary authoring environment:** Obsidian  
**Primary publishing environment:** Public GitHub repository

## 1. Purpose

`AIFDE-Wiki` is a public knowledge product for software engineers who already have backend or full-stack experience and want to move toward AI application engineering and Forward Deployed Engineering (FDE).

The Wiki must connect five kinds of competence:

1. AI concepts, algorithms, and model fundamentals.
2. LLM, RAG, Agent, multimodal, and related application engineering.
3. Evaluation, security, observability, deployment, and other production concerns.
4. Open-source usage, source-code study, minimal reimplementation, adaptation, and contribution.
5. FDE delivery and interview skills, including ambiguous requirements, enterprise integration, customer communication, system design, and project defense.

The repository is not a personal productivity system. It does not manage private learning tasks, daily notes, personal completion percentages, or a private dashboard.

## 2. Audience

The primary audience is:

- backend or full-stack engineers with established software engineering experience;
- engineers learning production AI rather than pursuing pure model research;
- engineers preparing for AI application engineer, Agent engineer, AI solution engineer, applied AI engineer, or FDE roles;
- the future maintainer, who needs a durable map of concepts, experiments, projects, and sources.

The assumed practice stack is Python first, with Vue and TypeScript as supporting technologies for user interfaces and integration work.

## 3. Design Principles

### 3.1 Public knowledge product first

- GitHub-rendered Markdown is the baseline experience.
- Obsidian enhances authoring and navigation but must not be required to read core content.
- The root `README.md` is the stable public entry point.
- Dataview queries may enhance authoring, but no essential navigation may depend on them.

### 3.2 Broad coverage with intentional depth

The Wiki covers common AI fields and important subdivisions without giving every topic equal weight.

| Depth | Required outcome |
|---|---|
| L1 — Awareness | Explain the principle, use cases, limitations, and relationship to adjacent approaches. |
| L2 — Experiment | Implement or reproduce a minimal experiment and explain important parameters. |
| L3 — Engineering | Integrate the technique into a tested project and justify trade-offs with evidence. |
| L4 — Production/FDE | Deploy, evaluate, monitor, secure, govern, hand off, and defend the design under business constraints. |

Each topic also has one importance classification:

- `core`: expected depth L3 or L4;
- `common`: expected depth L2 or L3;
- `extension`: expected depth L1 unless a project requires more.

LLM application engineering, RAG, Agent systems, evaluation, security, observability, deployment, and FDE delivery are core. Less common or less practical approaches remain visible as extension topics with principles and use cases, but they do not automatically receive a dedicated implementation project.

### 3.3 Evidence over passive completion

A topic is not considered covered merely because a resource was read. Strong content links concepts to one or more forms of evidence:

- a reproducible experiment;
- a minimal reimplementation;
- a production-oriented project;
- a source-code walkthrough;
- an evaluation report;
- an incident or failure analysis;
- an interview answer that withstands follow-up questions.

### 3.4 One canonical note per concept

Cross-domain concepts are linked rather than duplicated. MOCs provide navigation and learning order; canonical notes provide the explanation.

### 3.5 Sources and recency are explicit

- Prefer papers, official documentation, official repositories, and original job descriptions.
- Separate source claims, maintainer interpretation, and experimental findings.
- Record access or verification dates for fast-changing technologies and job-market observations.
- Summarize recruitment material instead of reproducing job descriptions.

## 4. Information Architecture

The Wiki uses a hybrid Map of Content (MOC) model: stable directories define domains, MOCs define relationships and recommended paths, and moderately atomic notes allow reuse.

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

Each major knowledge directory contains a `<Domain>-MOC.md` file. Subdirectories may be added only when the MOC becomes difficult to scan or a stable subdivision has accumulated enough content.

## 5. Note Model

The Wiki uses moderate atomicity: one note answers one independently reusable question, but minor parameters and closely coupled terms remain together.

### 5.1 Note types

| Type | Responsibility |
|---|---|
| `moc` | Define domain scope, topic relationships, recommended order, and links to practice. |
| `concept` | Explain a principle, algorithm, model, or foundational idea. |
| `pattern` | Explain a composable engineering architecture or solution pattern. |
| `experiment` | Record a reproducible hypothesis, setup, variables, metrics, result, and conclusion. |
| `project` | Describe an external GitHub practice project and its delivery evidence. |
| `source` | Analyze a paper, repository, official document, or recruitment sample. |
| `interview` | Record a question, answer framework, common traps, and follow-ups. |
| `decision` | Record a technical choice, alternatives, evidence, and consequences. |
| `retrospective` | Record lessons from a project, experiment set, or major content revision. |

### 5.2 Common properties

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

`maturity` has four values:

- `draft`: useful working content that has not passed the quality checklist;
- `reviewed`: checked against primary sources and internally coherent;
- `stable`: supported by reproducible evidence and suitable as a durable reference;
- `needs-update`: known to require recency or correctness review.

Type-specific properties are added only when useful:

```yaml
# source
source_type: paper
url: https://example.com/source
authors: []
published: 2024-01-01
accessed: 2026-09-09

# project
github: https://github.com/example/project
demo: https://example.com/demo
phase: RAG
tech:
  - Python
  - Vue
  - TypeScript

# experiment
repository: https://github.com/example/project
commit: abc1234
dataset: evaluation-set-v1
metrics:
  - recall_at_10
```

## 6. Naming, Language, and Linking

### 6.1 Language

- Explanations are primarily in Chinese.
- The first use of an important term includes its standard English form.
- Acronyms, product names, and established names remain in English.

Examples:

```text
混合检索 (Hybrid Search).md
重排序 (Reranking).md
上下文工程 (Context Engineering).md
GraphRAG.md
BM25.md
LoRA.md
```

### 6.2 File naming

```text
Domain navigation: RAG-MOC.md
Experiment: EXP-20260909-Chunk-Size-Comparison.md
Project: PRJ-Production-RAG.md
Architecture decision: ADR-001-Vector-Database-Selection.md
Retrospective: RETRO-Production-RAG-V1.md
Paper note: Paper-Self-RAG.md
Repository note: Repo-LangGraph.md
Job sample: Job-Company-Role-20260909.md
```

File names must not contain `/`, `\`, `:`, `?`, `#`, or other characters that reduce cross-platform compatibility.

### 6.3 Linking

- Use standard relative Markdown links for committed internal content so links work in both Obsidian and GitHub: `[混合检索](./Retrieval/混合检索%20(Hybrid%20Search).md)`.
- Configure Obsidian to create Markdown links instead of Wiki Links and to prefer relative paths.
- Use standard Markdown links for external content as well.
- Each knowledge note links to at least one parent MOC.
- Tags describe cross-cutting contexts such as `core`, `extension`, `interview`, or `needs-review`; the `domain` property stores taxonomy.
- Assets live under `99-Assets/`.

## 7. Knowledge Scope

### 7.1 Mathematics and AI foundations

- linear algebra, vectors, matrices, tensors, eigenvalues, and similarity;
- probability, common distributions, Bayesian reasoning, expectation, variance, and uncertainty;
- gradients, chain rule, optimization, numerical stability, and automatic differentiation;
- entropy, cross-entropy, KL divergence, and information-theoretic intuition.

### 7.2 Traditional machine learning

- regression and classification;
- trees, random forests, gradient boosting, and ensemble methods;
- clustering, dimensionality reduction, and anomaly detection;
- recommendation and time-series fundamentals;
- feature engineering, imbalance, leakage, calibration, validation, and metric selection.

### 7.3 Deep learning

- MLPs, backpropagation, initialization, optimization, and regularization;
- CNNs, RNNs, LSTMs, attention, Transformers, and embeddings;
- PyTorch tensors, autograd, datasets, training loops, evaluation, and model serialization.

### 7.4 NLP and LLM engineering

- tokenization, embeddings, language-model objectives, and Transformer architecture;
- pretraining, supervised fine-tuning, PEFT/LoRA, RLHF, DPO, distillation, and model adaptation;
- sampling, reasoning behavior, context windows, KV cache, quantization, batching, and inference economics;
- prompt engineering, context engineering, structured outputs, function calling, and model selection;
- hallucination, uncertainty, grounding, and model limitations.

### 7.5 RAG

RAG is treated as a composable design space rather than a single vector-search pipeline.

- naive and modular RAG;
- sparse, dense, and hybrid retrieval;
- metadata filtering, reranking, parent-child retrieval, and small-to-big retrieval;
- query rewriting, multi-query, decomposition, routing, and HyDE;
- conversational, multi-hop, adaptive, and iterative RAG;
- Corrective RAG and Self-RAG;
- Agentic RAG/Agent RAG;
- GraphRAG and knowledge-graph RAG;
- hierarchical RAG and RAPTOR;
- SQL and structured-data RAG;
- multimodal RAG;
- permission-aware, multi-tenant, temporal, and streaming RAG;
- indexing, retrieval, generation, citation, and end-to-end evaluation;
- trade-offs among RAG, long context, tools, and fine-tuning.

These labels are not assumed to be mutually exclusive. Notes must explain possible compositions, operating cost, failure modes, and selection criteria.

### 7.6 Agent systems

- workflow versus Agent boundaries;
- ReAct, plan-and-execute, reflection, and routing patterns;
- tools, schemas, state, memory, sessions, and context management;
- human approval, escalation, retries, recovery, and idempotency;
- single-Agent, supervisor, hierarchical, and multi-Agent patterns;
- MCP, A2A, and enterprise tool integration;
- browser, code, data, and workflow Agents;
- trace evaluation, security boundaries, and runaway cost control.

### 7.7 Multimodal and adjacent AI domains

- computer vision, OCR, and document intelligence;
- speech recognition, speech synthesis, and voice Agents;
- vision-language models and multimodal retrieval;
- recommendation, forecasting, optimization, robotics, expert systems, evolutionary algorithms, and generative models.

The last group is primarily a breadth map. Topics move beyond L1 only when they are common in FDE work or required by a selected project.

### 7.8 Production AI

- data ingestion, ETL/ELT, quality, lineage, and governance;
- model gateways, provider abstraction, routing, fallback, caching, rate limiting, and secret management;
- offline, online, retrieval, generation, and Agent evaluation;
- LLM-as-judge design, calibration, datasets, regression tests, and evaluation in CI;
- tracing, logs, metrics, feedback loops, cost, latency, and reliability;
- model serving, vLLM, containers, Kubernetes, CI/CD, rollbacks, and capacity planning;
- API design, asynchronous workflows, queues, and enterprise integration.

### 7.9 AI safety and governance

- prompt injection, indirect injection, data exfiltration, excessive agency, and unsafe tool use;
- knowledge-base poisoning, insecure output handling, and supply-chain risk;
- authentication, authorization, least privilege, isolation, auditability, and human review;
- PII, data residency, retention, compliance, red-team testing, and incident response.

### 7.10 FDE practice

- technical discovery and workflow mapping;
- translating ambiguous business goals into measurable outcomes;
- PoC scope, acceptance criteria, ROI, and launch readiness;
- legacy systems, APIs, data platforms, identity, VPC, hybrid, and on-premises integration;
- stakeholder communication, demos, changing requirements, and incident handling;
- production handoff, runbooks, adoption, feedback, and reusable delivery primitives.

### 7.11 Interview preparation

- practical Python coding and data manipulation;
- AI, ML, LLM, RAG, Agent, evaluation, and security fundamentals;
- AI system design under cost, latency, data, privacy, and deployment constraints;
- project deep dives, architecture trade-offs, failure analysis, and metrics;
- ambiguous customer cases, scope negotiation, live debugging, and behavioral stories.

## 8. Learning Roadmap

The roadmap is a recommendation, not a deadline. Estimates assume five to ten hours per week.

| Phase | Suggested duration | Main outcome |
|---|---:|---|
| 0. Baseline and environment | 1–2 weeks | Establish the AI engineering toolchain, Wiki conventions, and a small model/API baseline. |
| 1. AI/ML foundations | 6–8 weeks | Understand necessary mathematics, classical ML, deep learning, PyTorch, metrics, and data failure modes. |
| 2. LLM engineering | 6–8 weeks | Explain and experiment with Transformer behavior, prompting, structured output, adaptation, inference, and model APIs. |
| 3. RAG engineering | 8–12 weeks | Build and evaluate a production-oriented RAG system and compare representative retrieval architectures. |
| 4. Agent engineering | 8–12 weeks | Build reliable tool-using workflows with state, memory, approval, recovery, tracing, and evaluation. |
| 5. Production AI | 6–10 weeks | Harden earlier systems with security, observability, cost, deployment, CI/CD, and operational evidence. |
| 6. FDE capstone | 8–12 weeks | Deliver an end-to-end customer-style AI system from discovery through production handoff. |

Every phase connects:

```text
concept -> minimal experiment -> open-source study/reimplementation
        -> production project increment -> evaluation/failure review
        -> interview explanation -> Wiki synthesis
```

The roadmap does not contain a separate late open-source phase. Open-source work and interview preparation run horizontally through all phases.

## 9. Open-Source Practice

Each relevant phase follows four levels of open-source engagement:

1. **Use and evaluate:** run the project, document setup, architecture, strengths, constraints, and operational behavior.
2. **Trace and explain:** follow one meaningful call path or subsystem through the source.
3. **Reimplement:** build a minimal independent version of the core mechanism to validate understanding.
4. **Adapt or contribute:** make a useful change, publish a comparison, report a well-researched issue, or contribute documentation, tests, a bug fix, or a feature when a genuine opportunity exists.

Representative study targets include:

| Domain | Representative projects | Reimplementation target |
|---|---|---|
| AI/ML | scikit-learn, PyTorch | Core models, backpropagation, and training loops. |
| LLM | Transformers, nanoGPT, OpenAI Cookbook | Tokenizer, attention, simplified Transformer, and model call layer. |
| RAG | LlamaIndex, RAGFlow, GraphRAG, pgvector, Qdrant | Ingestion, hybrid retrieval, reranking, evaluation, and one advanced RAG method. |
| Agent | LangGraph, OpenAI Agents SDK, MCP Servers | Agent loop, tool registry, state, memory, approvals, and recovery. |
| Production | LiteLLM, vLLM, DeepEval, promptfoo | Gateway, routing/fallback, evaluation runner, tracing, and security tests. |
| End-to-end | Dify, RAGFlow | Architecture study followed by an independently designed customer solution. |

Every repository study note records its license. Reimplementations explicitly name their inspiration and distinguish learning replicas from original product work.

## 10. Project Model

Practice code lives in separate GitHub repositories. The Wiki contains project dossiers, not duplicate source trees.

Each project dossier contains:

1. Business problem and intended user.
2. Success metrics and acceptance criteria.
3. Constraints, assumptions, and discovery questions.
4. Architecture and key decisions.
5. Links to repository, demo, API documentation, issues, commits, and releases.
6. Dataset and evaluation design.
7. Quality, cost, latency, safety, and reliability results.
8. Failures, incidents, and improvements.
9. Interview explanation and likely follow-ups.
10. Reusable components and open-source opportunities.

Recommended project progression:

- `ai-foundations-labs`;
- `llm-engineering-lab`;
- `production-rag-system`;
- `enterprise-workflow-agent`;
- production hardening of the RAG or Agent system;
- one independent FDE capstone repository.

## 11. Job-Market and Interview Evidence

Job research must search beyond the literal `FDE` title. Relevant titles include:

- Forward Deployed Engineer;
- Forward Deployed AI Engineer;
- Applied AI Engineer;
- AI Application Engineer;
- Agent Engineer;
- AI Solution Engineer;
- customer engineer and solution architect roles with substantial hands-on AI delivery.

The job corpus includes official company career pages, BOSS Zhipin, and other recruitment platforms. Each sample records company, title, location, seniority, responsibilities, required skills, source URL, and access date. Automated access failures are documented; unverified search snippets are not treated as job-description evidence.

Current role samples show a recurring combination of end-to-end deployment ownership, Python and production software engineering, RAG and Agent systems, evaluation, enterprise data and API integration, cloud or hybrid deployment, security and governance, and direct work with customer stakeholders. Representative sources reviewed for this design include:

- [OpenAI — Forward Deployed Engineer, Healthcare](https://openai.com/careers/forward-deployed-engineer-%28fde%29-healthcare-sf-san-francisco/)
- [NextLink Labs — Forward Deployed Engineer, AI](https://jobs.ashbyhq.com/nextlinklabs/cb0bf55f-055a-489e-b982-4aa321036423/)
- [Hippocratic AI — Forward Deployed Engineer](https://jobs.ashbyhq.com/hippocratic%20ai/af528529-1c4b-4cc4-b073-4e4522fd2ab6)
- [Nextdata — Forward Deployed Engineer](https://jobs.ashbyhq.com/nextdata/4feeb725-13e9-440b-984b-b173f943317b)

Interview material is organized by capability rather than by memorized answer lists:

- practical coding and debugging;
- data and AI system design;
- LLM/RAG/Agent depth;
- production reliability, evaluation, safety, and governance;
- project deep dive;
- customer discovery, ambiguity, prioritization, and communication.

## 12. Public Repository Experience

### 12.1 Root README

The root `README.md` contains:

1. Wiki purpose and audience.
2. AI knowledge map.
3. FDE competency model.
4. Recommended learning roadmap.
5. Domain navigation.
6. Representative experiments and projects.
7. Open-source studies.
8. Interview preparation.
9. Content status, licenses, and contribution links.

There is no personal dashboard or personal progress percentage.

### 12.2 Obsidian plugins

The default setup is intentionally light:

- Templater for consistent note creation;
- Linter for Markdown and property formatting;
- Dataview as an optional authoring aid only;
- Obsidian Git as an optional interface for contributors who do not use command-line Git.

Tasks is not included because the repository does not manage personal learning work.

### 12.3 Version control

- The repository is public on GitHub.
- Normal content updates may go directly to `main`.
- Structural changes, template changes, and large content rewrites use branches and pull requests.
- Commits describe concrete content outcomes, such as `docs(rag): explain hybrid retrieval trade-offs`.
- Device-specific workspace state, caches, trash, environment files, secrets, and private data are ignored.
- Reusable Obsidian configuration, plugin identifiers, templates, and public content are committed.

## 13. Quality and Maintenance

### 13.1 Minimum note quality

A reviewed note:

- answers a clear question;
- declares domain, importance, depth, maturity, and dates;
- explains where the technique fits and does not fit;
- cites reliable sources for important claims;
- separates sourced claims, interpretation, and experimental evidence;
- includes an example, experiment, or project link when the topic is core;
- links to at least one MOC and relevant adjacent concepts;
- contains no private, secret, or unlicensed copied content.

### 13.2 Maintenance mechanisms

- `CHANGELOG.md` records major taxonomy, roadmap, and content changes.
- GitHub Issues track missing subjects, errors, broken links, and proposals.
- `last_verified` flags time-sensitive material.
- Recruitment observations are resampled at least quarterly when maintained actively.
- Major framework or model changes trigger review of affected MOCs and notes.

### 13.3 Automated checks

The implementation should add lightweight GitHub Actions for:

- Markdown formatting;
- YAML property validation;
- internal and external link checking;
- secret scanning;
- optional Chinese and English spelling checks after the initial corpus stabilizes.

## 14. Licensing and Public-Safety Rules

- Original prose and diagrams use Creative Commons Attribution 4.0 (`CC BY 4.0`).
- Original executable code snippets use the MIT License.
- Third-party material remains under its original license and is attributed.
- Job descriptions are summarized and linked rather than republished.
- Paid books, courses, interview banks, and proprietary materials are not reproduced.
- Project retrospectives must not expose former-employer, customer, credential, or private-system information.

## 15. Initial Source Set

The following primary sources establish initial anchors. They are starting points, not a frozen dependency list:

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
- [Self-RAG paper](https://arxiv.org/abs/2310.11511)
- [Corrective RAG paper](https://arxiv.org/abs/2401.15884)
- [RAPTOR paper](https://arxiv.org/abs/2401.18059)

## 16. Implementation Boundaries

The first implementation establishes the repository skeleton, conventions, templates, navigation, validation, and roadmap. It does not attempt to write the entire AI corpus in one pass.

Initial content must be sufficient to demonstrate every content type and validate the navigation model. Subsequent content should be added incrementally by domain and phase, with each increment remaining readable on GitHub and linked from its MOC.

## 17. Design Acceptance Criteria

The design is implemented successfully when:

1. A GitHub visitor can understand the purpose, audience, knowledge scope, and recommended learning path from the root README.
2. Every major AI/FDE domain has a discoverable MOC and declared depth expectations.
3. The repository includes usable templates for all nine note types.
4. Internal navigation works in both Obsidian and GitHub without requiring Dataview.
5. A representative concept, experiment, project, source, interview, decision, and retrospective demonstrates the content model.
6. GitHub project dossiers link cleanly to external practice repositories and evidence.
7. Open-source study is embedded into roadmap phases through use, tracing, reimplementation, and optional contribution.
8. Automated checks catch malformed properties, broken links, Markdown issues, and accidental secrets.
9. Licensing, attribution, and public-safety rules are visible and enforceable through contribution guidance.
10. No personal dashboard, daily notes, private progress tracking, or secret material is part of the public knowledge product.
