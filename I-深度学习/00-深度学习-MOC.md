---
type: moc
domain:
  - Deep Learning
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 深度学习
tags:
  - core
  - deep-learning
---

# 深度学习 MOC

## 领域边界

本领域解释神经网络如何学习表示，以及如何用 PyTorch 构建、训练、评估和交付模型。范围覆盖基础架构、训练机制、经典序列与视觉模型和 Transformer，不展开 LLM 的适配、应用接口或服务治理。

## 前置知识

- [数学与 AI 基础](../G-AI%20%E5%9F%BA%E7%A1%80/00-AI%20%E5%9F%BA%E7%A1%80-MOC.md)中的矩阵、梯度、链式法则、优化和数值稳定性。
- [机器学习](../H-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/00-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0-MOC.md)中的数据拆分、泛化、指标和泄漏。
- Python 类、迭代器和数组编程基础。

## 推荐顺序

1. 从 MLP、前向计算与反向传播建立计算图直觉。
2. 学习初始化、优化器和正则化，掌握稳定训练与诊断。
3. 分别用 CNN 和 RNN/LSTM 理解空间与序列归纳偏置。
4. 学习 Attention 与 Transformer，再将全流程落到 PyTorch 工程。

## 核心主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| MLP | 线性层、激活函数、层宽与深度、表达能力和张量形状 | L2 | core |
| 反向传播 | 计算图、链式法则、梯度累积、`backward` 语义和数值梯度检查 | L3 | core |
| 初始化 | Xavier、Kaiming、偏置初始化及其对激活和梯度尺度的影响 | L2 | core |
| 优化器 | SGD、Momentum、Adam/AdamW、学习率计划和梯度裁剪 | L3 | core |
| 正则化 | Weight Decay、Dropout、数据增强、早停和归一化的适用边界 | L3 | core |
| Attention | Query、Key、Value、缩放点积、Mask、多头机制和复杂度 | L3 | core |
| Transformer | 编码器/解码器、残差、归一化、前馈层、位置表示和因果 Mask | L3 | core |
| PyTorch 工程 | Tensor、Module、Autograd、Dataset/DataLoader、训练循环、检查点和推理模式 | L3 | core |

## 常用主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| CNN | 卷积、感受野、池化、步幅、图像增强和迁移学习 | L2 | common |
| RNN/LSTM | 循环状态、时间反向传播、门控机制和长依赖限制 | L2 | common |
| 训练诊断 | 损失曲线、梯度与激活统计、过拟合小批次、消融和错误分析 | L3 | common |
| 批处理与序列化 | Padding、Mask、动态批处理、`state_dict`、设备与精度兼容 | L3 | common |

## 拓展视野

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| 混合精度与分布式训练 | 自动混合精度、梯度缩放、数据并行、模型并行和通信开销 | L3 | extension |
| 生成模型 | 自编码器、GAN、扩散模型的目标函数与采样直觉 | L2 | extension |
| 图神经网络 | 消息传递、聚合、图级与节点级任务 | L3 | extension |
| 自定义算子与编译 | 自定义 Autograd、算子融合、图编译和性能剖析 | L4 | extension |

## 最小实验

- 用 NumPy 复刻两层 MLP 的前向与反向传播，并通过有限差分检查梯度。
- 在小型数据集上比较错误初始化、Xavier 和 Kaiming，记录激活、梯度和收敛曲线。
- 用 PyTorch 实现单头 Causal Self-Attention，以形状断言和 Mask 测试验证行为。

## 项目

- 在 `ai-foundations-labs` 中维护 MLP 训练、过拟合诊断、检查点恢复和推理脚本。
- 把 Attention 与 Transformer 最小复刻作为[阶段 2：LLM 工程](../F-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/03-%E9%98%B6%E6%AE%B5%202-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM%20%E5%B7%A5%E7%A8%8B.md)的机制证据。

## 开源研究

- 跟踪 PyTorch 从 `loss.backward()`、梯度累积到优化器 `step()` 的关键路径。
- 跟踪 PyTorch Examples 中数据加载、训练、验证和检查点的生命周期。
- 最小复刻 Attention，并与 PyTorch 等价算子在形状和数值容限内对照。

## 面试入口

- 解释反向传播、初始化、归一化和残差连接如何共同影响训练稳定性。
- 比较 CNN、RNN/LSTM 与 Transformer 的归纳偏置和计算复杂度。
- 设计可恢复、可评估的 PyTorch 训练循环，并排查损失不下降或出现 NaN。

## 相邻领域

- [数学与 AI 基础](../G-AI%20%E5%9F%BA%E7%A1%80/00-AI%20%E5%9F%BA%E7%A1%80-MOC.md)：解释梯度、优化和数值误差。
- [机器学习](../H-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/00-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0-MOC.md)：提供泛化、验证和指标方法。
- [LLM](../J-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM/00-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM-MOC.md)：将 Transformer 扩展到预训练、适配和生成。
- [AI 全局知识地图](../E-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/01-AI%20%E7%9F%A5%E8%AF%86%E5%9C%B0%E5%9B%BE.md)：查看深度学习的上下游位置。
