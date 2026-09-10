---
type: concept
domain:
  - LLM
depth: L3
importance: common
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - LoRA
  - 低秩适配
tags:
  - llm
  - lora
  - parameter-efficient-fine-tuning
---

# LoRA 参数高效微调

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

全参数微调要为每个任务保存并优化整个大模型。LoRA 冻结原权重，只训练低秩增量，用更少的可训练参数和优化器状态适配任务。它降低训练与多任务存储成本，但不会消除底座的前向和反向计算。

## 不理解会造成什么错误

- 以为冻结参数后不再经过底座计算，错误估算显存和时间。
- 矩阵方向或缩放写错，适配器能运行却语义错误。
- 把“可训练参数少”误当成数据与安全风险少。
- 合并适配器后重复应用 LoRA，把增量加了两次。
- 忘记保存底座版本与目标层列表，适配器无法复现。

## 它在 LLM 链路中的位置

LoRA 是 SFT 或偏好优化的参数化方式，不是新的训练目标：

```text
冻结底座 W + 可训练 A、B
→ SFT 或偏好损失 → 保存 Adapter 与配置
→ 动态加载或合并到 W
```

## 从多租户客服适配开始

一个基础模型服务多个业务线，各业务只需学习术语与回答风格。共享底座、分别保存 LoRA Adapter 比复制多个完整模型更省存储。

基线仍是 Prompt 和少样本示例。如果基线已满足要求，LoRA 的训练、版本路由和回归成本并不划算。

## 低秩增量的形状

采用列向量约定：

$$
y=Wx,\qquad W\in\mathbb R^{d_{out}\times d_{in}}
$$

LoRA 冻结 $W$，令：

$$
W'=W+\Delta W,\qquad
\Delta W=\frac{\alpha}{r}BA
$$

其中 $A\in\mathbb R^{r\times d_{in}}$，$B\in\mathbb R^{d_{out}\times r}$，秩 $r$ 远小于输入输出维度。前向无需生成大矩阵：

$$
y=Wx+\frac{\alpha}{r}B(Ax)
$$

输入先从 $d_{in}$ 压到 $r$，再投回 $d_{out}$。

## 参数量怎样推导

全量权重有 $d_{out}d_{in}$ 个参数，LoRA 有：

$$
N_{\mathrm{LoRA}}=r(d_{in}+d_{out})
$$

两者比例为：

$$
\frac{N_{\mathrm{LoRA}}}{N_{\mathrm{full}}}
=\frac{r(d_{in}+d_{out})}{d_{in}d_{out}}
$$

若 $d_{in}=d_{out}=4096,r=8$，全量有 `16,777,216` 个参数，LoRA 有 `65,536` 个，约为 `0.39%`。这是单个矩阵的参数比例，不代表总显存恰好同比缩小。

## 为什么能够合并

训练完成后 $A$、$B$ 是常量。由分配律：

$$
Wx+\frac{\alpha}{r}B(Ax)
=\left(W+\frac{\alpha}{r}BA\right)x
$$

所以可预先计算 $W_{\mathrm{merged}}=W+\alpha BA/r$。动态 Adapter 便于切换任务；合并减少额外算子，但必须记录来源并避免重复合并。

## 最小手算

设：

$$
W=\begin{bmatrix}1&0\\0&1\end{bmatrix},\quad
A=\begin{bmatrix}1&-1\end{bmatrix},\quad
B=\begin{bmatrix}2\\1\end{bmatrix}
$$

$r=\alpha=1$ 时，$BA=[[2,-2],[1,-1]]$，$W'=[[3,-2],[1,0]]$。输入 $x=[1,2]^T$，动态路径得到 $Wx+B(Ax)=[1,2]+[-2,-1]=[-1,1]$；合并路径同样得到 `[-1,1]`。

## PyTorch 可执行实验

实验验证动态与合并等价，并确认只有 Adapter 获得梯度。

```python
import torch
from torch import nn

torch.manual_seed(47)

class LoRALinear(nn.Module):
    def __init__(self, in_features, out_features, rank=2, alpha=4.0):
        super().__init__()
        self.weight = nn.Parameter(
            torch.randn(out_features, in_features) * 0.1,
            requires_grad=False,
        )
        self.A = nn.Parameter(torch.randn(rank, in_features) * 0.05)
        self.B = nn.Parameter(torch.zeros(out_features, rank))
        self.scale = alpha / rank

    def forward(self, x):
        return x @ self.weight.T + self.scale * (x @ self.A.T) @ self.B.T

    def merged_weight(self):
        return self.weight + self.scale * (self.B @ self.A)

layer = LoRALinear(4, 3)
x = torch.randn(5, 4)
target = torch.randn(5, 3)
optimizer = torch.optim.SGD([layer.A, layer.B], lr=0.2)

optimizer.zero_grad()
loss = nn.functional.mse_loss(layer(x), target)
loss.backward()
assert layer.weight.grad is None
assert layer.B.grad is not None and layer.B.grad.norm() > 0
assert layer.A.grad is not None and torch.all(layer.A.grad == 0)
optimizer.step()

optimizer.zero_grad()
loss = nn.functional.mse_loss(layer(x), target)
loss.backward()
assert layer.weight.grad is None
assert layer.A.grad.norm() > 0 and layer.B.grad.norm() > 0

with torch.no_grad():
    dynamic = layer(x)
    merged = x @ layer.merged_weight().T
assert torch.allclose(dynamic, merged, atol=1e-6)
trainable = sum(p.numel() for p in (layer.A, layer.B))
assert trainable == 2 * (4 + 3)
print("trainable:", trainable, "max diff:", (dynamic - merged).abs().max().item())
```

## 实验结果解释

冻结的 `weight.grad` 始终为空，说明底座没有梯度。零初始化 $B$ 让起始输出等于底座，也使第一步 $A$ 梯度为零；$B$ 更新后两者都获得信号。动态与合并输出一致验证了代数等价，不证明量化合并后仍完全无误差。

## 目标层秩与缩放

Attention 的 Query、Key、Value、输出投影和 MLP 都可适配，但目标更多不总是更好。秩越大，表达能力和状态成本越高。应从较小秩、明确目标层和固定预算开始验证。

$\alpha/r$ 让改变秩时更新尺度更可控，但不是免调参保证。Dropout、学习率、初始化和数据都会影响结果。

## 训练成本与部署影响

LoRA 减少可训练参数、梯度和优化器状态，却仍需通过冻结层传播激活和梯度。激活常是训练显存大头。量化底座配合 LoRA 可继续节省显存，但会引入误差与算子兼容问题。

动态加载便于共享底座和切换租户，但增加路由、缓存与首请求延迟；合并便于单任务部署，却产生新完整权重。两种方式都要绑定底座哈希、Tokenizer、模板和配置。

## 数据评测与安全风险

- Adapter 可覆盖底座安全行为，必须重做越权和危险能力评测。
- 不同租户数据与 Adapter 必须隔离。
- 验证数据按来源或用户拆分，模板改写不可跨集合。
- 合并模型继承底座和训练数据许可限制。
- 参数量不能代替端到端成本与延迟测量。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 初始输出不同于底座 | $B$ 未零初始化或缩放错 | 固定输入前后对照 |
| 所有梯度都为空 | Adapter 未参与前向 | 参数名、计算图、优化器 |
| 底座发生变化 | 冻结遗漏 | 训练前后权重哈希 |
| 合并输出不同 | 转置、缩放或量化顺序错 | 小矩阵动态合并对照 |
| 加载维度错误 | 底座或目标层不同 | 模型哈希、层名、rank |
| 多租户回答串线 | 路由或缓存键错误 | 租户隔离与并发测试 |

## 适用与不适用场景

LoRA 适合显存有限、多任务共享底座或频繁保存适配版本。需要彻底改变大量能力时低秩约束可能不足；只需少量格式引导时 Prompt 更简单；事实更新优先 RAG。使用 LoRA 与选择 SFT、DPO 等目标是两个不同决策。

## 学习收益

你应能追踪矩阵形状，推导参数量和合并等价性，解释零初始化行为，验证只有 Adapter 获得梯度，并估算真实训练与部署边界。

## 给别人讲清楚

“LoRA 不重写整本书，而是在书旁放两张很窄的修订表。输入先压缩再展开，两表相乘就是对原权重的低秩修订。”

## 自检问题

1. 为什么参数少却仍要执行底座计算？
2. $A$、$B$ 的形状为何保证 $BA$ 与 $W$ 相同？
3. 为什么 $B=0$ 时第一步 $A$ 梯度为零？
4. 动态与合并部署各有什么代价？

## 相关主题

- [大模型监督微调 SFT](<11-大模型监督微调 SFT.md>)
- [RLHF 与 DPO](<17-RLHF 与 DPO.md>)
- [大模型量化](15-大模型量化.md)
- [神经网络优化器](../I-深度学习/04-神经网络优化器.md)

## 资料来源

- Edward J. Hu 等, [LoRA](https://arxiv.org/abs/2106.09685), 2021，访问日期：2026-09-10。
- Hugging Face PEFT, [LoRA](https://huggingface.co/docs/peft/package_reference/lora)，访问日期：2026-09-10。
- Hugging Face PEFT, [Adapter injection](https://huggingface.co/docs/peft/developer_guides/low_level_api)，访问日期：2026-09-10。
