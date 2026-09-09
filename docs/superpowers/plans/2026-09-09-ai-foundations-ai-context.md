# AI Foundations AI Context Implementation Plan

<!-- markdownlint-disable MD013 MD032 -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 AI 基础 MOC 和 13 篇概念笔记从数学学科叙事重构为 AI 训练链路贯穿式叙事。

**Architecture:** MOC 同时提供 AI 训练链路和数学依赖两种入口。每篇笔记保留已验证的数学推导，以一个 AI 核心问题和贯穿案例重新组织开头、公式解释、实验、排错与学习收益。

**Tech Stack:** GitHub Markdown、YAML Front Matter、LaTeX、Python 3.12、NumPy、markdownlint-cli2。

## Global Constraints

- 每篇前 20% 内容必须出现真实 AI 对象。
- 每篇明确训练链路位置、上游输入和下游输出。
- 每篇使用设计稿指定的 AI 案例贯穿问题、变量、推导和验证。
- 核心公式必须把符号映射到模型、数据、参数、预测或损失。
- NumPy 实验必须输出 AI 相关结果，并保持可独立执行。
- 每篇必须包含“现象 → 可能原因 → 优先检查”的工程排错表。
- 每篇结尾必须说明能够解释、实现和排查什么。
- 已有数学结论、低门槛表达、来源、主题名和 Front Matter 枚举保持正确。

---

### Task 1: 重构 MOC 双入口导航

**Files:**
- Modify: `G-AI 基础/00-AI 基础-MOC.md`

**Interfaces:**
- Consumes: 设计稿中的统一训练链路和 13 个主题映射。
- Produces: 按 AI 工程现象查阅和按数学依赖学习的两个稳定入口。

- [ ] **Step 1: 增加 AI 价值和训练链路**

在领域边界后加入数据、表示、前向、损失、梯度、优化和决策链路，并解释每个环节失败时对应的数学主题。

- [ ] **Step 2: 增加双路线表格**

提供按训练链路查阅表和按依赖学习顺序，链接现有 13 篇笔记。

- [ ] **Step 3: 检查 MOC**

Run: `npx --yes markdownlint-cli2 'G-AI 基础/00-AI 基础-MOC.md'`

Expected: `Summary: 0 issue(s)`。

### Task 2: 重构表示与数据基础

**Files:**
- Modify: `G-AI 基础/01-线性代数.md`
- Modify: `G-AI 基础/02-概率统计.md`

**Interfaces:**
- Consumes: 原始数据、Embedding、线性层、二分类预测和验证集指标。
- Produces: 表示与抽样环节的 AI 解释和排错入口。

- [ ] **Step 1: 重构线性代数**

以文本 Embedding 进入线性层并计算 Attention 分数为贯穿案例，把形状、内积和矩阵乘法逐一映射到 Token、批次、隐藏维度和权重。

- [ ] **Step 2: 重构概率统计**

以二分类模型的概率输出和验证准确率为贯穿案例，把条件概率、期望、方差与置信区间映射到预测解释和评测波动。

- [ ] **Step 3: 增加排错与收益**

两篇分别加入形状错位、相似度误用、拆分泄漏、样本相关等排错表，并给出能够解释、实现和排查的学习收益。

### Task 3: 重构训练核心链路

**Files:**
- Modify: `G-AI 基础/03-微积分与梯度.md`
- Modify: `G-AI 基础/04-优化.md`
- Modify: `G-AI 基础/05-数值稳定性.md`
- Modify: `G-AI 基础/09-自动微分直觉.md`

**Interfaces:**
- Consumes: 模型预测、标量损失、计算图和参数。
- Produces: 前向计算、梯度回传、参数更新和数值故障的完整解释。

- [ ] **Step 1: 重构微积分与梯度**

使用单参数预测与平方损失贯穿导数、梯度和链式法则，明确每个导数对应预测或损失的哪段影响。

- [ ] **Step 2: 重构优化**

把现有二次目标明确为单参数模型训练，实验输出参数和损失轨迹，增加收敛、振荡和泛化排错。

- [ ] **Step 3: 重构数值稳定性**

从分类模型极端 logits 的 `NaN` 开始，贯穿稳定 Softmax、LogSumExp 和交叉熵，增加首个非有限值的定位流程。

- [ ] **Step 4: 重构自动微分**

把计算图变量映射为特征、权重、偏置、预测和损失，并解释 PyTorch 反向传播现象。

### Task 4: 重构损失与表示机制

**Files:**
- Modify: `G-AI 基础/06-信息论.md`
- Modify: `G-AI 基础/07-矩阵分解.md`
- Modify: `G-AI 基础/08-最大似然与最大后验.md`

**Interfaces:**
- Consumes: 分类概率、Embedding 矩阵、模型损失和参数先验。
- Produces: 交叉熵、压缩、损失选择和正则化的 AI 解释。

- [ ] **Step 1: 重构信息论**

以分类模型正确类别概率为主线，把熵、交叉熵和 KL 映射到标签分布、预测分布与训练损失。

- [ ] **Step 2: 重构矩阵分解**

以 Embedding 矩阵压缩为主线，连接 PCA、低秩权重与重构误差，并说明任务指标边界。

- [ ] **Step 3: 重构参数估计**

从损失函数来源切入，贯穿分类负对数似然、回归 MSE 和 L2 正则化。

### Task 5: 重构决策与拓展机制

**Files:**
- Modify: `G-AI 基础/10-凸优化.md`
- Modify: `G-AI 基础/11-不确定性量化.md`
- Modify: `G-AI 基础/12-因果推断.md`
- Modify: `G-AI 基础/13-信息几何.md`

**Interfaces:**
- Consumes: 训练目标、模型概率、策略干预和参数更新。
- Produces: 全局保证、拒答与人工升级、干预效果和分布更新尺度的解释。

- [ ] **Step 1: 重构凸优化**

用线性回归与逻辑回归说明凸性带来的全局保证，并增加求解状态和可行性排错。

- [ ] **Step 2: 重构不确定性量化**

用模型是否应拒答或转人工贯穿校准、区间和 OOD 检测，明确输出如何连接产品动作。

- [ ] **Step 3: 重构因果推断**

用购买预测与优惠券增量效果区分预测和干预，让辛普森悖论与后门调整回到用户策略问题。

- [ ] **Step 4: 重构信息几何**

用一次模型更新引起的分布变化贯穿 Fisher 信息、KL 局部展开和自然梯度。

### Task 6: 全目录验收

**Files:**
- Verify: `G-AI 基础/*.md`

**Interfaces:**
- Consumes: 重构后的 MOC 和 13 篇笔记。
- Produces: 数学依赖正确、AI 上下文贯穿且可执行的完整目录。

- [ ] **Step 1: 检查结构与链接**

自动扫描 13 篇笔记的 AI 问题、链路位置、工程排错、学习收益、Front Matter 和本地链接。

- [ ] **Step 2: 执行代码块**

在临时 Python 3.12 虚拟环境安装 NumPy，逐个执行 13 个 Python 代码块。

Expected: `python_blocks=13, errors=0`。

- [ ] **Step 3: 执行 Markdown 和差异检查**

Run: `npx --yes markdownlint-cli2 'G-AI 基础/*.md' && git diff --check`

Expected: Markdownlint 报告 0 个问题，Git 差异无空白错误。
