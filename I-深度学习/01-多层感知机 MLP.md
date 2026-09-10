---
type: concept
domain:
  - Deep Learning
depth: L2
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - MLP
  - 全连接神经网络
tags:
  - deep-learning
  - neural-network
  - mlp
---

# 多层感知机 MLP

<!-- markdownlint-disable MD013 -->

## 它解决什么深度学习问题

线性模型只能画一条直线或一个平面作为决策边界。现实中的图像、声音和用户行为往往由多个因素共同决定，边界通常是弯曲的。多层感知机 MLP 把“线性变换”和“非线性激活”交替叠加，让网络能学习弯曲、分段的映射。

它是理解其他神经网络的最小骨架：卷积层、循环层和 Transformer 虽然连接方式不同，但仍然在重复“参数化变换 → 非线性 → 损失 → 梯度更新”。

## 不理解会造成什么错误

- 忘记激活函数，多层线性层仍等价于一层线性层。
- 混淆批次轴和特征轴，矩阵乘法形状无法对应。
- 对分类输出先做 Softmax，再错误地把概率传给 `CrossEntropyLoss`。
- 只观察训练准确率，把记住训练样本误当成泛化能力。

## 它在训练系统中的位置

MLP 接收数值化后的特征，完成前向计算并输出 logits。损失函数比较 logits 与标签，反向传播计算参数梯度，优化器再更新参数。

```text
输入 [B,D] → 隐藏层 [B,H] → logits [B,C] → 损失标量
                                      ↓
参数更新 ← 参数梯度 ← 反向传播 ←────────┘
```

其中 $B$ 是批大小，$D$ 是输入维度，$H$ 是隐藏维度，$C$ 是类别数。

## 从手写形状识别开始

假设每张 $2\times2$ 黑白图像被展平成 4 个数。任务是判断亮点主要位于主对角线还是副对角线：

- 输入：`[B,4]`，每个值表示一个像素；
- 标签：`[B]`，取值为 0 或 1；
- 输出：`[B,2]` logits，数值越大表示该类越可信；
- 损失：交叉熵；
- 指标：独立测试集准确率；
- 错误成本：若用于缺陷图案识别，漏检通常比误报更贵，应额外看召回率。

## 先建立简单基线

先训练逻辑回归，即不含隐藏层的 `Linear(4, 2)`。若它已满足业务要求，MLP 的额外参数和延迟就没有价值。只有当验证集显示线性边界不足，才加入隐藏层。

## 张量形状与数据流

一个两层 MLP 的前向过程是：

| 步骤 | 计算 | 形状 |
| --- | --- | --- |
| 输入 | $X$ | `[B,D]` |
| 第一层 | $Z_1=XW_1+b_1$ | `[B,H]` |
| 激活 | $A_1=\operatorname{ReLU}(Z_1)$ | `[B,H]` |
| 第二层 | $Z_2=A_1W_2+b_2$ | `[B,C]` |
| 损失 | 交叉熵 | 标量 |

$W_1$ 是 `[D,H]`，$b_1$ 是 `[H]`；偏置沿批次轴广播。$W_2$ 是 `[H,C]`，$b_2$ 是 `[C]`。

## 核心机制

线性层混合已有特征，ReLU 再把空间切成不同区域：

$$
\operatorname{ReLU}(z)=\max(0,z)
$$

如果没有 ReLU，两层线性变换可以合并：

$$
(XW_1+b_1)W_2+b_2=X(W_1W_2)+(b_1W_2+b_2)
$$

右侧仍是一次线性变换，所以“层数更多”不自动意味着表达能力更强。非线性激活才阻止这种合并。

分类时保留 logits。对样本 $i$，Softmax 概率和交叉熵为：

$$
p_{ic}=\frac{e^{z_{ic}}}{\sum_{j=1}^{C}e^{z_{ij}}},\qquad
L_i=-\log p_{i,y_i}
$$

实际库会把 LogSoftmax 与负对数似然合并，以获得更好的数值稳定性。

## 最小手算

取单个输入 $x=[1,2]$：

$$
W_1=\begin{bmatrix}1&-1\\0.5&1\end{bmatrix},\quad
b_1=[0,0]
$$

则 $z_1=xW_1=[2,1]$，ReLU 后仍是 $a_1=[2,1]$。若

$$
W_2=\begin{bmatrix}1&0\\-1&2\end{bmatrix},\quad b_2=[0,0]
$$

则 logits 为 $z_2=[1,2]$。类别 1 的概率是 $e^2/(e^1+e^2)\approx0.731$，标签若为 1，损失约为 $-\log(0.731)=0.313$。

## NumPy 复刻

下面只复刻前向和交叉熵，并核对上述手算。

```python
import numpy as np

np.random.seed(7)
x = np.array([[1.0, 2.0]])
w1 = np.array([[1.0, -1.0], [0.5, 1.0]])
b1 = np.zeros(2)
w2 = np.array([[1.0, 0.0], [-1.0, 2.0]])
b2 = np.zeros(2)

hidden = np.maximum(0.0, x @ w1 + b1)
logits = hidden @ w2 + b2
stable = logits - logits.max(axis=1, keepdims=True)
prob = np.exp(stable) / np.exp(stable).sum(axis=1, keepdims=True)
loss = -np.log(prob[0, 1])

assert hidden.shape == (1, 2)
assert logits.shape == (1, 2)
assert np.allclose(logits, [[1.0, 2.0]])
assert np.isclose(loss, 0.31326169)
print("logits:", logits, "loss:", round(float(loss), 4))
```

## PyTorch 实验

合成数据模拟两类对角形状，并显式写出完整训练循环。

```python
import torch
from torch import nn

torch.manual_seed(7)
n = 160
x = torch.randn(n, 4)
y = ((x[:, 0] * x[:, 3]) > (x[:, 1] * x[:, 2])).long()
train_x, test_x = x[:120], x[120:]
train_y, test_y = y[:120], y[120:]

model = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 2))
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.03)

model.train()
first_loss = None
for _ in range(180):
    optimizer.zero_grad()
    logits = model(train_x)
    loss = loss_fn(logits, train_y)
    if first_loss is None:
        first_loss = loss.item()
    loss.backward()
    optimizer.step()

model.eval()
with torch.inference_mode():
    accuracy = (model(test_x).argmax(dim=1) == test_y).float().mean()
assert logits.shape == (120, 2)
assert loss.item() < first_loss
assert accuracy.item() >= 0.70
print("loss:", round(loss.item(), 4), "test accuracy:", round(accuracy.item(), 3))
```

## 如何解释实验结果

损失下降说明优化器找到了更符合训练样本的参数；测试准确率高于随机猜测说明学到的规律能部分泛化。它不能证明模型适合真实手写图像：合成数据缺少笔画粗细、噪声和采集偏差，业务数据仍需独立验证。

## 训练与推理差异

训练阶段保留计算图、计算梯度并更新参数。推理阶段应调用 `model.eval()`，再用 `torch.inference_mode()` 关闭梯度记录。MLP 本身若没有 Dropout 或 BatchNorm，模式切换可能不改变数值，但统一执行能避免模型扩展后留下隐患。

## 数据与验证风险

- 先按真实部署单位拆分数据，再做增强或标准化，避免同一对象进入不同集合。
- 不能用测试集选择隐藏层宽度、学习率或训练轮数。
- 类别不均衡时，准确率可能掩盖少数类漏检，应结合业务成本选择指标。
- 图像展平会丢失空间归纳偏置，尺寸变大时应比较 CNN。

详见[数据泄漏](../H-机器学习/05-数据泄漏.md)和[验证设计](../H-机器学习/11-验证设计.md)。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 矩阵乘法报错 | 输入维度与 `in_features` 不一致 | 打印每层输入输出形状 |
| 损失不降 | 忘记非线性、学习率不合适或标签错误 | 尝试过拟合 8 个样本 |
| 损失为 NaN | 学习率过大或 logits 溢出 | 检查有限值和梯度范数 |
| 训练很好验证很差 | 参数过多或数据泄漏 | 核对拆分并减小网络 |
| 分类损失异常 | 重复应用 Softmax | 直接把 logits 传给交叉熵 |

## 适用与不适用场景

MLP 适合固定长度的表格特征、小型嵌入向量和其他网络中的前馈子层。图像、长序列和图结构若直接展平，会忽略有价值的局部或关系结构；应优先比较 CNN、Transformer 或图神经网络。数据很少、表格特征成熟时，树模型也常是更强的基线。

## 学习收益

读完后应能从 `[B,D]` 追踪到 `[B,C]`，解释激活函数为何必要，手算一次前向与交叉熵，并写出不会混淆 logits 和概率的 PyTorch 分类器。

## 给别人讲清楚

可以把 MLP 比作“反复重组线索并做筛选”：线性层把已有线索组合成新线索，激活函数决定哪些组合在当前输入区域有效，最后一层给每个类别打分。训练就是根据错误反向调整这些组合规则。

## 自检问题

1. 为什么任意多个不带激活的线性层仍等价于一个线性层？
2. `[32,10]` 输入经过 `Linear(10,64)` 后是什么形状？
3. 为什么 `CrossEntropyLoss` 应接收 logits 而不是 Softmax 概率？
4. 训练准确率很高时，为什么仍不能宣布模型可上线？

## 相关主题

- [线性代数](../G-AI%20基础/01-线性代数.md)
- [数值稳定性](../G-AI%20基础/05-数值稳定性.md)
- [神经网络反向传播](02-神经网络反向传播.md)
- [神经网络正则化](05-神经网络正则化.md)
- [分类](../H-机器学习/02-分类.md)

## 资料来源

- PyTorch，*Linear*，<https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html>，访问于 2026-09-10。
- PyTorch，*CrossEntropyLoss*，<https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html>，访问于 2026-09-10。
- Ian Goodfellow 等，*Deep Learning*，<https://www.deeplearningbook.org/>，访问日期：2026-09-10。
