# RAG Content Implementation Plan

<!-- markdownlint-disable MD013 MD032 -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `K-检索增强生成 RAG` 建设为包含 38 篇独立主题笔记、覆盖数据进入到评测治理完整链路的知识体系。

**Architecture:** 以 RAG 生命周期为主线，将数据与基础检索、查询与上下文、高级 RAG、生产治理、评测决策拆成可独立审查的批次。每篇使用真实 AI 应用、机制推导、最小实验、指标和排错组织，MOC 同时提供生命周期、故障和方案决策入口。

**Tech Stack:** Markdown、YAML Front Matter、Python 3、NumPy、标准库内存索引与图、markdownlint-cli2

## Global Constraints

- 文件名、深度和重要程度严格使用设计稿 `docs/superpowers/specs/2026-09-10-rag-content-design.md`。
- 新主题使用 `type: concept`、`domain: [RAG]`、`maturity: draft` 和核验日期 `2026-09-10`。
- 每篇至少一个无需网络、付费 API、数据库服务或模型下载的可执行 Python 实验。
- 数学符号首次出现时解释，公式配逐步推导和可人工复核的手算。
- 每篇包含真实 AI 应用价值、简单基线、链路位置、结果边界、质量、延迟、成本、权限、安全、固定排错表、复述检查和自检。
- 排错表头固定为 `| 现象 | 可能原因 | 优先检查 |`。
- 实验含正常与失败分支断言；随机实验固定种子；不得把模拟结果描述为真实业务结果。
- LLM、Agent、多模态、生产级 AI 和安全治理只建立边界链接，不重复相邻目录完整内容。
- 当前算法或工具行为只引用论文或官方文档，所有来源写明访问日期 `2026-09-10`。

---

### Task 1: 重建导航和统一现有内容

**Files:**
- Modify: `K-检索增强生成 RAG/00-检索增强生成 RAG-MOC.md`
- Verify: `K-检索增强生成 RAG/01-EXP-20260909-检索基线.md`
- Modify: `K-检索增强生成 RAG/02-混合检索 Hybrid Search.md`

**Interfaces:**
- Consumes: 设计稿 38 个主题文件名与相邻领域边界。
- Produces: 生命周期、故障、方法决策和学习深度四种直接导航；统一 Hybrid 主题。

- [ ] **Step 1: 重写 MOC 导航**

MOC 直接链接 02 至 39，并保留检索基线实验入口；生命周期覆盖数据、索引、查询、召回、排序、上下文、生成、评测和运行。

- [ ] **Step 2: 重写 Hybrid 主题**

实现 BM25 与 Dense 排名的 RRF，推导 $\sum_i1/(k+rank_i)$，手算融合名次，代码断言异构原始分数未被直接相加。

- [ ] **Step 3: 核验实验协议**

只修正日期、断链或与统一术语冲突之处，不伪造未运行结果、仓库或 Commit。

- [ ] **Step 4: 验证导航**

Run: 本地 Markdown 链接扫描。

Expected: MOC 直接链接 38/38 主题和实验协议，相邻领域链接可解析。

### Task 2: 完成数据和基础检索

**Files:**
- Create: `K-检索增强生成 RAG/03-RAG 数据摄取.md`
- Create: `K-检索增强生成 RAG/04-RAG 文档解析.md`
- Create: `K-检索增强生成 RAG/05-RAG 文档清洗.md`
- Create: `K-检索增强生成 RAG/06-RAG 文档切分.md`
- Create: `K-检索增强生成 RAG/07-RAG 元数据.md`
- Create: `K-检索增强生成 RAG/08-BM25 稀疏检索.md`
- Create: `K-检索增强生成 RAG/09-Dense 向量检索.md`
- Create: `K-检索增强生成 RAG/10-RAG 向量索引.md`
- Create: `K-检索增强生成 RAG/11-RAG 重排序.md`

**Interfaces:**
- Consumes: 原始文档、来源身份、版本、权限、查询和相关性标注。
- Produces: 可追踪 Chunk、Sparse 和 Dense 候选、融合输入与精排候选。

- [ ] **Step 1: 完成数据生命周期笔记**

摄取实验验证内容哈希与幂等；解析实验保留标题和页码；清洗实验去除模板并防止正文误删；切分实验比较固定长度、句子边界和重叠；元数据实验执行类型、时间和权限过滤。

- [ ] **Step 2: 完成 Sparse 与 Dense 检索**

BM25 推导 TF 饱和、IDF 和长度归一化并手算排名；Dense 推导余弦、双编码器对比损失和困难负例，使用小型 NumPy 向量验证相似度。

- [ ] **Step 3: 完成向量索引与重排序**

向量索引对照精确搜索和受限候选近似搜索，计算 Recall@k；重排序证明只能改变候选顺序，不能召回缺失文档，并评测候选窗口。

- [ ] **Step 4: 执行本批代码**

Run: 隔离环境逐块执行 03 至 11。

Expected: 幂等、结构保留、切分覆盖、权限过滤、BM25、相似度、ANN 召回和排序上限断言全部通过。

### Task 3: 完成查询理解和上下文

**Files:**
- Create: `K-检索增强生成 RAG/12-父子文档检索.md`
- Create: `K-检索增强生成 RAG/13-RAG 查询改写.md`
- Create: `K-检索增强生成 RAG/14-RAG 多查询检索.md`
- Create: `K-检索增强生成 RAG/15-RAG 查询分解.md`
- Create: `K-检索增强生成 RAG/16-RAG 检索路由.md`
- Create: `K-检索增强生成 RAG/17-HyDE 假设文档检索.md`
- Create: `K-检索增强生成 RAG/18-多轮对话检索.md`
- Create: `K-检索增强生成 RAG/19-RAG 多跳检索.md`
- Create: `K-检索增强生成 RAG/35-RAG 上下文构建.md`

**Interfaces:**
- Consumes: 用户查询、会话、数据源描述和基础检索候选。
- Produces: 保持意图的检索查询、证据链和受 Token 预算约束的上下文。

- [ ] **Step 1: 完成检索粒度和查询变换**

父子文档实验区分检索 ID 与返回上下文；改写、多查询和 HyDE 均保留实体、否定与权限条件，并对漂移分支断言。

- [ ] **Step 2: 完成分解和路由**

查询分解显式表示子问题依赖；路由对数据源与检索器设置白名单、置信阈值和回退，不让生成文本直接选择越权源。

- [ ] **Step 3: 完成多轮和多跳**

多轮检索解析指代但隔离其他会话；多跳使用中间实体连接证据，记录来源并在缺证时停止。

- [ ] **Step 4: 完成上下文构建**

推导 `系统 + 查询 + 证据 + 输出 <= 窗口`，执行权限过滤、去重、排序、压缩和预算分配，保留引用映射。

- [ ] **Step 5: 执行本批代码**

Run: 隔离环境逐块执行 12 至 19 和 35。

Expected: 父子映射、意图约束、查询去重、依赖排序、路由回退、会话隔离、多跳终止和预算断言通过。

### Task 4: 完成高级 RAG

**Files:**
- Create: `K-检索增强生成 RAG/20-RAG 自适应检索.md`
- Create: `K-检索增强生成 RAG/21-RAG 迭代检索.md`
- Create: `K-检索增强生成 RAG/22-RAG 纠错检索.md`
- Create: `K-检索增强生成 RAG/23-Self-RAG 自反思检索.md`
- Create: `K-检索增强生成 RAG/24-Agentic RAG.md`
- Create: `K-检索增强生成 RAG/25-GraphRAG.md`
- Create: `K-检索增强生成 RAG/26-知识图谱 RAG.md`
- Create: `K-检索增强生成 RAG/27-RAG 层级检索.md`
- Create: `K-检索增强生成 RAG/28-RAPTOR 递归检索.md`

**Interfaces:**
- Consumes: 基础检索、查询状态、证据质量和小型文本图或层级树。
- Produces: 有显式预算、终止原因和可消融证据的复杂检索策略。

- [ ] **Step 1: 完成自适应、迭代和纠错**

自适应检索分类无需检索、单次检索和深检索；迭代与纠错使用有限状态机，显式计算最大查询数和延迟上界。

- [ ] **Step 2: 完成 Self-RAG 与 Agentic RAG**

用离散反思标签模拟检索必要性和证据支持度；Agentic RAG 实现规划、授权检索、观察、停止状态机，限制步数与数据源。

- [ ] **Step 3: 完成图和层级方法**

GraphRAG 区分局部实体与全局主题；知识图谱 RAG 显式执行图查询；层级检索和 RAPTOR 对照树遍历、摘要误差和更新成本。

- [ ] **Step 4: 执行本批代码**

Run: 隔离环境逐块执行 20 至 28。

Expected: 路径选择、最大步数、换源、支持度、工具授权、图遍历和树检索断言通过。

### Task 5: 完成数据形态和生产治理

**Files:**
- Create: `K-检索增强生成 RAG/29-结构化数据 RAG.md`
- Create: `K-检索增强生成 RAG/30-多模态 RAG.md`
- Create: `K-检索增强生成 RAG/31-RAG 权限控制.md`
- Create: `K-检索增强生成 RAG/32-RAG 多租户隔离.md`
- Create: `K-检索增强生成 RAG/33-RAG 知识时效.md`
- Create: `K-检索增强生成 RAG/34-RAG 流式更新.md`
- Create: `K-检索增强生成 RAG/36-RAG 引用生成.md`

**Interfaces:**
- Consumes: 表格、图文页面、身份与租户、版本事件、带来源 Chunk 和模型主张。
- Produces: 经过授权与时效过滤的证据、可恢复索引状态和主张级引用。

- [ ] **Step 1: 完成结构化与多模态数据**

结构化主题区分查询生成与数据库执行，使用只读白名单模拟；多模态主题保留页码、区域、模态和 OCR 来源，验证跨模态引用。

- [ ] **Step 2: 完成权限和租户隔离**

权限必须在候选生成前或候选读取边界内生效；多租户实验覆盖索引、缓存键、日志和配额，断言跨租户不可见。

- [ ] **Step 3: 完成时效和流式更新**

按 `valid_from`、`valid_to` 和版本选择证据；增量事件含幂等键、顺序、墓碑删除和重建对账。

- [ ] **Step 4: 完成引用生成**

将答案拆成主张，计算引用覆盖率与归属正确率，区分链接存在、来源可打开和来源支持主张。

- [ ] **Step 5: 执行本批代码**

Run: 隔离环境逐块执行 29 至 34 和 36。

Expected: 只读约束、区域映射、越权拒绝、租户隔离、版本过滤、事件幂等和主张引用断言通过。

### Task 6: 完成评测和方案决策

**Files:**
- Create: `K-检索增强生成 RAG/37-RAG 检索评测.md`
- Create: `K-检索增强生成 RAG/38-RAG 生成评测.md`
- Create: `K-检索增强生成 RAG/39-RAG 方案选型.md`

**Interfaces:**
- Consumes: 排名列表、qrels、答案、证据、引用、延迟、成本和业务约束。
- Produces: 分层指标、错误归因、消融证据和 RAG 方案选择。

- [ ] **Step 1: 完成检索评测**

手算并实现 Recall@k、MRR 和 nDCG@k，说明不完整 qrels、查询切片、置信区间和测试集封存。

- [ ] **Step 2: 完成生成评测**

区分答案正确、证据 Faithfulness、引用覆盖、不可回答拒答和端到端任务成功，加入人工评审一致性。

- [ ] **Step 3: 完成方案选型**

先用权限、时效、可引用、延迟和成本硬约束筛选，再比较 RAG、长上下文、工具和微调；代码执行加权敏感性与方案消融。

- [ ] **Step 4: 执行本批代码**

Run: 隔离环境逐块执行 37 至 39。

Expected: 指标手算、主张支持、拒答和权重敏感性断言通过。

### Task 7: 全目录验收

**Files:**
- Verify: `K-检索增强生成 RAG/*.md`

**Interfaces:**
- Consumes: MOC、38 篇主题和检索基线实验。
- Produces: 可提交的完整 RAG 知识目录。

- [ ] **Step 1: 运行结构和链接检查**

Run: 自定义 Python 扫描 Front Matter、一级标题、必需职责、固定排错表、代码块、MOC 直接链接和本地链接。

Expected: 38/38 主题通过，实验协议保持未运行边界。

- [ ] **Step 2: 运行全部 Python 代码块**

Run: 使用行首 Fence 解析器，在隔离 Python 环境逐文件、逐代码块独立执行。

Expected: 所有断言通过，无 RuntimeWarning、NaN 或异常退出。

- [ ] **Step 3: 运行 Markdown 和补丁检查**

Run: `npx --yes markdownlint-cli2 'K-检索增强生成 RAG/*.md' && git diff --check`

Expected: 0 errors。

- [ ] **Step 4: 交叉审查**

逐批复核公式分母、边界条件、手算与代码一致性、实验是否支持结论、权限是否在检索边界内，以及高级方法是否给出静态基线。

- [ ] **Step 5: 提交内容**

Run: `git add 'K-检索增强生成 RAG' && git commit -m 'docs: 补全检索增强生成 RAG 主题内容'`

Expected: 提交成功，工作区干净。
