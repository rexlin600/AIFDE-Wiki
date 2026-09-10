---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Chunking]
tags: [chunking, retrieval]
---

# RAG 文档切分

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

切分把长文档变成可索引 Chunk。Chunk 太大，会混入无关内容并浪费上下文；太小，会把条件与结论拆开。目标不是找到万能长度，而是在召回、证据完整性和成本之间取得可验证的平衡。

## 不理解会造成什么错误

- 按字符硬切，把“仅限正式员工”和福利结论分开。
- 重叠过大造成重复召回，同一证据占满 Top-k。
- 用字符数代替模型 Token 数，超出编码或上下文限制。
- 改切分参数却沿用旧 Chunk ID 和评测结果。

## 它在 RAG 链路中的位置

`清洗结构块 → 边界选择 → 重叠与标题继承 → Chunk + 来源映射 → Embedding 与索引`。一个 Chunk 至少包含 `chunk_id`、文本、父文档、字符或 Token 区间、标题路径、版本和权限。

## 从制度条款开始

原文“适用范围：正式员工。年假：满一年可享 5 天。”简单基线是每 12 个字符硬切，可能割裂条件。句子或标题边界切分优先保持语义单元；超长单元再按 Token 递归拆分。

## 长度重叠和数量

长度为 $L$ 的 Token 序列，窗口大小 $c$，重叠 $o$，步长 $s=c-o>0$。覆盖全文所需窗口数为：

$$
n=\max\left(1,\left\lceil\frac{L-c}{c-o}\right\rceil+1\right)
$$

重叠率为 $o/c$。它提高跨边界信息同时出现的机会，但近似让索引 Token 量从 $L$ 增至 $n\cdot c$，末窗口可能较短。

## 最小手算

$L=1000,c=300,o=50$，步长为 250：

$$
n=\lceil(1000-300)/250\rceil+1=4
$$

窗口起点为 0、250、500、750，最后窗口覆盖 750 到 1000。无重叠时只需 4 个窗口，但边界两侧不会共同出现。

## 可执行实验

```python
def windows(tokens, size, overlap):
    if not 0 <= overlap < size:
        raise ValueError("overlap must be smaller than size")
    step, output = size - overlap, []
    for start in range(0, len(tokens), step):
        piece = tokens[start:start + size]
        if piece:
            output.append((start, start + len(piece), piece))
        if start + size >= len(tokens):
            break
    return output

tokens = list(range(10))
chunks = windows(tokens, size=4, overlap=1)
print([(start, end) for start, end, _ in chunks])
assert [(a, b) for a, b, _ in chunks] == [(0, 4), (3, 7), (6, 10)]
assert set().union(*(set(piece) for _, _, piece in chunks)) == set(tokens)
assert chunks[0][2][-1] == chunks[1][2][0]
try:
    windows(tokens, 4, 4)
    raise AssertionError("invalid overlap was accepted")
except ValueError:
    pass
```

## 实验结果边界

实验验证窗口覆盖、一次重叠和非法参数分支。它没有证明固定窗口比句子切分好，也没有测语义完整性。真实选择必须在目标语料上比较 Recall@k、重复率、证据完整率和答案质量。

## 质量延迟与成本影响

小 Chunk 增加向量数量与索引开销；大 Chunk 增加编码、网络和上下文 Token。重叠提高存储及重复候选。可让小块负责检索、父块负责生成，但需维护映射并单独评测。

## 数据评测与安全风险

权限应继承自父文档且不可因合并跨越安全边界。切分器版本进入 Chunk ID 或索引清单；删除父文档时清理所有子块。评测按表格、代码、短条款、长章节和语言切片，并封存测试集。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 答案缺前置条件 | 边界割裂或 Chunk 太小 | 命中块相邻文本、标题继承、窗口 |
| Top-k 内容重复 | 重叠过大或近重复未去除 | overlap、父文档 ID、去重 |
| 召回主题混杂 | Chunk 太大 | 长度分布、段落边界、相关片段占比 |
| 编码器截断内容 | 字符数与 Token 数混淆 | Tokenizer、最大长度、截断日志 |
| 重建后引用失效 | Chunk ID 不稳定 | 切分器版本、来源区间、迁移策略 |

## 适用与不适用场景

长文本索引通常需要切分；短 FAQ 可整条索引。表格、代码和法律条款应使用结构感知策略，而非统一字符窗口。切分无法弥补错误解析或缺失原文。

## 学习收益

你应能推导窗口数量，验证覆盖与重叠，说明粒度对检索和生成的不同影响，并制定切分消融实验。

## 给别人讲清楚

“Chunk 是检索拿取证据的盒子。盒子太大装了杂物，太小又把条件和结论拆开；尺寸要由真实问题的召回与答案评测决定。”

## 自检问题

1. 为什么增大重叠既可能帮助召回又可能伤害 Top-k？
2. 字符长度为什么不能保证 Token 长度？
3. 修改切分方式后哪些产物需要重建？

## 相关主题

- [RAG 文档清洗](05-RAG%20文档清洗.md)
- [父子文档检索](12-父子文档检索.md)
- [RAG 上下文构建](35-RAG%20上下文构建.md)

## 资料来源

- Lewis 等, [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), 2020，访问日期：2026-09-10。
- Gao 等, [Retrieval-Augmented Generation for Large Language Models](https://arxiv.org/abs/2312.10997), 2023，访问日期：2026-09-10。
- Hugging Face, [Tokenizer](https://huggingface.co/docs/transformers/main_classes/tokenizer)，访问日期：2026-09-10。
