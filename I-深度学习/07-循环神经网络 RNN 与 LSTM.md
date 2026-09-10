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
  - RNN
  - LSTM
tags:
  - deep-learning
  - sequence-modeling
  - rnn
---

# 循环神经网络 RNN 与 LSTM

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么深度学习问题

RNN 用一个反复更新的隐藏状态概括已经读过的序列，适合事件流、传感器和文本等顺序不能交换的数据。LSTM 在此基础上加入门控记忆，让重要信息更容易跨越较长距离。

序列统一写成 `[B,T,D]`：批大小、时间步数、每步特征维度。循环层输出通常是每步状态 `[B,T,H]` 和最终状态 `[层数,B,H]`，其中 `H` 是隐藏维度。

## 不理解会造成什么错误

- 将 Padding 当作真实时间步，让短序列的表示被填充值污染。
- 取批次最后一列作为所有样本的最终状态，忽略真实长度不同。
- 认为 LSTM 已彻底消除长依赖问题，忽视优化、容量和计算瓶颈。
- 在线预测时使用未来时间步，造成时序泄漏。
- 忘记截断或分离跨批状态，使计算图无限增长。

## 它在训练系统中的位置

RNN/LSTM 接在逐时间步特征或嵌入之后，把 `[B,T,D]` 转成上下文状态。分类任务读取最终有效状态，序列标注任务读取每个状态。输出进入损失函数，梯度通过时间展开的共享单元反向传播。

## 从设备故障预警开始

每台设备每分钟产生温度、振动和电流三个特征。模型根据最近不等长的观测判断一小时内是否故障：

- 输入：补齐后的 `[B,T,3]` 和真实长度；
- 标签：故障 `1`、正常 `0`；
- 损失：二元交叉熵；
- 指标：故障召回、误报次数、提前量；
- 错误成本：漏报会停线，误报会增加检修。

训练、验证和测试应按设备与时间隔离，不能让同一台设备相邻窗口跨集合。

## 先建立简单基线

先用最后一个观测、窗口均值和线性分类器。它们训练快，也能检验“顺序”是否真的提供额外信号。如果打乱时间后性能不变，复杂循环模型可能只在使用总体统计。

## 张量形状与数据流

```text
输入 x                 [B,T,D]
逐步隐藏状态 h_t       [B,H]
全部输出                [B,T,H]
最终隐藏状态 h_n        [L,B,H]
分类器                  [B,H] → [B,C]
```

`batch_first=True` 只改变输入输出布局，不改变返回的 `h_n` 布局。双向 RNN 会引入方向维，但依赖未来，不适合严格在线预测。

## RNN 怎样保存上下文

最简单的 RNN 更新为：

$$
a_t=x_tW_{xh}+h_{t-1}W_{hh}+b,
\qquad h_t=\tanh(a_t)
$$

$x_t\in\mathbb{R}^{B\times D}$，$h_t\in\mathbb{R}^{B\times H}$。同一组权重在所有时间步复用，所以模型能处理不同长度，也意味着一次参数更新会汇总各时间步贡献。

## 梯度为什么会消失或爆炸

若最终损失 $L$ 依赖 $h_T$，链式法则给出：

$$
\frac{\partial L}{\partial h_t}
=\frac{\partial L}{\partial h_T}
\prod_{k=t+1}^{T}
\frac{\partial h_k}{\partial h_{k-1}}
$$

而

$$
\frac{\partial h_k}{\partial h_{k-1}}
=\operatorname{diag}(1-\tanh^2(a_k))W_{hh}^{\mathsf T}
$$

多个雅可比矩阵连续相乘。若其典型尺度小于 1，远处梯度指数衰减；大于 1，则可能爆炸。这是乘法累积的结果，不只是“序列太长”的口号。梯度裁剪能限制爆炸，但不能恢复已经消失的信号。

## LSTM 怎样建立更平直的记忆路径

LSTM 使用遗忘门、输入门、候选记忆和输出门：

$$
f_t=\sigma(z_tW_f+b_f),\quad
i_t=\sigma(z_tW_i+b_i)
$$

$$
g_t=\tanh(z_tW_g+b_g),\quad
o_t=\sigma(z_tW_o+b_o)
$$

$$
c_t=f_t\odot c_{t-1}+i_t\odot g_t,
\qquad h_t=o_t\odot\tanh(c_t)
$$

其中 $z_t=[x_t,h_{t-1}]$。沿记忆状态的直接导数为
$\partial c_t/\partial c_{t-1}=f_t$。当遗忘门接近 1 时，梯度可沿加法记忆路径保留；这比每步都经过 `tanh` 和循环权重更容易训练，但并非无限记忆保证。

## 最小手算

取标量 RNN：$h_0=0$，$W_{xh}=1$，$W_{hh}=0.5$，偏置为 0，输入为 $[1,0]$。

$$
h_1=\tanh(1)\approx0.7616
$$

$$
h_2=\tanh(0+0.5\times0.7616)\approx0.3634
$$

第二步即使输入为 0，仍保留第一步信息。若把激活换成恒等映射，$h_T$ 对 $h_0$ 的导数是 $0.5^T$，十步后只剩约 $0.001$，直观展示梯度消失。

## NumPy 复刻循环单元

```python
import numpy as np

np.random.seed(42)
x = np.array([1.0, 0.0])
h = 0.0
states = []
for x_t in x:
    h = np.tanh(x_t + 0.5 * h)
    states.append(h)

assert np.allclose(states, [0.76159416, 0.36339948], atol=1e-7)
long_gradient = 0.5 ** 10
assert long_gradient < 0.001
print("states", np.round(states, 4), "ten-step gradient", long_gradient)
```

## PyTorch 等价与 Padding 实验

```python
import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

np.random.seed(42)
torch.manual_seed(42)

# 两个样本真实长度为 4 和 2，补齐后统一为 [B=2,T=4,D=1]。
x = torch.tensor([[[1.], [0.], [1.], [0.]],
                  [[1.], [1.], [0.], [0.]]])
lengths = torch.tensor([4, 2])
lstm = nn.LSTM(input_size=1, hidden_size=3, batch_first=True)
packed = pack_padded_sequence(x, lengths.cpu(), batch_first=True,
                              enforce_sorted=False)
packed_out, (h_n, c_n) = lstm(packed)
out, restored_lengths = pad_packed_sequence(
    packed_out, batch_first=True, total_length=4
)

assert tuple(out.shape) == (2, 4, 3)
assert tuple(h_n.shape) == (1, 2, 3)
assert restored_lengths.tolist() == [4, 2]
assert torch.allclose(out[1, 2:], torch.zeros_like(out[1, 2:]))
assert torch.allclose(h_n[0, 1], out[1, 1], atol=1e-6)

lstm.eval()
with torch.inference_mode():
    packed_eval, (h_eval, _) = lstm(packed)
assert torch.allclose(h_n, h_eval, atol=1e-6)
print("output", tuple(out.shape), "final", tuple(h_n.shape))
```

`pack_padded_sequence` 让循环层跳过 Padding。分类时可直接使用 `h_n`，避免把短样本补齐位置误当最终状态。

## 实验结果怎样解释

NumPy 例子验证状态会携带过去信息，也展示重复乘法造成的衰减。PyTorch 例子验证不等长序列的形状和最终有效状态。它们不能证明 LSTM 必然胜过 RNN；要在相同拆分、参数预算和指标下比较，还要包括无顺序基线。

## 训练与推理差异

无 Dropout 的单层 RNN/LSTM 在训练和推理中单元公式相同。多层模型的层间 Dropout 会受 `train()` 与 `eval()` 控制。流式推理还要明确状态生命周期：新设备开始时清零状态，跨窗口保留状态时应 `detach()`，防止训练图跨批延伸；服务重启时要决定状态是否持久化。

双向模型训练时会读到序列两端，只适合完整序列离线任务。实时告警如果使用双向层，就等价于偷看未来。

## 数据与验证风险

- 滑动窗口高度重叠时，按设备或时间块拆分。
- Padding Mask 和长度必须与截断后的数据同步。
- 只用预测时已经产生的事件，不能用窗口结束后修订的状态。
- 比较 RNN 与 LSTM 时保持嵌入、隐藏维度、训练预算和早停规则可比。
- 在不同长度区间单独报告性能，防止平均指标掩盖长序列退化。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 短序列预测异常 | 读取了 Padding 后的最后一列 | 真实长度、`h_n`、Mask |
| 长序列性能下降 | 梯度消失或容量不足 | 分长度指标、梯度范数、LSTM 基线 |
| 梯度突然极大 | 时间展开累积或学习率过高 | 梯度范数、裁剪阈值、异常批次 |
| 显存随批次增长 | 隐藏状态未 `detach` | 状态是否携带旧计算图 |
| 在线指标异常好 | 双向网络或未来事件泄漏 | 方向配置、特征可用时间 |
| 训练很慢 | Python 逐步循环或序列过长 | 使用框架循环层、长度分桶 |

## 适用与不适用场景

RNN/LSTM 适合流式、状态递推自然、序列不太长或资源受限的任务。长序列需要并行训练和任意位置交互时，通常比较[注意力机制](08-注意力机制.md)与[Transformer](09-Transformer.md)。如果顺序并不重要，聚合统计或 MLP 可能更可靠。

## 学习收益

你应能追踪 `[B,T,D]`，解释时间展开与共享参数，推导梯度连乘，说明 LSTM 的加法记忆路径，并正确处理 Padding 和最终有效状态。

## 给别人讲清楚

“RNN 每读一步就把新信息和旧摘要合成新摘要；反复相乘让远处信号难保留。LSTM 加了一条受门控制的记忆通道，让信息可以选择保留、写入和读出。”

## 自检问题

1. 为什么梯度裁剪不能解决梯度消失？
2. `batch_first=True` 会不会改变 `h_n` 的维度顺序？
3. 为什么短序列不能直接读取补齐批次的最后一列？
4. 双向 LSTM 为什么不适合严格在线预测？

## 相关主题

- [神经网络反向传播](02-神经网络反向传播.md)
- [注意力机制](08-注意力机制.md)
- [Transformer](09-Transformer.md)
- [批处理与模型序列化](12-批处理与模型序列化.md)

## 资料来源

- PyTorch, [RNN](https://docs.pytorch.org/docs/stable/generated/torch.nn.RNN.html)，访问日期：2026-09-10。
- PyTorch, [LSTM](https://docs.pytorch.org/docs/stable/generated/torch.nn.LSTM.html)，访问日期：2026-09-10。
- Sepp Hochreiter and Jürgen Schmidhuber, [Long Short-Term Memory](https://doi.org/10.1162/neco.1997.9.8.1735), 1997，访问日期：2026-09-10。
- Razvan Pascanu, Tomas Mikolov, Yoshua Bengio, [On the Difficulty of Training Recurrent Neural Networks](https://proceedings.mlr.press/v28/pascanu13.html), 2013，访问日期：2026-09-10。
