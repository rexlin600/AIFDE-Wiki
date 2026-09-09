# AI Foundations Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 AI 基础 MOC 创建 13 篇低数学门槛但推导完整的概念笔记，并建立可验证的目录导航。

**Architecture:** `00-AI 基础-MOC.md` 只负责领域边界、学习顺序和链接；13 篇概念笔记各自负责一个稳定主题。内容按依赖顺序分四批完成，每批统一符号、交叉链接并运行仓库检查，最终进行全目录一致性复核。

**Tech Stack:** GitHub Markdown、YAML Front Matter、LaTeX 数学公式、Python 3.12、NumPy、仓库 Wiki 校验和 Markdownlint。

## Global Constraints

- 目标读者只假定具备高中代数和基础 Python 能力。
- 文件名与一级标题严格采用 MOC 主题名，编号只用于排序。
- 每篇初稿使用 `type: concept`、`domain: [AI Foundations]` 和 `maturity: draft`。
- 内容按“具体问题 → 数字示例 → 自然语言规则 → 数学定义 → 一般推导 → 工程应用”展开。
- 每篇至少包含一个完整核心推导或证明、一个手算例子、一个可运行的 NumPy 实验、一个 AI 工程应用、两个常见误区、一份讲解提纲和分层自检问题。
- 首次出现的符号必须解释含义、取值范围、类型，以及适用时的形状或单位。
- MOC 和知识笔记使用 GitHub 可渲染的相对 Markdown 链接，不依赖 Obsidian 专属语法。
- 来源优先使用教材、原始论文、标准、官方课程、官方文档和官方仓库，并记录访问日期 `2026-09-09`。
- 每批修改后运行 `python3 -m pytest -q`、`python3 scripts/validate_wiki.py .` 和 `npm run lint:md`。

---

### Task 1: 建立基础数学主线

**Files:**
- Create: `G-AI 基础/01-线性代数.md`
- Create: `G-AI 基础/02-概率统计.md`
- Create: `G-AI 基础/03-微积分与梯度.md`

**Interfaces:**
- Consumes: `G-AI 基础/00-AI 基础-MOC.md` 中的领域边界、主题范围和推荐顺序。
- Produces: 后续优化、信息论、矩阵分解、参数估计、自动微分和不确定性主题可链接的数学定义与符号体系。

- [ ] **Step 1: 创建线性代数笔记**

写清标量、向量、矩阵、张量、形状、线性组合、内积、矩阵乘法、范数和余弦相似度。完整推导矩阵乘法表示线性变换组合及余弦相似度取值范围，用二维向量手算并提供批量 NumPy 形状断言。

- [ ] **Step 2: 创建概率统计笔记**

写清随机试验、事件、随机变量、概率分布、联合与条件概率、独立、贝叶斯公式、期望、方差、协方差、抽样和置信区间。用计数定义推导贝叶斯公式，用伯努利样本手算均值和方差，并用 NumPy 模拟置信区间覆盖率。

- [ ] **Step 3: 创建微积分与梯度笔记**

从平均变化率进入极限和导数，依次解释偏导数、方向导数、梯度和链式法则。用极限推导平方函数导数，完整推导两层复合函数的链式法则，并用有限差分验证解析梯度。

- [ ] **Step 4: 运行第一批检查**

Run: `python3 -m pytest -q && python3 scripts/validate_wiki.py . && npm run lint:md`

Expected: 三条命令退出码均为 0；新文件无非法 Front Matter、断链或 Markdownlint 错误。

### Task 2: 建立训练计算主线

**Files:**
- Create: `G-AI 基础/04-优化.md`
- Create: `G-AI 基础/05-数值稳定性.md`

**Interfaces:**
- Consumes: `01-线性代数.md` 的向量和范数、`03-微积分与梯度.md` 的梯度与链式法则。
- Produces: 深度学习训练、自动微分和凸优化可复用的目标函数、更新规则与稳定计算解释。

- [ ] **Step 1: 创建优化笔记**

定义决策变量、目标函数、约束、可行域、局部解和全局解。从一阶局部近似推导梯度下降更新式，解释学习率、批量梯度、随机梯度、停止条件和鞍点，用一元二次函数手算两步更新并绘制不同学习率的数值轨迹。

- [ ] **Step 2: 创建数值稳定性笔记**

解释浮点表示、舍入误差、灾难性消减、溢出、下溢和条件数。推导减去最大值不改变 Softmax 结果及稳定 LogSumExp，比较直接写法和稳定写法在极端 logits 下的 NumPy 输出。

- [ ] **Step 3: 运行第二批检查**

Run: `python3 -m pytest -q && python3 scripts/validate_wiki.py . && npm run lint:md`

Expected: 三条命令退出码均为 0；新文件无非法 Front Matter、断链或 Markdownlint 错误。

### Task 3: 建立常用数学机制

**Files:**
- Create: `G-AI 基础/06-信息论.md`
- Create: `G-AI 基础/07-矩阵分解.md`
- Create: `G-AI 基础/08-最大似然与最大后验.md`
- Create: `G-AI 基础/09-自动微分直觉.md`

**Interfaces:**
- Consumes: 基础数学和训练计算主线中的概率、矩阵、梯度、优化及数值稳定性定义。
- Produces: 分类损失、降维、概率参数估计和框架反向传播的独立机制说明。

- [ ] **Step 1: 创建信息论笔记**

从理想编码长度解释信息量，定义熵、交叉熵和 KL 散度，推导三者关系并用对数不等式证明 KL 非负性。手算二元分布的指标，并用 NumPy 比较预测置信度变化时的交叉熵。

- [ ] **Step 2: 创建矩阵分解笔记**

解释特征值、特征向量、特征分解、奇异值分解和低秩近似的几何意义与适用条件。验证 SVD 重构，展示保留不同奇异值数量时的误差和压缩权衡。

- [ ] **Step 3: 创建最大似然与最大后验笔记**

从观测数据的概率进入似然，推导伯努利参数的最大似然估计、高斯误差对应均方误差，以及高斯先验如何产生 L2 正则化。用 NumPy 比较 MLE 与 MAP 在小样本下的结果。

- [ ] **Step 4: 创建自动微分直觉笔记**

定义计算图和局部导数，逐节点手算前向模式与反向模式，解释向量雅可比积、梯度累积和叶子变量。用小型纯 Python 或 NumPy 计算图结果对照解析导数。

- [ ] **Step 5: 运行第三批检查**

Run: `python3 -m pytest -q && python3 scripts/validate_wiki.py . && npm run lint:md`

Expected: 三条命令退出码均为 0；新文件无非法 Front Matter、断链或 Markdownlint 错误。

### Task 4: 建立拓展数学视野

**Files:**
- Create: `G-AI 基础/10-凸优化.md`
- Create: `G-AI 基础/11-不确定性量化.md`
- Create: `G-AI 基础/12-因果推断.md`
- Create: `G-AI 基础/13-信息几何.md`

**Interfaces:**
- Consumes: 前九篇笔记的概率、矩阵、梯度、优化、信息论和参数估计概念。
- Produces: 可按项目需要深入的全局最优性、预测可信度、因果判断和概率空间几何入口。

- [ ] **Step 1: 创建凸优化笔记**

定义凸集、凸组合、凸函数、严格凸和强凸，解释一阶及二阶判据，并证明凸函数的局部最优也是全局最优。用 NumPy 比较凸与非凸目标的优化轨迹，再介绍约束、拉格朗日乘子和对偶的工程直觉。

- [ ] **Step 2: 创建不确定性量化笔记**

区分数据不确定性与模型不确定性、置信区间与预测区间、概率置信度与校准。解释覆盖率、可靠性图、Brier Score、Bootstrap 和分布外输入，用 NumPy 模拟区间覆盖和分类校准。

- [ ] **Step 3: 创建因果推断笔记**

区分相关、干预和反事实，解释混杂、碰撞点、因果图、潜在结果、可交换性和后门调整。用辛普森悖论数据手算观察相关与分组关系，并说明随机试验和观察研究的识别边界。

- [ ] **Step 4: 创建信息几何笔记**

从概率分布族作为曲面建立直觉，定义得分函数和 Fisher 信息，推导一维参数下 KL 散度的二阶局部展开，解释自然梯度为什么考虑参数空间尺度。用伯努利分布验证局部 KL 与 Fisher 近似。

- [ ] **Step 5: 运行第四批检查**

Run: `python3 -m pytest -q && python3 scripts/validate_wiki.py . && npm run lint:md`

Expected: 三条命令退出码均为 0；新文件无非法 Front Matter、断链或 Markdownlint 错误。

### Task 5: 更新导航并执行全目录验收

**Files:**
- Modify: `G-AI 基础/00-AI 基础-MOC.md`
- Verify: `G-AI 基础/01-线性代数.md`
- Verify: `G-AI 基础/02-概率统计.md`
- Verify: `G-AI 基础/03-微积分与梯度.md`
- Verify: `G-AI 基础/04-优化.md`
- Verify: `G-AI 基础/05-数值稳定性.md`
- Verify: `G-AI 基础/06-信息论.md`
- Verify: `G-AI 基础/07-矩阵分解.md`
- Verify: `G-AI 基础/08-最大似然与最大后验.md`
- Verify: `G-AI 基础/09-自动微分直觉.md`
- Verify: `G-AI 基础/10-凸优化.md`
- Verify: `G-AI 基础/11-不确定性量化.md`
- Verify: `G-AI 基础/12-因果推断.md`
- Verify: `G-AI 基础/13-信息几何.md`

**Interfaces:**
- Consumes: 13 篇已完成的概念笔记和现有 MOC 表格。
- Produces: 从 MOC 可访问全部主题、从每篇可回到前置和相邻主题的完整导航。

- [ ] **Step 1: 更新 MOC 主题链接**

把核心主题、常用主题和拓展视野表格中的主题名称分别链接到对应编号文件，保持现有范围、深度和重要程度不变，并将 `updated` 更新为 `2026-09-09`。

- [ ] **Step 2: 复核术语和推导一致性**

确认向量默认列向量、对数底数、概率记号、梯度形状、样本索引、期望与经验均值等约定在 13 篇中一致；重复结论链接到首次完整讲解处。

- [ ] **Step 3: 执行示例代码**

将每个 Python 代码块复制到临时脚本运行，确认退出码为 0，输出数值与正文一致；不得向仓库添加生成数据或临时脚本。

- [ ] **Step 4: 执行最终仓库检查**

Run: `python3 -m pytest -q && python3 scripts/validate_wiki.py . && npm run lint:md && git diff --check`

Expected: 所有命令退出码均为 0；测试无失败，Wiki 校验无错误，Markdownlint 无错误，Git 差异无空白问题。
