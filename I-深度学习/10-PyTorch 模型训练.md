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
  - PyTorch 训练循环
tags:
  - pytorch
  - training-loop
  - validation
---

# PyTorch 模型训练

<!-- markdownlint-disable MD013 -->

## 它解决什么深度学习问题

模型结构只定义“怎样计算”，训练循环才把数据、损失、梯度、参数更新和验证连成一个可信过程。本主题解决的不是让代码跑起来，而是让一次实验可解释、可复现、可验证、可恢复。

## 不理解会造成什么错误

- 忘记清空梯度，当前批次会叠加之前批次的梯度。
- 验证时仍处于训练模式，Dropout 和 BatchNorm 使指标不稳定。
- 用验证集更新参数，得到带泄漏的过高分数。
- 只保存模型权重，中断后无法从相同步数和优化器状态继续。
- 把不同设备上的模型和张量混用，引发运行错误。

## 它在训练系统中的位置

```text
Dataset → DataLoader → Module 前向 → 损失
                                  ↓
                         backward → optimizer.step
                                  ↓
                   独立验证 → 选择检查点 → 测试或推理
```

它消费已经定义好的特征、标签、模型与损失，产出训练后的参数、验证记录和检查点。数据拆分应先按[验证设计](../H-机器学习/11-验证设计.md)确定。

## 从一个 AI 案例开始

假设用两个传感器读数预测设备是否即将故障：

- 每个样本是两个浮点特征，批张量形状为 `[B,2]`；
- 标签是 0 或 1，形状为 `[B]`；
- 模型输出两个类别的 logits，形状为 `[B,2]`；
- 损失使用交叉熵，业务指标使用准确率；
- 漏报故障成本更高时，最终还应按业务成本调整阈值，而不能只看准确率。

训练集用于求梯度，验证集用于比较配置，测试集只在方案冻结后评估一次。

## 先建立简单基线

先用单个线性层 `Linear(2, 2)`。如果线性模型已经达到目标，不必立即加深网络。复杂模型至少要与多数类预测、线性分类器和上一版线上模型比较。

## 张量形状与数据流

小型分类网络的数据流如下：

```text
x [B,2]
→ Linear(2,8) → z [B,8]
→ ReLU        → h [B,8]
→ Linear(8,2) → logits [B,2]
→ CrossEntropy(logits, y [B]) → loss []
```

`loss` 是标量。反向传播从它出发，为每个可训练参数生成同形状的 `parameter.grad`。

## 核心机制

一个训练批次必须按固定语义执行：

1. `optimizer.zero_grad()` 清除旧梯度；
2. `logits = model(x)` 记录本次前向计算图；
3. `loss = criterion(logits, y)` 衡量预测误差；
4. `loss.backward()` 用链式法则填充每个参数的 `.grad`；
5. `optimizer.step()` 按优化规则更新参数。

验证阶段不执行后三步。`model.eval()` 切换 Dropout、BatchNorm 等模块的行为；`torch.inference_mode()` 关闭 Autograd 记录，降低不必要的内存与调度开销。两者作用不同，所以通常同时使用。

## 损失与参数更新推导

设一个样本的 logits 为 $z_1,\ldots,z_C$，真实类别为 $y$。Softmax 概率和交叉熵为：

$$
p_c=\frac{e^{z_c}}{\sum_{j=1}^{C}e^{z_j}},\qquad L=-\log p_y
$$

把 $L=-z_y+\log\sum_j e^{z_j}$ 对 $z_c$ 求导：

$$
\frac{\partial L}{\partial z_c}=p_c-\mathbb{1}(c=y)
$$

若线性层为 $z=xW+b$，链式法则给出：

$$
\frac{\partial L}{\partial W}=x^\top\frac{\partial L}{\partial z}
$$

最简单的 SGD 更新是 $W\leftarrow W-\eta\,\partial L/\partial W$。PyTorch 自动完成求导，但训练循环仍必须决定何时清梯度、求导和更新。

## 最小手算

二分类 logits 为 `[2, 0]`，真实类别是 0。Softmax 概率约为 `[0.881, 0.119]`，损失为 $-\log 0.881\approx0.127$，对 logits 的梯度为 `[-0.119, 0.119]`。

若输入是 `[1, 2]`，则权重梯度是外积：

$$
\begin{bmatrix}1\\2\end{bmatrix}
\begin{bmatrix}-0.119&0.119\end{bmatrix}
=
\begin{bmatrix}-0.119&0.119\\-0.238&0.238\end{bmatrix}
$$

这说明一次样本如何把分类误差传回每个输入到输出的连接。

## 可执行 CPU 实验

下面的实验不下载数据，完整覆盖 Dataset、DataLoader、训练、验证和内存检查点恢复。

```python
import io
import random
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
device = torch.device("cpu")

# 合成故障数据；先固定生成，再明确切分，测试集不参与本实验调参。
x = torch.randn(240, 2)
y = ((1.4 * x[:, 0] - 0.8 * x[:, 1]) > 0).long()
train_ds = TensorDataset(x[:160], y[:160])
valid_ds = TensorDataset(x[160:200], y[160:200])
train_generator = torch.Generator().manual_seed(SEED)
train_loader = DataLoader(train_ds, batch_size=32, shuffle=True,
                          generator=train_generator)
valid_loader = DataLoader(valid_ds, batch_size=40, shuffle=False)

def make_model():
    return nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2))

model = make_model().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.2)

def train_one_epoch(model, loader, optimizer):
    model.train()
    loss_sum = 0.0
    correct = 0
    count = 0
    for features, labels in loader:
        features = features.to(device)
        labels = labels.to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(features)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        loss_sum += loss.item() * labels.numel()
        correct += (logits.argmax(dim=1) == labels).sum().item()
        count += labels.numel()
    return loss_sum / count, correct / count

def evaluate(model, loader):
    model.eval()
    loss_sum = 0.0
    correct = 0
    count = 0
    with torch.inference_mode():
        for features, labels in loader:
            features = features.to(device)
            labels = labels.to(device)
            logits = model(features)
            loss_sum += criterion(logits, labels).item() * labels.numel()
            correct += (logits.argmax(dim=1) == labels).sum().item()
            count += labels.numel()
    return loss_sum / count, correct / count

first_loss = evaluate(model, valid_loader)[0]
for epoch in range(12):
    train_loss, train_acc = train_one_epoch(model, train_loader, optimizer)
valid_loss, valid_acc = evaluate(model, valid_loader)

# 完整训练检查点：模型、优化器、步数和构造模型所需的配置。
checkpoint = {
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "epoch": epoch,
    "config": {"input_dim": 2, "hidden_dim": 8, "classes": 2, "seed": SEED},
    "torch_rng_state": torch.get_rng_state(),
    "loader_rng_state": train_generator.get_state(),
}
buffer = io.BytesIO()
torch.save(checkpoint, buffer)
buffer.seek(0)
loaded = torch.load(buffer, map_location=device, weights_only=True)
restored = make_model().to(device)
restored.load_state_dict(loaded["model"])

probe = x[200:205].to(device)
model.eval()
restored.eval()
with torch.inference_mode():
    before = model(probe)
    after = restored(probe)

assert valid_loss < first_loss
assert valid_acc > 0.85
assert torch.allclose(before, after, atol=1e-7)
assert all(parameter.grad is None for parameter in restored.parameters())
print(round(first_loss, 4), round(valid_loss, 4), round(valid_acc, 3))
```

## 实验结果解释

验证损失下降且准确率超过 0.85，说明循环能在这份合成数据上学习。它不能证明模型适合真实故障数据，也不能证明阈值满足漏报成本。恢复前后 logits 一致，证明权重往返正确；继续训练还必须恢复优化器、步数和随机状态。

## 训练与推理差异

| 项目 | 训练 | 验证与推理 |
| --- | --- | --- |
| 模式 | `model.train()` | `model.eval()` |
| Autograd | 需要计算图 | `inference_mode()` 通常足够 |
| Dropout | 随机丢弃 | 关闭丢弃 |
| BatchNorm | 更新运行统计量 | 使用已保存统计量 |
| 参数更新 | `backward` 与 `step` | 不更新 |

`eval()` 不会自动关闭梯度，`inference_mode()` 也不会自动切换模块模式。

## 数据与验证风险

- 先拆分实体或时间，再拟合归一化、词表和采样规则，避免[数据泄漏](../H-机器学习/05-数据泄漏.md)。
- `shuffle=True` 适合近似独立的训练样本，不适合破坏时间因果关系。
- 不能根据测试集结果反复修改模型；此时测试集已经变成验证集。
- 一个批次的平均损失要按样本数加权，否则最后一个小批次会被高估。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 损失几乎不变 | 没有更新或学习率不合适 | `.grad`、`step()`、参数前后差异 |
| 损失锯齿剧烈 | 学习率过大或批次太小 | 降低学习率、记录批次损失 |
| 验证结果每次变化 | 忘记 `eval()` | Dropout、BatchNorm、随机预处理 |
| 显存或内存持续增长 | 保存了带计算图的张量 | 使用 `.item()` 或 `.detach()` |
| 设备不一致 | 数据没有迁移 | 模型、输入、标签的 `.device` |
| 恢复后不能继续训练 | 只保存模型权重 | 优化器、步数、配置和随机状态 |

## 适用与不适用场景

显式训练循环适合研究、定制损失和需要精确控制状态的项目。成熟训练框架适合多设备、日志和容错需求复杂的工程，但仍应理解底层五步语义。数据很小且表格关系简单时，树模型往往是更好的基线。

## 学习收益

你应能从数据集开始写出没有验证污染的训练循环，解释每一步改变了什么状态，正确切换训练与推理模式，并产出能够继续训练的检查点。

## 给别人讲清楚

“训练循环像一次有纪律的实验：每批先清旧梯度，再预测、算错、反传和更新；验证只观察，不改答案。”

## 自检问题

1. 为什么 `zero_grad()` 通常放在每个训练批次内？
2. `model.eval()` 和 `torch.inference_mode()` 各自改变什么？
3. 想从中断处继续训练，为什么只保存 `state_dict` 不够？

## 相关主题

- [神经网络反向传播](02-神经网络反向传播.md)
- [神经网络优化器](04-神经网络优化器.md)
- [深度学习训练诊断](11-深度学习训练诊断.md)
- [批处理与模型序列化](12-批处理与模型序列化.md)
- [自动微分直觉](../G-AI%20基础/09-自动微分直觉.md)

## 资料来源

- PyTorch, [Datasets and DataLoaders](https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html)，访问日期：2026-09-10。
- PyTorch, [The Fundamentals of Autograd](https://docs.pytorch.org/tutorials/beginner/introyt/autogradyt_tutorial.html)，访问日期：2026-09-10。
- PyTorch, [Saving and Loading Models](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)，访问日期：2026-09-10。
- PyTorch, [Locally disabling gradient computation](https://docs.pytorch.org/docs/stable/notes/autograd.html#locally-disable-grad-doc)，访问日期：2026-09-10。
