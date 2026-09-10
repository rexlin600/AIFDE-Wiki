---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Dense Retrieval]
tags: [dense-retrieval, embedding]
---

# Dense 向量检索

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

Dense 检索把查询和文档编码到同一连续向量空间，用相似度召回没有共享关键词但语义接近的内容。它解决“重置登录凭证”与“忘记密码恢复”这类表达差异，不保证理解精确数字、否定或最新事实。

## 不理解会造成什么错误

- 查询与文档使用不同模型或不同指令前缀，向量空间不兼容。
- 未归一化却把点积称为余弦，向量范数主导结果。
- 训练只见容易负例，真实相似但不相关的文档排得过高。
- 把向量相近解释为事实等价或证据充分。

## 它在 RAG 链路中的位置

`查询文本 → 查询编码器 → q∈R^D`；离线侧为 `Chunk → 文档编码器 → d_i∈R^D → 向量索引`。在线检索必须把可信身份对应的权限过滤下推到索引查询，或在可信索引内部搜索时同步过滤，再返回 Dense Top-N 做融合或重排序。未授权候选不能进入重排、模型上下文或正文日志。

## 从同义问法开始

知识库写“忘记密码恢复流程”，用户问“登录凭证丢了怎么办”。关键词计数是简单基线，可能零匹配。经过相关性数据训练的双编码器可让两者向量接近，但效果必须用真实查询验证。

## 相似度逐步推导

点积为 $q^Td$。余弦相似度消除长度影响：

$$
s(q,d)=\frac{q^Td}{\lVert q\rVert_2\lVert d\rVert_2}
$$

若先做 L2 归一化，$\hat q=q/\lVert q\rVert$、$\hat d=d/\lVert d\rVert$，则余弦就是 $\hat q^T\hat d$。零向量没有余弦，应拒绝或显式降级。

双编码器常用批内对比损失。一个正文档 $d^+$ 和候选集合 $D$ 的单样本损失为：

$$
L=-\log\frac{e^{s(q,d^+)/\tau}}{\sum_{d\in D}e^{s(q,d)/\tau}}
$$

$\tau>0$ 是温度。相似但错误的困难负例若得分很高，会显著增大分母和损失，迫使模型学习细粒度区别。

## 最小手算

$q=[1,0]$，正例 $d^+=[0.8,0.6]$，负例 $d^-=[0,1]$，三者范数均为 1。余弦分别为 0.8 和 0。取 $\tau=1$：

$$
L=-\log\frac{e^{0.8}}{e^{0.8}+e^0}\approx0.371
$$

若困难负例得分 0.7，损失约 0.644，训练信号更强。

## 可执行实验

```python
import numpy as np

def normalize(x):
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    if np.any(norm == 0):
        raise ValueError("cosine is undefined for zero vector")
    return x / norm

q = normalize(np.array([[1.0, 0.0]]))[0]
docs = normalize(np.array([[0.8, 0.6], [0.0, 1.0], [0.7, 0.714]]))
scores = docs @ q
print(np.round(scores, 3))
assert int(np.argmax(scores)) == 0

def contrastive_loss(positive, negative, temperature=1.0):
    logits = np.array([positive, negative]) / temperature
    shifted = logits - logits.max()
    probability = np.exp(shifted)[0] / np.exp(shifted).sum()
    return -np.log(probability)

easy = contrastive_loss(0.8, 0.0)
hard = contrastive_loss(0.8, 0.7)
assert hard > easy
try:
    normalize(np.array([[0.0, 0.0]]))
    raise AssertionError("zero vector was accepted")
except ValueError:
    pass
```

## 实验结果边界

实验验证归一化余弦和困难负例提高当前损失，不证明任意困难负例都改善泛化。错误标注或假负例会伤害训练；二维手工向量也不是实际模型效果。

## 质量延迟与成本影响

文档编码可离线批量完成，查询编码增加在线模型延迟。维度越高，存储、传输和距离计算通常越贵。模型、Pooling、归一化、精度和指令前缀必须随索引版本绑定；升级模型通常需重建索引。

## 数据评测与安全风险

训练负例可能包含实际相关文档，需抽样复核。Embedding 不是匿名化，仍可能泄露敏感属性。权限过滤必须由索引或可信边界执行，不能依赖向量。按领域、语言、实体、否定和时间查询切片评测。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 相似问法召回差 | 模型未适配领域 | 查询切片、困难样例、Recall@k |
| 分数都很高 | 未归一化或向量各向异性 | 范数、随机负例、Pooling |
| 升级后接近随机 | 新旧向量空间混用 | 模型、前缀、维度、索引版本 |
| 精确编号丢失 | Dense 弱化罕见词 | BM25 消融、Hybrid、Tokenizer |
| 空文本出现 NaN | 产生零向量 | 输入校验、范数、降级路径 |

## 适用与不适用场景

适合语义改写、跨措辞和自然语言描述。精确 ID、数字、强否定或必须可解释的词匹配应保留 BM25。没有领域评测或无法维护向量版本时，不应只因“语义更智能”就替换基线。

## 学习收益

你应能追踪文本到向量的数据流，手算余弦和对比损失，并解释困难负例、模型版本和安全过滤的作用。

## 给别人讲清楚

“Dense 检索把不同说法放到同一张语义地图上，靠方向接近找文档。地图由训练数据决定，相近不等于事实相同，权限也不由地图决定。”

## 自检问题

1. 归一化后点积为什么等于余弦？
2. 困难负例为什么比无关负例提供更强训练信号？
3. 为什么升级文档编码模型通常需要重建索引？

## 相关主题

- [文本 Embedding](../J-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM/02-%E6%96%87%E6%9C%AC%20Embedding.md)
- [RAG 向量索引](10-RAG%20向量索引.md)
- [混合检索 Hybrid Search](02-混合检索%20Hybrid%20Search.md)

## 资料来源

- Karpukhin 等, [Dense Passage Retrieval](https://aclanthology.org/2020.emnlp-main.550/), 2020，访问日期：2026-09-10。
- Reimers 与 Gurevych, [Sentence-BERT](https://aclanthology.org/D19-1410/), 2019，访问日期：2026-09-10。
- PyTorch, [CosineSimilarity](https://docs.pytorch.org/docs/stable/generated/torch.nn.CosineSimilarity.html)，访问日期：2026-09-10。
