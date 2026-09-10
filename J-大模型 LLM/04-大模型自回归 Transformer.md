---
type: concept
domain:
  - LLM
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Decoder Only Transformer
  - 因果 Transformer
tags:
  - autoregressive-model
  - transformer
  - causal-attention
---

# 大模型自回归 Transformer

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

自回归 Transformer 根据已经出现的 Token，预测下一个 Token 的概率分布。它把“续写一个 Token”反复执行，就能生成回答、代码和结构化文本。因果约束保证位置 $t$ 只能读取自己和过去，不能在训练时偷看未来答案。

通用注意力、残差和归一化的结构原理见[Transformer](../I-深度学习/09-Transformer.md)。本篇只讲 LLM 特有的 decoder-only 数据流、标签移位、因果性与逐步生成。

## 不理解会造成什么错误

- 标签没有右移，模型学成复制当前 Token，而不是预测下一个 Token。
- 因果 Mask 方向写反，训练损失异常低，真实生成却失败。
- 以为训练和生成都必须逐 Token 计算，浪费训练并行能力。
- 把每个位置的 `[V]` Logits 当成已经归一化的概率。
- 把较低预训练损失等同于回答真实、安全或遵循指令。

## 它在 LLM 链路中的位置

```text
文本 → Token ID [B,T] → Token 与位置表示 [B,T,D]
→ N 个因果 Transformer 块 [B,T,D]
→ 输出投影 [B,T,V] → 下一个 Token 分布
→ 采样一个 Token → 追加到序列 → 重复
```

$B$ 是批大小，$T$ 是当前序列长度，$D$ 是隐藏维度，$V$ 是词表大小。训练时输出与右移一位的标签计算损失；推理时只消费最后位置的 Logits。

## 从客服回答生成开始

用户输入订单状态和问题，模型逐 Token 生成回复：

- 输入：系统指令、业务上下文和用户问题的 Token；
- 输出：回复 Token，直到终止符或长度上限；
- 质量指标：任务完成率、事实支持率、拒答准确率；
- 性能指标：首 Token 延迟、逐 Token 延迟和峰值显存；
- 错误成本：编造退款状态比措辞不自然更严重。

最重要的系统边界是：模型预测“文本上可能接什么”，它没有自动获得订单真相。动态事实仍需受控上下文或工具提供。

## 先建立简单基线

先比较固定模板、检索已有答案和 unigram/bigram 转移表。它们能揭示任务是否真的需要开放生成。若回复结构固定、错误成本高，模板或结构化工具通常比自由生成更稳定。

## 输入输出与张量流

设 $D=H d_k$，$H$ 是注意力头数：

| 环节 | 张量形状 | 说明 |
| --- | --- | --- |
| Token ID | `[B,T]` | 离散词表编号 |
| 隐藏表示 | `[B,T,D]` | Token 与位置信息 |
| Q K V | `[B,H,T,d_k]` | 每头查询、键和值 |
| 注意力分数 | `[B,H,T,T]` | 每个位置对各历史位置的分数 |
| 块输出 | `[B,T,D]` | 残差后形状不变 |
| 词表 Logits | `[B,T,V]` | 每个位置预测下一 Token |

输出投影常写成 $Z=HW_{out}+b$。有些模型让 $W_{out}$ 与输入 Embedding 共享权重，但这不是自回归成立的必要条件。

## 联合概率为什么能逐步生成

概率链式法则把 Token 序列分解为：

$$
p(x_1,\ldots,x_T)
=\prod_{t=1}^{T}p(x_t\mid x_{<t})
$$

取对数后，乘积变成求和：

$$
\log p(x_1,\ldots,x_T)
=\sum_{t=1}^{T}\log p(x_t\mid x_{<t})
$$

所以最大化整段文本的似然，等价于让每个位置的真实下一 Token 概率尽量大。平均负对数似然为：

$$
L=-\frac{1}{N}\sum_{t\in\mathcal V}
\log p_\theta(x_{t+1}\mid x_{\le t})
$$

$\mathcal V$ 是参与损失的有效位置，$N=|\mathcal V|$。Padding、跨文档边界或提示部分可以按训练目标排除。

## 标签为什么右移一位

Token 序列为 `[BOS, 我, 喜欢, AI, EOS]` 时：

```text
模型输入：BOS  我    喜欢  AI
训练标签：我   喜欢  AI    EOS
```

位置 0 的隐藏状态只能读取 `BOS`，却要预测“我”；位置 2 读取
`BOS 我 喜欢`，预测 `AI`。如果输入和标签相同，网络可能只学习复述当前位置。

## 因果注意力怎样保证未来不可见

第 $t$ 个 Query 和第 $j$ 个 Key 的分数为：

$$
s_{t,j}=\frac{q_tk_j^{\mathsf T}}{\sqrt{d_k}}+M_{t,j}
$$

因果 Mask 定义为：

$$
M_{t,j}=\begin{cases}
0,&j\le t\\
-\infty,&j>t
\end{cases}
$$

Softmax 后，$e^{-\infty}=0$，所以 $j>t$ 的注意力权重严格为零。第 $t$ 层只依赖不晚于 $t$ 的上一层位置；逐层应用这一约束，可归纳得到最终位置 $t$ 也不依赖未来输入。

这必须用行为断言验证：修改未来 Token，不应改变过去位置的输出。只查看三角矩阵不够，因为 API 的布尔 Mask 含义可能相反。

## 最小手算

位置 0 对三个 Key 的未屏蔽分数为 `[2,1,3]`。因果 Mask 后变成
`[2,-∞,-∞]`，Softmax 权重必为 `[1,0,0]`。

位置 1 的分数若为 `[1,2,4]`，Mask 后是 `[1,2,-∞]`。减最大值后指数为
`[e^-1,1,0]`，权重约 `[0.269,0.731,0]`。即使未来位置分数最高，也不能被读取。

若这一位置的四类 Logits 为 `[2,1,0,-1]`，真实类别是 0，则正确概率为
$e^2/(e^2+e^1+1+e^{-1})\approx0.644$，损失约 $0.440$。

## 可执行因果实验

```python
import numpy as np

rng = np.random.default_rng(42)
B, T, D = 1, 4, 4
x = rng.normal(size=(B, T, D))
wq = rng.normal(size=(D, D))
wk = rng.normal(size=(D, D))
wv = rng.normal(size=(D, D))

def causal_attention(hidden):
    q, k, v = hidden @ wq, hidden @ wk, hidden @ wv
    scores = q @ k.transpose(0, 2, 1) / np.sqrt(D)
    blocked = np.triu(np.ones((T, T), dtype=bool), k=1)
    scores = np.where(blocked[None], -np.inf, scores)
    scores -= scores.max(axis=-1, keepdims=True)
    weights = np.exp(scores)
    weights /= weights.sum(axis=-1, keepdims=True)
    return weights @ v, weights

original, weights = causal_attention(x)
changed = x.copy()
changed[:, 3] += 100.0  # 只改变最后一个未来位置
changed_output, _ = causal_attention(changed)

assert original.shape == (B, T, D)
assert weights.shape == (B, T, T)
assert np.all(weights[0][np.triu(np.ones((T, T), dtype=bool), 1)] == 0)
assert np.allclose(original[:, :3], changed_output[:, :3], atol=1e-10)
assert not np.allclose(original[:, 3], changed_output[:, 3])
print("future blocked:", np.allclose(original[:, :3], changed_output[:, :3]))
```

## 实验结果解释

最后位置被大幅修改后，前三个位置输出完全不变，说明当前实现满足因果不可见性。它只验证一个注意力层的前向约束，不证明训练数据没有未来字段，也不证明模型生成质量良好。外部特征泄漏和标签错位仍需单独审计。

## 训练与生成为什么不同

训练时已知整段真实文本，可以把所有位置放进同一个 `[B,T,D]` 张量并行计算；因果 Mask 阻止信息越界。生成时下一个 Token 尚不存在，必须先得到一步结果、选择 Token、追加后才能继续。

这形成两阶段推理：

- **Prefill：** 并行处理完整提示，建立每层上下文状态；
- **Decode：** 每次生成一个 Token，通常复用[大模型 KV Cache](<14-大模型 KV Cache.md>)。

训练中常有 Dropout 并保存反向图；推理使用评估模式和关闭梯度。生成是否随机则由[大模型生成采样](13-大模型生成采样.md)决定，不由 `eval()` 决定。

## 质量延迟与成本影响

- 标准自注意力保存 `[T,T]` 分数，长上下文的 Prefill 计算和显存增长很快。
- 输出投影需为每个位置计算 $V$ 个 Logit，大词表增加算力和参数。
- 首 Token 延迟主要包含 Tokenization、排队和 Prefill；逐 Token 延迟主要来自 Decode。
- 更长提示不保证更好，相关信息可能被噪声淹没，还会直接增加费用和缓存。
- 只比较每秒 Token 不足以代表体验，还要区分首 Token 延迟和完成延迟。

## 数据评测与安全风险

- 因果 Mask 不能修复提示中已经泄漏的答案或未来业务字段。
- 训练语料重复、基准污染会让损失与能力评测虚高。
- 下一 Token 似然不保证事实性、授权边界和无害性。
- 上线前需测试提示注入、敏感信息复述、越权请求和拒答。
- 生成事实应由来源、检索或工具结果约束，不能把模型概率当事实置信度。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 训练损失低得异常 | 标签未右移或 Mask 方向错误 | 打印输入标签对，运行未来修改断言 |
| 训练正常但生成重复输入 | 目标对齐偏移错误 | BOS、输入切片和标签切片 |
| 输出出现未来内容 | 因果 Mask 未应用到所有层 | 每层执行因果不可见性测试 |
| 首 Token 很慢 | 提示过长或 Prefill 低效 | 输入 Token、排队和 Prefill 分段耗时 |
| 每步生成越来越慢 | 未使用缓存或缓存复制 | Decode 跟踪、缓存长度和内存分配 |
| 回答流畅但事实错误 | 目标只优化文本概率 | 来源验证、工具调用和事实评测 |

## 适用与不适用场景

自回归 Transformer 适合开放式文本、代码和其他序列生成，也可通过读取特定位置完成分类。固定规则、严格精确计算和高风险状态变更不应仅靠自由生成；应使用确定性程序、结构化输出或受控工具。超长输入也不应默认全部塞入上下文，应先做选择、压缩或检索。

## 学习收益

你应能追踪 `[B,T] → [B,T,D] → [B,T,V]`，从链式法则推导自回归目标，手工对齐输入与标签，用行为测试证明未来不可见，并区分训练并行、Prefill 和 Decode。

## 给别人讲清楚

### 复述检查

请尝试不用公式说明：“训练时模型虽然一次看到整段张量，但每个位置被三角形门挡住，只能读取左侧；生成时右侧内容尚不存在，所以必须一步一步把新 Token 接回输入。”如果能继续说明标签为什么右移，就掌握了主线。

## 自检问题

1. 位置 $t$ 的 Logits 应与哪个 Token 计算损失？
2. 为什么训练可以并行，生成却存在顺序依赖？
3. `eval()` 为什么不能代替因果 Mask？
4. 怎样通过修改输入验证未来不可见性？
5. 较低的下一 Token 损失为什么不等于事实可靠？

## 相关主题

- [大模型预训练目标](03-大模型预训练目标.md)
- [大模型生成采样](13-大模型生成采样.md)
- [大模型 KV Cache](<14-大模型 KV Cache.md>)
- [Transformer](../I-深度学习/09-Transformer.md)

## 资料来源

- Ashish Vaswani 等, [Attention Is All You Need](https://arxiv.org/abs/1706.03762), 2017，访问日期：2026-09-10。
- Alec Radford 等, [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf), 2019，访问日期：2026-09-10。
- Hugging Face, [Causal language modeling](https://huggingface.co/docs/transformers/tasks/language_modeling)，访问日期：2026-09-10。
- PyTorch, [Scaled Dot Product Attention](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)，访问日期：2026-09-10。
