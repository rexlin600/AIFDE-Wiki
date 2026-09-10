---
type: concept
domain:
  - Deep Learning
depth: L2
importance: common
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - CNN
  - 图像卷积网络
tags:
  - deep-learning
  - computer-vision
  - cnn
---

# 卷积神经网络 CNN

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么深度学习问题

卷积神经网络让模型利用图像的两个事实：相邻像素通常共同组成局部结构，同一种结构可能出现在任何位置。它不为每个位置重新学习一套规则，而是让同一个卷积核滑过整幅图像，因此能用较少参数识别边缘、纹理和缺陷。

真实系统中的输入统一写成 `[B,C,H,W]`：批大小、通道数、高度、宽度。不要把高度 `H` 与注意力头数混淆；本篇不使用“头”这个概念。

## 不理解会造成什么错误

- 把 `[B,H,W,C]` 直接交给 PyTorch，导致通道维解释错误。
- 只看分类准确率，不检查模型是否学到了背景或拍摄水印。
- 不计算输出尺寸，使线性层输入维度对不上。
- 认为卷积天然平移不变；卷积更准确地说是平移等变，池化和全局聚合才增强不变性。
- 在整套数据上计算归一化统计或做重复图像拆分，造成验证泄漏。

## 它在训练系统中的位置

卷积层替代通用全连接层完成图像特征提取。它接收 `[B,C_in,H,W]`，输出 `[B,C_out,H_out,W_out]`，再由激活、池化和分类头产生预测。参数仍通过[神经网络反向传播](02-神经网络反向传播.md)学习，并受[参数初始化](03-神经网络参数初始化.md)和[正则化](05-神经网络正则化.md)影响。

## 从图像缺陷检测开始

设产线相机拍摄 `8×8` 灰度图，模型判断表面是否存在划痕：

- 样本单位：一件产品的一张图像；
- 输入：`[B,1,8,8]`；
- 标签：无缺陷 `0`、有缺陷 `1`；
- 损失：交叉熵；
- 指标：召回率、误报率和推理延迟；
- 错误成本：漏检流入客户的成本通常高于人工复检一次。

验证集必须按产品批次或拍摄时间隔离。相邻帧几乎相同，随机按图片拆分会让指标虚高。

## 先建立简单基线

先比较像素均值、边缘强度阈值或小型 MLP。若缺陷位置固定，简单规则可能已足够；CNN 的价值在于缺陷会移动、局部形状比绝对位置更稳定。基线还能暴露数据问题：若只凭整体亮度就能高分，模型可能在利用曝光差异。

## 张量形状与数据流

一个小型分类器可以这样流动：

```text
[B,1,8,8]
→ Conv2d(1,4,kernel_size=3,padding=1) → [B,4,8,8]
→ ReLU                                  → [B,4,8,8]
→ MaxPool2d(2)                          → [B,4,4,4]
→ Flatten                               → [B,64]
→ Linear(64,2)                          → [B,2]
```

`C_out=4` 表示模型学习四种不同的局部检测器。空间尺寸保留还是缩小，由卷积核、步幅、填充和膨胀共同决定。

## 核心机制

### 局部连接与权重共享

二维互相关是深度学习框架通常所谓的“卷积”。先看步幅 1、无填充、膨胀率 1 的单输入、单输出通道简化式：

$$
Y_{i,j}=b+\sum_{u=0}^{K_h-1}\sum_{v=0}^{K_w-1}W_{u,v}X_{i+u,j+v}
$$

$X$ 是输入，$W$ 是卷积核，$b$ 是偏置。关键不在求和本身，而在每个位置都使用同一组 $W$。多通道时还要对输入通道求和，每个输出通道拥有一组 `[C_in,K_h,K_w]` 权重。

### 输出尺寸怎样得到

以高度为例，输入两侧各补 $P_h$ 个像素，有效卷积核大小为

$$
K_{eff}=D_h(K_h-1)+1
$$

其中 $D_h$ 是膨胀率。卷积核左端可从 0 移到 $H+2P_h-K_{eff}$，每次跨 $S_h$，所以可放置次数为：

$$
H_{out}=\left\lfloor\frac{H+2P_h-D_h(K_h-1)-1}{S_h}+1\right\rfloor
$$

宽度公式相同。比如 $H=8,K=3,P=1,S=2,D=1$，得到
$\lfloor(8+2-2-1)/2+1\rfloor=4$。

### 感受野怎样扩大

第 $l$ 层的跳距记为 $j_l$，感受野记为 $r_l$。初始 $j_0=r_0=1$，则

$$
j_l=j_{l-1}S_l,\qquad
r_l=r_{l-1}+(K_{eff,l}-1)j_{l-1}
$$

两个步幅 1 的 `3×3` 卷积：第一层感受野为 3，第二层为
$3+(3-1)\times1=5$。堆叠小卷积既扩大感受野，又在中间加入非线性。

## 最小手算

输入与核为：

$$
X=\begin{bmatrix}1&2&0\\0&1&3\\2&1&0\end{bmatrix},\quad
W=\begin{bmatrix}1&0\\0&-1\end{bmatrix}
$$

步幅 1、无填充时输出是 `2×2`。左上角为
$1\times1+2\times0+0\times0+1\times(-1)=0$；右上角为
$2-3=-1$。完整输出为：

$$
Y=\begin{bmatrix}0&-1\\-1&1\end{bmatrix}
$$

## NumPy 复刻卷积

```python
import numpy as np

np.random.seed(42)
x = np.array([[1., 2., 0.], [0., 1., 3.], [2., 1., 0.]])
kernel = np.array([[1., 0.], [0., -1.]])
out = np.empty((2, 2))
for i in range(2):
    for j in range(2):
        out[i, j] = np.sum(x[i:i + 2, j:j + 2] * kernel)

expected = np.array([[0., -1.], [-1., 1.]])
assert np.allclose(out, expected)
print(out)
```

这段代码刻意不做自动微分，只验证“滑动窗口、逐元素乘、求和”三个动作。

## PyTorch 等价实验

```python
import numpy as np
import torch
from torch import nn

np.random.seed(42)
torch.manual_seed(42)
x_np = np.array(
    [[1., 2., 0.], [0., 1., 3.], [2., 1., 0.]], dtype=np.float32
)
w_np = np.array([[1., 0.], [0., -1.]], dtype=np.float32)

manual = np.empty((2, 2))
for i in range(2):
    for j in range(2):
        manual[i, j] = np.sum(x_np[i:i + 2, j:j + 2] * w_np)

conv = nn.Conv2d(1, 1, kernel_size=2, bias=False)
with torch.no_grad():
    conv.weight.copy_(torch.tensor(w_np)[None, None])
x = torch.tensor(x_np)[None, None]  # [B=1,C=1,H=3,W=3]
conv.eval()
with torch.inference_mode():
    y = conv(x)

assert tuple(y.shape) == (1, 1, 2, 2)
assert np.allclose(y[0, 0].numpy(), manual, atol=1e-6)
print(y[0, 0])
```

## 实验结果怎样解释

手工实现与 `Conv2d` 一致，证明了本例的运算和 PyTorch 的定义一致；它没有证明 CNN 一定能识别真实缺陷。后者还取决于标注质量、覆盖的缺陷形态、采集偏差和独立验证。真正训练时还应把 CNN 与规则、MLP 和人工抽检成本比较。

## 训练与推理差异

卷积本身在训练和推理时公式相同，但模型中的 BatchNorm、Dropout 会切换行为。训练时调用 `model.train()`；验证和推理调用 `model.eval()` 与 `torch.inference_mode()`。推理还可能使用量化、固定输入尺寸或批处理，这些优化必须重新验证数值、召回率和延迟。

## 数据与验证风险

- 同一产品的连拍图、裁剪块和增强副本必须位于同一数据分区。
- 图像归一化均值和方差只从训练集估计。
- 拍摄设备、班次、材质和缺陷类别要做切片评估。
- 数据增强只用于训练集，并确保不会改变标签含义。
- 显著图或热力图只说明模型敏感区域，不等于因果解释。

参见[数据泄漏](../H-机器学习/05-数据泄漏.md)和[验证设计](../H-机器学习/11-验证设计.md)。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 报通道数不匹配 | 输入用了 `[B,H,W,C]` | 打印输入和首层权重形状 |
| 线性层维度错误 | 输出尺寸计算遗漏步幅或填充 | 逐层打印 `[B,C,H,W]` |
| 训练高分验证差 | 重复图片泄漏或模型记住背景 | 按产品分组、遮挡背景复验 |
| 小缺陷漏检 | 下采样过早或分辨率不足 | 检查缺陷像素大小和特征图 |
| 损失不下降 | 学习率、标签或归一化错误 | 先过拟合一个小批次 |
| 推理结果波动 | 未进入评估模式 | 检查 `eval` 和随机增强 |

## 适用与不适用场景

CNN 适合局部空间结构重要、同一模式可跨位置复用的图像、音频时频图和网格数据。数据很少且规则清楚时先用传统视觉；关系不是规则网格时考虑[图神经网络](15-图神经网络.md)；任务需要全局、内容自适应交互时可比较[注意力机制](08-注意力机制.md)。

## 学习收益

你应能追踪 `[B,C,H,W]`，手算卷积，推导输出尺寸与感受野，说明权重共享的价值，并设计避免相邻图像泄漏的验证方案。

## 给别人讲清楚

“卷积核像一个可学习的小窗口，在整张图上重复使用。浅层找局部边缘，堆叠后看见更大区域；共享窗口使参数比逐像素全连接少得多。”

## 自检问题

1. 为什么 PyTorch 的图像通道位于第二维？
2. `3×3` 卷积、步幅 2、填充 1 如何改变 `8×8` 输入？
3. 两层 `3×3` 卷积的感受野为什么是 `5×5`？
4. 为什么随机拆分同一产品的连拍图会使指标虚高？

## 相关主题

- [多层感知机 MLP](01-多层感知机%20MLP.md)
- [神经网络反向传播](02-神经网络反向传播.md)
- [注意力机制](08-注意力机制.md)
- [PyTorch 模型训练](10-PyTorch%20模型训练.md)

## 资料来源

- PyTorch, [Conv2d](https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html)，访问日期：2026-09-10。
- Yann LeCun et al., [Gradient-Based Learning Applied to Document Recognition](https://doi.org/10.1109/5.726791), 1998，访问日期：2026-09-10。
- Christopher Olah, [Understanding Convolutions](https://colah.github.io/posts/2014-07-Understanding-Convolutions/)，访问日期：2026-09-10。
