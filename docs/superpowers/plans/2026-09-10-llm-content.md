# LLM Content Implementation Plan

<!-- markdownlint-disable MD001 MD013 MD032 MD036 -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `J-大模型 LLM` 建设为包含 20 篇独立主题笔记、贯通模型机制、应用可靠性、适配训练和推理交付的知识体系。

**Architecture:** 以 LLM 生命周期为主线，从 Token、Embedding、预训练和自回归生成进入 Prompt、Context、结构化输出、工具与幻觉，再扩展到微调、偏好优化、量化、服务和从头训练。每篇以真实应用、机制推导、最小实验、评测和排错组成，MOC 同时提供生命周期、问题决策和故障现象三种入口。

**Tech Stack:** Markdown、YAML Front Matter、Python 3、NumPy、PyTorch、JSON Schema 思维、markdownlint-cli2

## Global Constraints

- 文件名、标题、深度和重要程度严格使用设计稿清单。
- 每篇使用 `type: concept`、`domain: [LLM]`、`maturity: draft` 和核验日期 `2026-09-10`。
- 每篇至少一个无需网络和付费 API 的可执行 Python 实验，并固定随机种子。
- 机制主题使用 NumPy 或 PyTorch；接口主题使用标准库模拟 Schema、重试和状态流。
- 每篇包含应用价值、链路位置、基线、公式或状态推导、手算、结果解释、成本延迟、安全、排错和适用边界。
- Transformer 基础链接深度学习；RAG、Agent 和生产平台内容只建立边界链接。
- 当前 API 只依赖官方文档，机制优先引用原始论文。

---

### Task 1: 重建 LLM 导航

**Files:**
- Modify: `J-大模型 LLM/00-大模型 LLM-MOC.md`

**Interfaces:**
- Consumes: 20 个主题文件名和 LLM 生命周期边界。
- Produces: 生命周期、问题决策和故障现象三类直接导航。

- [ ] **Step 1: 写入三类导航**

生命周期覆盖输入、训练、生成、应用、适配和交付；问题决策覆盖 Prompt、RAG、工具、微调和换模型；故障导航覆盖截断、格式失败、幻觉、延迟、OOM 和成本异常。

- [ ] **Step 2: 验证边界链接**

Run: `python3` 本地链接扫描脚本。

Expected: MOC 直接链接全部 20 篇，并能进入深度学习、RAG、Agent 和生产 AI。

### Task 2: 完成模型输入与生成机制

**Files:**
- Modify: `J-大模型 LLM/01-词元化 Tokenization.md`
- Create: `J-大模型 LLM/02-文本 Embedding.md`
- Create: `J-大模型 LLM/03-大模型预训练目标.md`
- Create: `J-大模型 LLM/04-大模型自回归 Transformer.md`
- Create: `J-大模型 LLM/13-大模型生成采样.md`
- Create: `J-大模型 LLM/14-大模型 KV Cache.md`

**Interfaces:**
- Consumes: 深度学习目录中的 Attention、Transformer、反向传播和批处理。
- Produces: Token 序列、向量、Logits、概率、生成循环和缓存成本的统一语言。

- [ ] **Step 1: 完成 Tokenizer 与 Embedding**

用中英文、代码和 JSON 解释词元成本；手算 BPE 合并、Embedding 查表、池化和余弦相似度，区分 Token Embedding、句向量和输出投影。

- [ ] **Step 2: 完成预训练与自回归 Transformer**

推导标签右移、交叉熵、困惑度和因果 Mask，用最小张量证明未来不可见，并说明数据混合、重复、版权和评测污染。

- [ ] **Step 3: 完成采样与 KV Cache**

实现 Temperature、top-k、top-p、停止条件和随机种子；对照完整解码与缓存解码，推导缓存形状和字节数，区分 Prefill 与 Decode。

- [ ] **Step 4: 执行本批代码**

Run: 隔离环境逐块执行 6 篇代码。

Expected: 合并、查表、概率归一化、因果断言、采样约束和缓存等价性全部通过。

### Task 3: 完成应用可靠性主题

**Files:**
- Create: `J-大模型 LLM/05-大模型提示设计.md`
- Create: `J-大模型 LLM/06-大模型上下文工程.md`
- Create: `J-大模型 LLM/07-大模型结构化输出.md`
- Create: `J-大模型 LLM/08-大模型工具调用.md`
- Create: `J-大模型 LLM/09-大模型幻觉.md`
- Create: `J-大模型 LLM/10-大模型选型.md`

**Interfaces:**
- Consumes: Task 2 的 Token 预算、生成概率和停止条件。
- Produces: 可版本化 Prompt、上下文装配、Schema 边界、工具状态机、错误分类和选型证据。

- [ ] **Step 1: 完成 Prompt 与 Context**

以客服抽取为案例，定义系统与用户指令、Few-shot、模板变量、Token 预算、信息排序、截断和污染；实验验证模板版本及预算分配。

- [ ] **Step 2: 完成结构化输出与工具调用**

实现 JSON 解析、字段类型与范围校验、有限修复、重试和降级；工具调用使用“模型提议、程序校验、授权执行、结果回填”的状态机。

- [ ] **Step 3: 完成幻觉与模型选型**

建立可回答性、事实性、引用支持和拒答分类；用固定评测矩阵比较质量、延迟、成本、上下文、隐私、许可和供应商风险。

- [ ] **Step 4: 执行本批代码**

Run: 执行模板、预算、Schema、工具状态、错误分类和加权选型实验。

Expected: 正常与失败分支均有断言，重试有上限，选型结果能随权重变化而解释。

### Task 4: 完成适配与对齐主题

**Files:**
- Create: `J-大模型 LLM/11-大模型监督微调 SFT.md`
- Create: `J-大模型 LLM/12-LoRA 参数高效微调.md`
- Create: `J-大模型 LLM/17-RLHF 与 DPO.md`
- Create: `J-大模型 LLM/18-大模型蒸馏.md`

**Interfaces:**
- Consumes: 预训练交叉熵、训练验证拆分和 PyTorch 参数更新。
- Produces: 训练数据格式、低秩更新、偏好目标和教师学生迁移的选择边界。

- [ ] **Step 1: 完成 SFT 与 LoRA**

解释消息模板、只对回答 Token 计损失、灾难性遗忘和数据切分；推导 $\Delta W=BA$、参数量和缩放，并用 PyTorch 验证只有适配参数更新。

- [ ] **Step 2: 完成 RLHF 与 DPO**

从偏好对进入奖励建模、策略优化和 DPO 目标，手算一对偏好样本的 Log-Sigmoid，说明参考模型、KL 约束和奖励投机。

- [ ] **Step 3: 完成蒸馏**

推导带温度的软标签、$T^2$ 梯度尺度和教师学生损失，区分 Logits 蒸馏、响应蒸馏与能力评测污染。

- [ ] **Step 4: 执行本批代码**

Run: 执行标签 Mask、LoRA 等价、DPO 损失和蒸馏温度实验。

Expected: 参数量、梯度范围、偏好方向和软标签概率均满足断言。

### Task 5: 完成推理交付与规模扩展

**Files:**
- Create: `J-大模型 LLM/15-大模型量化.md`
- Create: `J-大模型 LLM/16-大模型服务.md`
- Create: `J-大模型 LLM/19-大模型从头预训练.md`
- Create: `J-大模型 LLM/20-稀疏模型与长上下文.md`

**Interfaces:**
- Consumes: 模型权重、Token 序列、KV Cache、检查点和评测矩阵。
- Produces: 量化误差、服务延迟、训练预算、MoE 路由和长上下文验证方法。

- [ ] **Step 1: 完成量化与服务**

推导对称量化的 scale、舍入和反量化；实现离散事件服务模拟，区分首 Token 延迟、逐 Token 延迟、吞吐、批处理、排队和超时。

- [ ] **Step 2: 完成从头预训练**

说明数据治理、Tokenizer、Token 预算、计算估算、分布式训练、检查点和小规模试跑；不把单次训练损失下降当成语言能力证据。

- [ ] **Step 3: 完成稀疏与长上下文**

推导 Top-k MoE 路由、负载均衡和稀疏 Attention 复杂度；区分窗口支持、位置外推、信息检索和长上下文实际利用率。

- [ ] **Step 4: 执行本批代码**

Run: 执行量化误差、批处理队列、训练预算、MoE 路由和长上下文检索实验。

Expected: 数值、容量和复杂度计算通过，结论不依赖 GPU 或远程模型。

### Task 6: 全目录验收

**Files:**
- Verify: `J-大模型 LLM/*.md`

**Interfaces:**
- Consumes: MOC 和全部 20 篇主题。
- Produces: 可提交的完整 LLM 知识目录。

- [ ] **Step 1: 运行结构与链接检查**

Run: 自定义 Python 扫描 Front Matter、标题、必需职责、排错表、代码块、MOC 直接链接和本地链接。

Expected: 20/20 通过。

- [ ] **Step 2: 运行全部代码块**

Run: 在隔离 Python 环境逐文件、逐代码块独立执行。

Expected: 所有代码块无异常退出，输出符合正文声明。

- [ ] **Step 3: 运行 Markdown 和补丁检查**

Run: `npx --yes markdownlint-cli2 'J-大模型 LLM/*.md' && git diff --check`

Expected: 0 errors。

- [ ] **Step 4: 提交内容**

Run: `git add 'J-大模型 LLM' docs/superpowers/plans/2026-09-10-llm-content.md && git commit -m 'docs: 补全大模型 LLM 主题内容'`

Expected: 提交成功，工作区干净。
