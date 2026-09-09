# 机器学习内容补全实施计划

<!-- markdownlint-disable MD001 MD013 MD032 MD036 -->

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 `H-机器学习` 建设为覆盖 15 个主题、可独立阅读、能用于真实建模与排错的机器学习知识体系。

**Architecture:** 以端到端建模工作流为主线，以任务类型为第二入口。每篇笔记从业务问题和错误成本开始，经基线、机制、手算、可执行实验、评测、泄漏和排错，最终回到模型选择与上线决策；数学细节链接 `G-AI 基础`，避免重复推导。

**Tech Stack:** Markdown、YAML Front Matter、Python 3、NumPy、scikit-learn、markdownlint-cli2

---

### Task 1: 重建机器学习导航

**Files:**
- Modify: `H-机器学习/00-机器学习-MOC.md`

**Step 1: 写入按工作流导航**

把业务目标、问题定义、验证设计、特征工程、模型训练、指标校准、上线监控串成可点击路线。

**Step 2: 写入按任务类型导航**

分别组织监督学习、无监督学习、排序、时序、在线学习和因果决策入口，并保留前置知识、项目、面试与相邻领域。

**Step 3: 验证导航链接**

Run: `python3` 本地链接扫描脚本
Expected: MOC 中 15 个主题链接全部解析到存在的文件。

### Task 2: 完成监督学习核心笔记

**Files:**
- Create: `H-机器学习/01-回归.md`
- Create: `H-机器学习/02-分类.md`
- Create: `H-机器学习/03-树与 Boosting.md`

**Step 1: 建立业务案例与基线**

分别用交付时长、客户流失和表格数据强基线明确样本、标签、预测时点、错误成本与朴素基线。

**Step 2: 分层解释模型机制**

从直觉到公式解释线性回归、逻辑回归、决策树、随机森林和梯度提升，并给出最小手算。

**Step 3: 加入可执行实验与排错**

使用固定随机种子的 NumPy 或 scikit-learn 实验，解释验证结果、泄漏风险、适用边界和排错顺序。

### Task 3: 完成数据与评测核心笔记

**Files:**
- Create: `H-机器学习/04-特征工程.md`
- Create: `H-机器学习/05-数据泄漏.md`
- Create: `H-机器学习/06-指标.md`
- Create: `H-机器学习/10-校准.md`
- Create: `H-机器学习/11-验证设计.md`

**Step 1: 贯通训练与评测边界**

解释预测时点、数据拆分、Pipeline、阈值、概率质量和业务成本之间的关系。

**Step 2: 构造可观察的错误实验**

让读者实际观察预处理泄漏、错误拆分、阈值变化和校准前后的差异，并说明为什么发生。

**Step 3: 建立工程检查清单**

每篇加入“现象、可能原因、优先检查”表格和上线前核查步骤。

### Task 4: 完成无监督学习笔记

**Files:**
- Create: `H-机器学习/07-聚类.md`
- Create: `H-机器学习/08-降维.md`
- Create: `H-机器学习/09-异常检测.md`

**Step 1: 区分无标签任务与监督任务**

说明聚类、降维和异常检测的输出不是天然正确答案，不能只凭图形或单一内部指标断言业务有效。

**Step 2: 完成最小实验**

实现缩放对 K-Means 的影响、PCA 解释方差与下游性能、Isolation Forest 与统计基线比较。

**Step 3: 加入稳定性与业务验证**

写明簇稳定性、信息损失、污染率、人工抽检和后续实验的验证方法。

### Task 5: 完成扩展任务笔记

**Files:**
- Create: `H-机器学习/12-推荐系统.md`
- Create: `H-机器学习/13-时间序列.md`
- Create: `H-机器学习/14-在线学习.md`
- Create: `H-机器学习/15-因果机器学习.md`

**Step 1: 明确各任务独有的验证单位**

推荐系统按用户与时间切分，时间序列滚动回测，在线学习按数据到达顺序评测，因果机器学习围绕处理、结果和反事实假设设计。

**Step 2: 建立朴素但可信的基线**

实现热门推荐、季节性朴素预测、静态模型和总体平均处理效应，并与更复杂方案比较。

**Step 3: 解释上线风险**

覆盖冷启动、反馈回路、概念漂移、延迟标签、共同支持和不可识别等风险。

### Task 6: 全目录验收

**Files:**
- Verify: `H-机器学习/*.md`

**Step 1: 运行 Markdown 检查**

Run: `npx --yes markdownlint-cli2 'H-机器学习/*.md'`
Expected: 0 errors.

**Step 2: 运行结构与链接检查**

Run: `python3` 自定义扫描脚本，检查 Front Matter、一级标题、必需章节、排错表格、15 个 MOC 链接和所有本地链接。
Expected: 所有文件通过。

**Step 3: 执行全部 Python 代码块**

Run: 在临时虚拟环境安装 NumPy 和 scikit-learn，逐文件、逐代码块独立执行。
Expected: 所有代码块无异常退出，输出与正文解释一致。

**Step 4: 检查补丁质量**

Run: `git diff --check`
Expected: 无尾随空格或补丁格式错误。

**Step 5: 提交实现**

Run: `git add H-机器学习 docs/superpowers/plans/2026-09-09-machine-learning-content.md && git commit -m 'docs: 补全机器学习主题内容'`
Expected: 提交成功且工作区干净。
