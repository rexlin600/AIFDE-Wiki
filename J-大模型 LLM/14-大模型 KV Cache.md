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
  - Key Value Cache
  - 推理缓存
tags:
  - inference
  - kv-cache
  - latency
---

# 大模型 KV Cache

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

自回归生成每次只新增一个 Token，过去 Token 的 Key 和 Value 在同一层不会改变。KV Cache 保存这些结果，使下一步只计算新 Token 的 Q、K、V，再让新 Query 关注已有缓存。它减少重复计算，是 LLM 逐 Token 推理的核心优化。

KV Cache 不减少模型权重，也不让注意力摆脱对全部历史位置的读取。它用更多显存换更低的 Decode 计算和延迟。

## 不理解会造成什么错误

- 每步把完整前缀重新送入模型，生成越长越慢。
- 只按模型权重估显存，忽略缓存随批量和上下文线性增长。
- 缓存位置、层或请求错位，输出能生成但与无缓存结果不一致。
- 多个请求复用缓存却不隔离，造成数据串线和隐私事故。
- 把 Prefix Cache 命中当成 KV Cache 必然命中，忽略 Token 与模型版本必须完全一致。

## 它在 LLM 链路中的位置

```text
提示 Token → Prefill → 每层生成提示 K V → KV Cache
                                            ↓
新 Token → Decode → 新 Q K V → 追加 K V → 下一个 Token
                         ↑                  │
                         └──── 读取历史 ────┘
```

采样只选择下一个 Token，见[大模型生成采样](13-大模型生成采样.md)；KV Cache 优化的是选择前的模型计算，不改变采样分布。

## 从长对话助手开始

对话已有 2,000 个 Token，用户希望模型再生成 200 个 Token。没有缓存时，每一步都重新计算整个历史的各层 K 和 V。使用缓存后，历史只在 Prefill 处理一次，Decode 每步追加一个位置。

需要同时关注：

- 首 Token 延迟：主要受排队与 Prefill 影响；
- 逐 Token 延迟：主要受 Decode、缓存读取和调度影响；
- 缓存显存：限制并发数和可用上下文；
- 隔离：每个请求的缓存、位置和生命周期必须明确。

## 先建立简单基线

无缓存完整解码是最可信的正确性基线：每步用完整前缀重新前向。先让缓存实现与它在同一 Token 序列上逐位置数值一致，再测加速。短输出或极小模型中，缓存管理开销可能抵消收益，不应只凭原理宣布更快。

## Key 和 Value 为什么可以复用

单层自注意力投影为：

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
$$

在因果模型中，加入新 Token $x_t$ 不会改变过去隐藏状态 $x_{<t}$。模型权重也固定，因此过去的 $K_{<t}$ 和 $V_{<t}$ 保持不变。新一步只需计算：

$$
q_t=x_tW_Q,\quad k_t=x_tW_K,\quad v_t=x_tW_V
$$

并追加缓存：

$$
K_{\le t}=[K_{<t};k_t],\qquad
V_{\le t}=[V_{<t};v_t]
$$

新位置输出为：

$$
o_t=\operatorname{softmax}\left(
\frac{q_tK_{\le t}^{\mathsf T}}{\sqrt{d_k}}
\right)V_{\le t}
$$

因为缓存里恰好是完整前缀本应重新计算出的 K/V，所以在相同数值精度和位置处理下，缓存与无缓存输出应等价。

## 缓存张量形状

第 $l$ 层的标准多头缓存通常分别为：

```text
K_l [B,H_kv,T,d_k]
V_l [B,H_kv,T,d_v]
```

$H_{kv}$ 是 Key/Value 头数。标准多头注意力中 $H_{kv}=H$；Multi-Query Attention 可令 $H_{kv}=1$；Grouped-Query Attention 介于两者之间。Query 头共享较少的 K/V 头，能降低缓存与内存带宽，但必须由模型训练结构支持，不能在部署时随意修改。

整个模型的概念布局可写成 `[L,2,B,H_kv,T,d_k]`，`2` 表示 K 和 V，实际框架可能按层保存元组或采用不同维度顺序。

## 显存字节数怎样推导

若 K/V 维度相同，每个元素占 $s$ 字节，缓存总量近似：

$$
M_{KV}=2LBH_{kv}Td_ks
$$

标准多头注意力中 $H_{kv}d_k=D$，所以：

$$
M_{KV}=2LBTDs
$$

它与层数、批量、缓存长度和隐藏维度线性增长。这里未计分配器碎片、对齐、元数据、临时注意力张量与模型权重，因此是下界式估算。

## 最小手算

设 $L=32$、$B=1$、$T=2048$、$D=4096$，缓存为 FP16，即 $s=2$ 字节：

$$
M_{KV}=2\times32\times1\times2048\times4096\times2
=1{,}073{,}741{,}824\ \text{bytes}
$$

即约 `1 GiB`。批量增加到 8 时约为 `8 GiB`。这还没有计算权重和运行时工作区，所以“权重刚好装下”远不等于服务能承载目标并发。

## Prefill 与 Decode 的计算差别

- **Prefill：** 一次处理长度 $P$ 的提示，可并行产生所有位置的 K/V；标准注意力分数规模约 $P^2$。
- **Decode：** 每步只有一个新 Query，读取长度为 $t$ 的缓存，注意力规模约 $t$；但矩阵更小、并行度较低，常受内存带宽影响。

生成 $N$ 个 Token 时，缓存后的 Decode 注意力工作量随
$P+(P+1)+\cdots+(P+N-1)$ 增长；没有缓存则每步还会重算完整前缀各位置的投影和注意力。缓存消除的是过去计算重复，不是历史长度本身。

## 可执行缓存等价实验

```python
import numpy as np

rng = np.random.default_rng(42)
B, T, D = 1, 6, 4
x = rng.normal(size=(B, T, D))
wq = rng.normal(size=(D, D))
wk = rng.normal(size=(D, D))
wv = rng.normal(size=(D, D))

def softmax(scores):
    shifted = scores - scores.max(axis=-1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=-1, keepdims=True)

def full_causal(hidden):
    q, k, v = hidden @ wq, hidden @ wk, hidden @ wv
    scores = q @ k.transpose(0, 2, 1) / np.sqrt(D)
    blocked = np.triu(np.ones((T, T), dtype=bool), k=1)
    weights = softmax(np.where(blocked[None], -np.inf, scores))
    return weights @ v

full = full_causal(x)
cached_outputs = []
k_cache = np.empty((B, 0, D))
v_cache = np.empty((B, 0, D))
for position in range(T):
    token = x[:, position:position + 1]
    q_new = token @ wq
    k_cache = np.concatenate([k_cache, token @ wk], axis=1)
    v_cache = np.concatenate([v_cache, token @ wv], axis=1)
    weights = softmax(q_new @ k_cache.transpose(0, 2, 1) / np.sqrt(D))
    cached_outputs.append(weights @ v_cache)
cached = np.concatenate(cached_outputs, axis=1)

assert full.shape == cached.shape == (B, T, D)
assert np.allclose(full, cached, atol=1e-10)
assert k_cache.shape == v_cache.shape == (B, T, D)

layers, batch, length, hidden, bytes_per = 32, 1, 2048, 4096, 2
cache_bytes = 2 * layers * batch * length * hidden * bytes_per
assert cache_bytes == 1024 ** 3
print("max difference", np.max(np.abs(full - cached)),
      "cache GiB", cache_bytes / 1024**3)
```

## 实验结果解释

逐 Token 缓存输出与完整因果计算在浮点容差内一致，证明本例没有改变注意力语义。实际框架可能因低精度、融合内核或运算顺序出现微小差异，应设合理容差并比较最终 Token，而不是要求每一位比特相同。

这个实验没有测真实 GPU 加速，也没有模拟多层缓存调度。性能结论必须在目标模型、硬件、并发和长度分布上实测。

## 缓存生命周期与位置

每个缓存至少隐含以下状态：模型与适配器版本、批次槽位、已缓存 Token、位置编号、有效长度、数据类型和设备。新增 Token 的位置编码必须从缓存长度继续，不能每步从 0 开始。

请求结束、取消或超时后应释放缓存。连续批处理会动态加入和移除请求，因此逻辑批次槽位与物理缓存页要有明确映射。Prefix Cache 可让多个请求复用完全相同的前缀，但前缀 Token、模型、位置与相关配置必须兼容，并设置租户与隐私隔离。

## 质量延迟与成本影响

- 缓存通常降低逐 Token 计算，却增加显存占用和内存读带宽。
- 更长上下文使每一步读取更多 K/V，Decode 延迟仍可能随长度上升。
- 缓存占满会降低并发、触发排队、驱逐或请求拒绝。
- GQA/MQA、低精度缓存和分页管理能降低压力，但都需验证质量或复杂度代价。
- Prefix Cache 只改善重复前缀的 Prefill；普通请求内 KV Cache 改善同一生成过程的 Decode，二者不要混称。

容量规划应基于输入与输出长度分布、并发、层数、KV 头数、精度和碎片安全余量，而不是只看平均请求。

## 数据评测与安全风险

- 不同用户和租户的缓存必须隔离，释放后应避免残留数据被错误复用。
- 提示包含个人信息时，Prefix Cache 的键、共享范围和保留时间需要审计。
- 缓存命中与未命中路径都应通过相同内容安全策略。
- 截断或驱逐历史会改变模型可见上下文，必须在响应元数据中可诊断。
- 等价性测试应覆盖不同长度、Padding、批次重排和停止时间。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 有缓存和无缓存文本不同 | 位置、追加轴或层映射错误 | 逐层逐位置比较 K V 和 Logits |
| 每步仍越来越慢得异常 | 完整前缀被重复前向 | Trace 每步输入长度和 Prefill 次数 |
| 并发一高就 OOM | 未计 KV Cache 或碎片 | 按 P95 长度估算缓存与安全余量 |
| 不同请求内容串线 | 批次槽复用或释放错误 | 请求 ID、页表、生命周期隔离测试 |
| Prefix Cache 命中率低 | Token 或模板不完全一致 | Token ID、模型版本、前缀哈希 |
| 长上下文质量下降 | 截断、位置外推或注意力退化 | 实际可见 Token、长度切片评测 |

## 适用与不适用场景

KV Cache 适合自回归逐 Token 生成，尤其是长提示或长输出。一次性分类、Embedding 编码和训练全序列不靠它获得同样收益。极短输出、显存极紧或高并发场景需要测量缓存收益与容量代价，有时应限制上下文、量化缓存或选择更小模型。

## 学习收益

你应能证明过去 K/V 可复用，追踪 `[B,H_kv,T,d_k]`，手算缓存字节数，区分 Prefill、Decode 与 Prefix Cache，并设计有缓存和无缓存的逐位置等价测试。

## 给别人讲清楚

### 复述检查

请尝试说明：“模型写下一个字时，过去每个字的 Key 和 Value 已经算过且不会改变。缓存把它们留下，只为新字计算一份，再读取全部历史。这样少算很多，但历史越长，要保存和读取的数据仍越多。”

## 自检问题

1. 为什么缓存 Key 和 Value，却通常不缓存供未来使用的 Query？
2. KV Cache 为什么降低计算却增加显存？
3. 标准多头注意力下缓存字节数怎样从层数、批量、长度和隐藏维度得到？
4. Prefix Cache 与请求内 KV Cache 分别优化哪个阶段？
5. 怎样检测两个请求的缓存发生串线？

## 相关主题

- [大模型自回归 Transformer](<04-大模型自回归 Transformer.md>)
- [大模型生成采样](13-大模型生成采样.md)
- [大模型量化](15-大模型量化.md)
- [大模型服务](16-大模型服务.md)

## 资料来源

- Ashish Vaswani 等, [Attention Is All You Need](https://arxiv.org/abs/1706.03762), 2017，访问日期：2026-09-10。
- Noam Shazeer, [Fast Transformer Decoding](https://arxiv.org/abs/1911.02150), 2019，访问日期：2026-09-10。
- Joshua Ainslie 等, [GQA Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints](https://arxiv.org/abs/2305.13245), 2023，访问日期：2026-09-10。
- Hugging Face, [Cache strategies](https://huggingface.co/docs/transformers/kv_cache)，访问日期：2026-09-10。
