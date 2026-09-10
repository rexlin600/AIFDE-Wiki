# Deep Learning Content Implementation Plan

<!-- markdownlint-disable MD001 MD013 MD032 MD036 -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `I-深度学习` 建设为包含 16 篇独立主题笔记、贯通神经网络训练原理与 PyTorch 工程的知识体系。

**Architecture:** 以“张量前向、损失、反向传播、参数更新、稳定训练、验证诊断、保存推理、规模扩展”为主线。每篇从真实 AI 任务开始，用形状、推导、手算、NumPy 复刻和 PyTorch 实验逐层讲透，并通过 MOC 提供训练流程、模型架构和故障现象三种入口。

**Tech Stack:** Markdown、YAML Front Matter、Python 3、NumPy、PyTorch、markdownlint-cli2

## Global Constraints

- 新增 16 篇笔记，文件名和一级标题严格使用已确认主题名。
- 新增笔记统一使用 `type: concept`、`domain: [Deep Learning]`、`maturity: draft`。
- 访问和核验日期统一为 `2026-09-10`。
- 默认实验必须在 CPU 执行，不下载在线数据，固定 NumPy 和 PyTorch 随机种子。
- 图像形状统一为 `[B, C, H, W]`，序列形状统一为 `[B, T, D]`。
- 数学基础链接 `G-AI 基础`，通用拆分、指标和泄漏链接 `H-机器学习`。
- Transformer 不展开 LLM 预训练、对齐、应用接口和服务治理。
- 每篇必须包含真实用途、形状与数据流、关键推导、手算、可执行实验、验证风险、训练推理差异、排错表、适用边界和权威来源。
- PyTorch API 以当前官方文档为准，模型机制优先引用原始论文或权威教材。

---

### Task 1: 重建深度学习导航

**Files:**
- Modify: `I-深度学习/00-深度学习-MOC.md`

**Interfaces:**
- Consumes: 设计稿中的 16 个主题、统一训练主线和领域边界。
- Produces: 指向 16 篇主题笔记的直接链接，以及按训练系统、模型架构和故障现象组织的三种导航。

- [ ] **Step 1: 写入训练系统导航**

按任务与张量、前向、损失、反向传播、参数更新、稳定训练、验证诊断、保存推理和规模扩展组织可点击路线。

- [ ] **Step 2: 写入架构与故障导航**

架构入口覆盖 MLP、CNN、RNN/LSTM、Attention、Transformer、生成模型和图神经网络；故障入口覆盖不收敛、过拟合、NaN、显存不足、恢复失败和推理变慢。

- [ ] **Step 3: 验证导航边界**

Run: `python3` 本地链接扫描脚本

Expected: 16 个主题均有直接链接，数学、机器学习、LLM 和生产目录链接均存在。

### Task 2: 完成神经网络训练基础

**Files:**
- Create: `I-深度学习/01-多层感知机 MLP.md`
- Create: `I-深度学习/02-神经网络反向传播.md`
- Create: `I-深度学习/03-神经网络参数初始化.md`
- Create: `I-深度学习/04-神经网络优化器.md`
- Create: `I-深度学习/05-神经网络正则化.md`

**Interfaces:**
- Consumes: `G-AI 基础`中的线性代数、梯度、自动微分、优化和概率内容。
- Produces: 后续架构笔记共同使用的层、激活、损失、梯度、初始化、优化和泛化语言。

- [ ] **Step 1: 完成 MLP 与反向传播笔记**

使用非线性分类案例，追踪 `[B,D] → [B,H] → [B,C]`，推导线性层、激活、交叉熵和链式法则；用 NumPy 两层网络、有限差分和 PyTorch Autograd 对照。

- [ ] **Step 2: 完成参数初始化与优化器笔记**

从前向和反向方差递推解释 Xavier 与 Kaiming；从梯度下降推到 Momentum、Adam 和 AdamW，区分 L2 正则与解耦 Weight Decay，并比较收敛轨迹。

- [ ] **Step 3: 完成正则化笔记**

用小数据分类案例比较 Weight Decay、Dropout、数据增强与早停，明确训练和推理模式差异以及正则化不能修复数据泄漏。

- [ ] **Step 4: 执行本批实验**

Run: 在隔离环境逐块执行 5 篇中的 NumPy 与 PyTorch 代码。

Expected: 所有形状断言、梯度对照和训练结果通过；损失下降和正则化现象与正文一致。

### Task 3: 完成视觉序列与 Transformer 架构

**Files:**
- Create: `I-深度学习/06-卷积神经网络 CNN.md`
- Create: `I-深度学习/07-循环神经网络 RNN 与 LSTM.md`
- Create: `I-深度学习/08-注意力机制.md`
- Create: `I-深度学习/09-Transformer.md`

**Interfaces:**
- Consumes: Task 2 的层、激活、梯度、初始化和优化概念。
- Produces: 视觉、递归序列和并行序列建模的形状约定、归纳偏置和选择边界。

- [ ] **Step 1: 完成 CNN 笔记**

用图像缺陷检测解释局部连接和权重共享，推导卷积输出尺寸与感受野，手算二维卷积，并与 `torch.nn.Conv2d` 对照。

- [ ] **Step 2: 完成 RNN 与 LSTM 笔记**

用序列分类解释时间展开、共享参数、时间反向传播、梯度消失和门控记忆；追踪 Padding 后的 `[B,T,D]`，比较 RNN 与 LSTM。

- [ ] **Step 3: 完成 Attention 与 Transformer 笔记**

从 Query、Key、Value 推导缩放点积、多头重排和 Mask，说明除以 $\sqrt{d_k}$ 的方差原因；再贯通残差、归一化、前馈和因果 Mask。

- [ ] **Step 4: 执行本批实验**

Run: 在隔离环境执行手工卷积、循环单元、Attention 和最小 Transformer 的 NumPy 与 PyTorch 代码。

Expected: 手工实现与 PyTorch 等价结果在声明容差内一致，Mask 位置满足形状和不可见性断言。

### Task 4: 完成 PyTorch 训练交付能力

**Files:**
- Create: `I-深度学习/10-PyTorch 模型训练.md`
- Create: `I-深度学习/11-深度学习训练诊断.md`
- Create: `I-深度学习/12-批处理与模型序列化.md`

**Interfaces:**
- Consumes: Task 2 和 Task 3 的模型、损失、梯度及统一形状约定。
- Produces: 可验证、可诊断、可恢复的训练循环和推理工件生命周期。

- [ ] **Step 1: 完成 PyTorch 模型训练笔记**

从 Dataset、DataLoader、Module 到 `zero_grad → forward → loss → backward → step` 写出完整训练验证循环，解释设备迁移、模式切换和 `inference_mode`。

- [ ] **Step 2: 完成训练诊断笔记**

建立“先过拟合一个小批次”的诊断顺序，记录损失、梯度范数和激活统计，通过故意断开梯度、错误学习率和标签问题展示症状。

- [ ] **Step 3: 完成批处理与模型序列化笔记**

实现变长序列 Padding、Mask 和批整理；用内存缓冲区验证 `state_dict` 保存恢复后输出一致，并说明完整检查点所需状态。

- [ ] **Step 4: 执行本批实验**

Run: 在隔离环境执行训练、诊断、Padding、Mask 与检查点往返实验。

Expected: 训练验证流程无梯度污染，恢复前后输出满足数值容差，错误实验能稳定产生声明的故障信号。

### Task 5: 完成规模扩展与前沿架构

**Files:**
- Create: `I-深度学习/13-混合精度与分布式训练.md`
- Create: `I-深度学习/14-生成模型.md`
- Create: `I-深度学习/15-图神经网络.md`
- Create: `I-深度学习/16-自定义算子与模型编译.md`

**Interfaces:**
- Consumes: 完整训练循环、数值稳定性、检查点和架构基础。
- Produces: 对精度与并行、生成目标、图消息传递、自定义梯度和编译性能的可验证理解。

- [ ] **Step 1: 完成混合精度与分布式训练笔记**

推导梯度缩放如何把小梯度移出低精度下溢区间，解释数据并行梯度平均、有效批大小、通信开销和恢复边界；CPU 实验只验证语义，CUDA 结论明确硬件前提。

- [ ] **Step 2: 完成生成模型笔记**

以生成简单二维样本为案例，分层解释自编码器、GAN 和扩散模型各自学习的目标、训练信号和采样路径，不把三者混为同一机制。

- [ ] **Step 3: 完成图神经网络笔记**

用关系欺诈检测解释节点、边、邻居聚合和消息传递，手算一轮归一化聚合，并用张量实现节点分类的最小前向。

- [ ] **Step 4: 完成自定义算子与模型编译笔记**

实现自定义 Autograd 函数并通过 `gradcheck`，解释图捕获、图中断、算子融合、动态形状和性能剖析；编译结果不承诺固定加速比。

- [ ] **Step 5: 执行本批实验**

Run: 在隔离 CPU 环境执行梯度缩放语义、生成目标、消息聚合、自定义梯度和可用时的 `torch.compile` 实验。

Expected: 数值和形状断言通过；硬件相关能力能够安全跳过并输出明确原因。

### Task 6: 全目录验收

**Files:**
- Verify: `I-深度学习/*.md`

**Interfaces:**
- Consumes: Task 1 至 Task 5 的 MOC 和 16 篇主题笔记。
- Produces: 可提交的完整深度学习知识目录。

- [ ] **Step 1: 运行 Markdown 检查**

Run: `npx --yes markdownlint-cli2 'I-深度学习/*.md'`

Expected: 0 errors。

- [ ] **Step 2: 运行结构和链接检查**

Run: `python3` 自定义扫描脚本，检查 Front Matter、一级标题、必需章节、排错表格、16 个 MOC 直接链接和全部本地链接。

Expected: 16 篇全部通过，无损坏链接。

- [ ] **Step 3: 执行全部 Python 代码块**

Run: 在临时虚拟环境安装 NumPy 和 PyTorch，逐文件按顺序执行每个 Python 代码块。

Expected: 所有 CPU 代码块无异常退出；硬件条件分支给出明确可解释输出。

- [ ] **Step 4: 核对形状与训练语义**

Run: 扫描 `[B,C,H,W]`、`[B,T,D]`、`zero_grad`、`eval`、`inference_mode` 和检查点章节，并复核跨篇术语。

Expected: 形状记号一致，训练验证测试角色无冲突。

- [ ] **Step 5: 检查补丁质量并提交**

Run: `git diff --check && git add I-深度学习 docs/superpowers/plans/2026-09-10-deep-learning-content.md && git commit -m 'docs: 补全深度学习主题内容'`

Expected: 提交成功且工作区干净。
