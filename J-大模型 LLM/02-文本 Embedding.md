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
  - 文本向量
tags:
  - embedding
  - representation
---

# 文本 Embedding

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

Embedding 把离散 Token 或整段文本映射到连续向量，使模型能学习相似性和可组合表示。Token Embedding 是生成模型内部输入；句向量常用于检索、聚类和相似度，两者用途不能混用。

## 不理解会造成什么错误

- 把 Token ID 当成有大小和距离意义的数值。
- 对 Token 向量盲目平均，忽略 Padding 和任务训练方式。
- 用生成模型的某个隐藏层直接做检索，却没有验证相似度质量。
- 混用不同模型或版本的向量，导致索引与查询不在同一空间。

## 它在 LLM 链路中的位置

Tokenizer 产生 `input_ids [B,T]`，查表后得到 `[B,T,D]`，再加入位置信息进入 Transformer。句向量模型则把整段 `[T,D]` 聚合为 `[D]`，供相似度和下游任务使用。

## 从语义检索开始

用户查询“怎样重置密码”，知识条目写着“忘记登录凭证的恢复步骤”。关键词不完全相同，句向量可以作为语义召回信号。简单基线仍是关键词或 BM25；Embedding 只有在固定查询集的 Recall@K 上更好才有价值。

## 查表不是把 ID 当数值

设词表大小 $V$、维度 $D$，Embedding 矩阵 $E\in\mathbb R^{V\times D}$。Token ID $i$ 的向量是第 $i$ 行：

$$
e_i=E[i]
$$

等价地，把 ID 写成 one-hot 向量 $o_i\in\mathbb R^V$：

$$
e_i=o_i^TE
$$

因此 ID 7 与 ID 8 并不天然比 ID 100 更相似；相似性由训练后的矩阵行决定。

## 从 Token 向量到句向量

最简单的 Masked Mean 为：

$$
s=\frac{\sum_{t=1}^{T}m_th_t}{\sum_{t=1}^{T}m_t}
$$

$m_t=1$ 表示有效 Token。它避免 Padding 稀释短文本，但没有自动保证 $s$ 适合语义检索。句向量模型通常使用专门对比目标训练。

余弦相似度只看方向：

$$
\cos(a,b)=\frac{a^Tb}{\lVert a\rVert_2\lVert b\rVert_2}
$$

## 最小手算

词表三行向量为 `[[1,0],[0,1],[1,1]]`。ID 序列 `[0,2]` 查表得到 `[1,0]` 和 `[1,1]`，均值为 `[1,0.5]`。它与查询 `[1,0]` 的余弦为 $1/\sqrt{1.25}\approx0.894$。

## 可执行实验

```python
import numpy as np

embedding = np.array([[1., 0.], [0., 1.], [1., 1.], [-1., 0.]])
ids = np.array([[0, 2, 1], [0, 1, 3]])
valid = np.array([[1, 1, 1], [1, 1, 0]], dtype=float)
tokens = embedding[ids]
sentences = (tokens * valid[..., None]).sum(1) / valid.sum(1, keepdims=True)
normalized = sentences / np.linalg.norm(sentences, axis=1, keepdims=True)
similarity = normalized @ normalized.T
unmasked_second = tokens[1].mean(0)
print("token shape", tokens.shape)
print("sentence vectors", sentences)
print("cosine matrix\n", np.round(similarity, 3))
assert tokens.shape == (2, 3, 2)
assert np.isfinite(similarity).all()
assert np.isclose(similarity[0, 1], 1.0)
assert not np.allclose(sentences[1], unmasked_second)
```

第二条序列屏蔽最后一个 Token 后得到 `[0.5,0.5]`；若错误地把 Padding 一起平均，则得到 `[0,1/3]`。断言验证两者不同，说明 Mask 是表示协议的一部分。余弦计算还必须处理零向量；真实系统可拒绝空输入或显式约定其相似度，不能让除零悄悄产生 NaN。

## 实验结果解释

余弦高只说明当前空间中方向接近，不证明事实等价、可替换或因果相关。检索需要在真实查询与相关文档标签上评价 Recall@K、排序和困难负例。

## 质量延迟与成本影响

向量维度越大，索引存储、网络传输和相似度计算越贵。批量编码可提高吞吐；查询向量和文档向量必须使用兼容模型、相同规范化与指令前缀。降维或量化要重新评测召回。

## 数据评测与安全风险

Embedding 可能编码敏感属性，向量也不是天然匿名。模型升级后应建立新索引或证明跨版本兼容。检索评测需按查询意图和语言切片，并防止同一文档近重复版本跨训练与测试。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 语义相近却召回不到 | 模型不适合领域或截断 | 查询文档长度、困难样例、Recall@K |
| 所有相似度都很高 | 向量各向异性或未归一化 | 范数分布、随机负例、中心化 |
| 升级后检索崩溃 | 新旧向量空间混用 | 模型版本、索引重建、维度 |
| 短文本结果异常 | Padding 进入池化 | Mask、分母、特殊 Token |
| 成本过高 | 维度或重复编码过大 | 批量、缓存、维度、文档去重 |

## 适用与不适用场景

Embedding 适合语义召回、聚类和相似度特征。精确编号、错误码和专有名词常需要稀疏检索配合。生成 Token 使用模型内部 Token Embedding，不应拿句向量直接替代。

## 学习收益

你应能解释查表等价式，追踪 `[B,T] → [B,T,D] → [B,D]`，手算余弦，并设计向量版本与检索评测。

## 给别人讲清楚

“ID 只是字典页码，Embedding 才是模型学到的坐标。句向量又是把一串坐标压成一个用于比较的地址，它是否好用必须由检索任务验证。”

## 自检问题

1. 为什么相邻 Token ID 不表示相似？
2. Padding 为零时为什么仍要 Masked Mean？
3. 为什么模型升级通常需要重建向量索引？

## 相关主题

- [词元化 Tokenization](<01-词元化 Tokenization.md>)
- [大模型预训练目标](03-大模型预训练目标.md)
- [RAG](../K-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG/00-%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90%20RAG-MOC.md)

## 资料来源

- Tomas Mikolov 等, [Efficient Estimation of Word Representations](https://arxiv.org/abs/1301.3781), 2013，访问日期：2026-09-10。
- Nils Reimers, Iryna Gurevych, [Sentence-BERT](https://aclanthology.org/D19-1410/), 2019，访问日期：2026-09-10。
- PyTorch, [Embedding](https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html)，访问日期：2026-09-10。
