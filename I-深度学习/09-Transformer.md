---
type: concept
domain:
  - Deep Learning
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Transformer 架构
tags:
  - deep-learning
  - transformer
  - sequence-modeling
---

# Transformer

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么深度学习问题

Transformer 把注意力、前馈网络、残差和归一化组装成可堆叠的序列建模架构。它让一个序列内的位置并行交换信息，避免 RNN 必须按时间步串行计算，并通过位置表示补回顺序信息。

本篇解释架构和最小训练机制。大模型预训练、指令微调、对齐、生成策略与服务不在这里展开，参见[大模型 LLM](../J-大模型%20LLM/00-大模型%20LLM-MOC.md)。

## 不理解会造成什么错误

- 以为自注意力天然知道顺序，忘记加入位置表示。
- 因果 Mask 方向错误，让语言模型训练时偷看后续答案。
- 残差两端形状不一致，或把归一化轴写成批次轴。
- 把训练时一次处理全序列与推理时逐步生成混为一谈。
- 只扩大层数和宽度，不监控显存、梯度、数据和验证边界。

## 它在训练系统中的位置

离散 Token 或连续事件先变成 `[B,T,D]` 表示，再加入位置信息，经过若干 Transformer 块，最后由任务头变成分类分数或下一位置分数。每个块内部是：

```text
[B,T,D]
→ 归一化 → 多头注意力 → 残差相加 [B,T,D]
→ 归一化 → 逐位置前馈 → 残差相加 [B,T,D]
```

注意力负责位置间通信，前馈网络负责每个位置内部的非线性变换，残差提供短路径，归一化控制表示尺度。

## 从事件序列预测开始

给定用户最近 $T$ 个操作，预测下一类操作：

- 输入：事件 ID 与位置，嵌入后为 `[B,T,D]`；
- 目标：每个位置的下一事件类别 `[B,T]`；
- 输出：类别 Logits `[B,T,C]`；
- 损失：只在非 Padding 位置计算交叉熵；
- Mask：每个位置只能读取自己和过去；
- 指标：交叉熵、Top-k 命中和线上延迟。

错误的因果 Mask 会产生非常漂亮却完全无效的离线指标，因为答案已经出现在输入右侧。

## 先建立简单基线

先比较事件频率、最近事件转移表、窗口平均池化和 LSTM。Transformer 的优势应来自长距离依赖和并行训练，而不是更多参数。相同参数预算、相同输入窗口与相同验证边界，才是可信比较。

## 张量形状与数据流

设批大小 $B$、长度 $T$、隐藏维度 $D$、头数 $H$，每头维度 $d_k=D/H$：

```text
Token/事件 ID                         [B,T]
嵌入与位置相加                        [B,T,D]
Q、K、V 重排                          [B,H,T,d_k]
注意力分数                            [B,H,T,T]
多头拼接                              [B,T,D]
前馈中间层                            [B,T,D_ff]
块输出                                [B,T,D]
任务头                                [B,T,C] 或 [B,C]
```

$D$ 必须能被 $H$ 整除。分类任务可以读取专用汇总位置或按 Mask 池化；因果预测保留每个时间步输出。

## Transformer 块的完整计算

以下采用常见的 Pre-Norm 形式。输入为 $X\in\mathbb{R}^{B\times T\times D}$：

$$
U=X+\operatorname{MHA}(\operatorname{LN}(X),M)
$$

$$
Y=U+\operatorname{FFN}(\operatorname{LN}(U))
$$

其中前馈网络对每个位置独立且共享参数：

$$
\operatorname{FFN}(x)=\phi(xW_1+b_1)W_2+b_2
$$

$W_1$ 把 $D$ 扩展到 $D_{ff}$，$W_2$ 再投回 $D$，所以能与残差相加。$\phi$ 常用 ReLU 或 GELU。

### 残差为什么帮助梯度传播

若一层写成 $y=x+F(x)$，则：

$$
\frac{\partial L}{\partial x}
=\frac{\partial L}{\partial y}
\left(I+\frac{\partial F}{\partial x}\right)
$$

梯度包含恒等路径 $I$，不必完全穿过复杂子层。它改善深层优化，但不能自动修复错误学习率、坏数据或数值溢出。

### LayerNorm 在哪个轴计算

对每个样本、每个位置的 $D$ 维向量计算：

$$
\mu=\frac1D\sum_{i=1}^D x_i,\qquad
\sigma^2=\frac1D\sum_{i=1}^D(x_i-\mu)^2
$$

$$
\operatorname{LN}(x_i)=
\gamma_i\frac{x_i-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta_i
$$

它不混合不同样本或时间位置，因此推理不需要维护运行均值。

## 为什么必须加入位置表示

若没有位置信息，自注意力对输入位置的同一置换会产生相同置换的输出，即只知道“有哪些内容”，不知道原始次序。最初论文使用正弦余弦位置编码：

$$
PE_{pos,2i}=\sin\left(pos/10000^{2i/D}\right)
$$

$$
PE_{pos,2i+1}=\cos\left(pos/10000^{2i/D}\right)
$$

把 $PE$ 与 Token 嵌入逐元素相加，形状仍为 `[B,T,D]`。位置表示也可以学习，但必须考虑训练长度之外的行为。

## 因果 Mask 的严格含义

预测位置 $t+1$ 时，位置 $t$ 只能访问索引 $j\le t$：

$$
M_{t,j}=\begin{cases}
0,&j\le t\\
-\infty,&j>t
\end{cases}
$$

加到 Softmax 前的分数后，未来位置的概率严格为零。正确性不能只看矩阵图，至少应断言：修改未来输入不会改变过去输出。

## 最小手算

对向量 $x=[1,2,3]$，均值 $\mu=2$，方差
$[(1-2)^2+0+(3-2)^2]/3=2/3$。令 $\gamma=1,\beta=0,\epsilon=0$：

$$
\operatorname{LN}(x)=
[-1,0,1]/\sqrt{2/3}
\approx[-1.225,0,1.225]
$$

若注意力子层给出 $F(x)=[0.1,-0.2,0.3]$，残差输出为
$[1.1,1.8,3.3]$。子层学得很差时，恒等路径仍保留原输入。

## NumPy 复刻位置编码与归一化

```python
import numpy as np

np.random.seed(42)
T, D = 4, 6
position = np.arange(T)[:, None]
frequency = np.exp(np.arange(0, D, 2) * (-np.log(10000.0) / D))
pe = np.zeros((T, D))
pe[:, 0::2] = np.sin(position * frequency)
pe[:, 1::2] = np.cos(position * frequency)

x = np.array([[[1., 2., 3., 4., 5., 6.]]])  # [B=1,T=1,D=6]
mean = x.mean(axis=-1, keepdims=True)
var = ((x - mean) ** 2).mean(axis=-1, keepdims=True)
normalized = (x - mean) / np.sqrt(var + 1e-5)

assert pe.shape == (4, 6)
assert np.allclose(pe[0, 0::2], 0.0)
assert np.allclose(pe[0, 1::2], 1.0)
assert np.allclose(normalized.mean(axis=-1), 0.0, atol=1e-7)
assert np.allclose(normalized.var(axis=-1), 1.0, atol=1e-4)
print("position", pe.shape, "normalized variance", normalized.var())
```

## PyTorch 最小编码块与因果断言

```python
import numpy as np
import torch
from torch import nn

np.random.seed(42)
torch.manual_seed(42)

class TinyBlock(nn.Module):
    def __init__(self, d_model=8, heads=2, d_ff=16):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.attn = nn.MultiheadAttention(
            d_model, heads, dropout=0.0, batch_first=True
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.ReLU(), nn.Linear(d_ff, d_model)
        )

    def forward(self, x, causal_mask):
        z = self.norm1(x)
        attended, weights = self.attn(
            z, z, z, attn_mask=causal_mask,
            need_weights=True, average_attn_weights=False
        )
        x = x + attended
        return x + self.ffn(self.norm2(x)), weights

B, T, D = 2, 5, 8
x = torch.randn(B, T, D)
# MultiheadAttention 的布尔 Mask 中 True 表示禁止关注。
causal_mask = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
model = TinyBlock(d_model=D, heads=2)
model.eval()
with torch.inference_mode():
    original, weights = model(x, causal_mask)
    changed = x.clone()
    changed[:, 3:] += 100.0  # 只改未来位置
    changed_out, _ = model(changed, causal_mask)

assert tuple(original.shape) == (B, T, D)
assert tuple(weights.shape) == (B, 2, T, T)
assert torch.all(weights.masked_select(causal_mask[None, None]) == 0)
assert torch.allclose(original[:, :3], changed_out[:, :3], atol=1e-5)

# 一个训练步验证梯度能流过完整块。
model.train()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
target = torch.zeros_like(x)
optimizer.zero_grad()
prediction, _ = model(x, causal_mask)
loss = nn.functional.mse_loss(prediction, target)
loss.backward()
assert all(p.grad is not None for p in model.parameters())
optimizer.step()
print("output", tuple(prediction.shape), "loss", round(loss.item(), 4))
```

断言同时检查了被屏蔽权重为零，以及改变索引 3、4 不会影响索引 0、1、2 的输出。

## 编码器与因果解码的区别

- **双向编码器：** 每个位置可查看全部非 Padding 位置，适合整段分类和表征。
- **因果模型：** 每个位置只能查看过去与自己，适合下一步预测。
- **编码器解码器：** 解码器除因果自注意力外，还通过交叉注意力读取编码器输出。

架构名称不决定数据是否合规；在线特征本身仍需符合预测时可用性。

## 实验结果怎样解释

实验验证块的形状、梯度链路和因果不可见性。它没有说明深层 Transformer 已收敛，也不能外推到长序列吞吐。正式实验要与 LSTM、池化基线比较验证损失、业务指标、训练成本、峰值内存和不同长度切片。

## 训练与推理差异

训练时，因果 Mask 允许所有位置并行计算损失；Dropout 开启，保存反向图。逐步推理时，`eval()` 关闭 Dropout，`inference_mode()` 不记录梯度，并缓存历史 Key/Value。缓存使每步不必重算过去，但会占用随序列长度增长的内存。

完整序列分类不一定需要因果 Mask；下一步预测必须需要。不要把 `eval()` 误当成因果约束，它只改变层的运行模式。

## 数据与验证风险

- 下一步标签要与输入严格错开一位，Padding 标签需从损失中排除。
- 训练与验证按实体、会话或时间边界拆分，避免相邻窗口重复。
- 输入特征的生成时间必须早于预测时点，模型内 Mask 无法修复外部泄漏。
- 学习位置编码在超过训练长度时可能失效，应单独验证长度外推。
- 调参只使用验证集，测试集保留到最终一次评估。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 训练损失低得异常 | 标签未错位或看到了未来 | 因果断言、输入标签索引 |
| 残差相加报错 | 注意力或 FFN 未投回 $D$ | 两个分支的 `[B,T,D]` |
| 各位置表现相似 | 没有位置表示 | 嵌入与位置相加步骤 |
| 深层训练不稳定 | 归一化位置、初始化或学习率 | 梯度范数、Pre-Norm、预热 |
| 长序列内存不足 | 注意力矩阵为 $T^2$ | 长度分布、批大小、注意力实现 |
| 生成越来越慢 | 未缓存 Key/Value | 每步计算图和缓存长度 |
| Padding 改变输出 | Padding Mask 缺失或方向错误 | 改动填充值并做不变性断言 |

## 适用与不适用场景

Transformer 适合需要全局交互、并行训练和可扩展表示的序列任务。数据少、序列短或严格低延迟时，线性模型、CNN 或 LSTM 可能更省资源。标准注意力在超长序列上成本为 $O(T^2)$，不能只靠缩小批次掩盖架构不匹配。

## 学习收益

你应能追踪 `[B,T,D]` 到 `[B,H,T,T]`，解释位置、注意力、残差、LayerNorm 和 FFN 的职责，证明因果不可见性，并区分训练并行与逐步推理。

## 给别人讲清楚

“Transformer 让序列中的位置通过注意力交换信息，再让每个位置独立做非线性加工。位置编码告诉它顺序，Mask 限定能看哪里，残差和归一化帮助许多层稳定堆叠。”

## 自检问题

1. 没有位置表示时，自注意力缺少什么信息？
2. 为什么 FFN 的输出维度必须回到 $D$？
3. `eval()` 为什么不能替代因果 Mask？
4. 怎样用一次输入修改实验验证模型没有读取未来？
5. 训练和逐步推理的计算路径有何不同？

## 相关主题

- [注意力机制](08-注意力机制.md)
- [神经网络参数初始化](03-神经网络参数初始化.md)
- [PyTorch 模型训练](10-PyTorch%20模型训练.md)
- [深度学习训练诊断](11-深度学习训练诊断.md)

## 资料来源

- Ashish Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762), 2017，访问日期：2026-09-10。
- Kaiming He et al., [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385), 2015，访问日期：2026-09-10。
- Jimmy Lei Ba, Jamie Ryan Kiros, Geoffrey E. Hinton, [Layer Normalization](https://arxiv.org/abs/1607.06450), 2016，访问日期：2026-09-10。
- PyTorch, [MultiheadAttention](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)，访问日期：2026-09-10。
- PyTorch, [TransformerEncoderLayer](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html)，访问日期：2026-09-10。
