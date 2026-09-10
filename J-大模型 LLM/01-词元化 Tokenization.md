---
type: concept
domain:
  - LLM
depth: L3
importance: core
maturity: draft
created: 2026-09-09
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Tokenizer
tags:
  - tokenization
  - llm-input
---

# 词元化 Tokenization

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

模型不能直接读取文字。Tokenizer 把文本变成有限词表中的 Token ID，也把输出 ID 还原成文本。它同时决定输入长度、上下文占用、计算量、计费和特殊消息协议。

## 不理解会造成什么错误

- 用字符数估算窗口，中文、代码或 JSON 被意外截断。
- 模型权重与 Tokenizer 不匹配，程序能跑但语义完全错误。
- 把用户文本当特殊 Token 解析，破坏角色或停止边界。
- 认为 Token 越少质量必然越高，忽略词表参数和低频学习。

## 它在 LLM 链路中的位置

```text
原始文本 → 规范化 → 切分 → Token ID [B,T]
→ Embedding [B,T,D] → Transformer → 输出 ID → 解码文本
```

Tokenizer 是模型契约的一部分。它的词表、合并规则、规范化、特殊 Token 和对话模板都必须与权重版本一起保存。

## 从中英文客服输入开始

用户输入可能同时包含中文、英文产品名、订单号和 JSON。预测对象是下一 Token，输入成本按完整系统消息、工具 Schema、历史和用户文本的 Token 总数计算。基线是直接使用目标模型自带 Tokenizer，不自行更换词表。

## 三种粒度

- 字符级词表小、几乎无未知项，但序列长。
- 词级直观，但新词、词形和拼写会快速扩大词表。
- 子词在二者间折中，常见片段保持整体，罕见内容继续拆分；字节回退还可覆盖任意文本。

## BPE 合并怎样产生词表

从字符或字节符号开始，统计所有相邻对的频次，每轮合并最常见的一对。设语料切分为若干序列，第 $k$ 轮选择：

$$
(a_k,b_k)=\arg\max_{(a,b)}\operatorname{count}_k(a,b)
$$

然后把每个相邻的 $a_k,b_k$ 替换为新符号 $a_kb_k$。训练得到的是有顺序的合并规则；编码新文本时必须按规则应用，而不是重新统计新文本。

Unigram 则从较大候选词表出发，用概率模型评价切分并逐步删除贡献较小的子词。两者都能产生子词词表，但目标与编码算法不同。

## 最小手算

语料只有 `low low lower`，初始写为字符加词尾。第一轮相邻对 `l-o` 出现 3 次，若合并成 `lo`，序列变短。随后 `lo-w` 仍出现 3 次，可合并成 `low`。常见词逐渐成为单 Token，`lower` 仍可表示为 `low e r`。

## 可执行实验

```python
from collections import Counter

corpus = [tuple(word) + ("</w>",) for word in "low low lower".split()]

def pairs(words):
    return Counter(pair for word in words for pair in zip(word, word[1:]))

def merge(words, target):
    output = []
    for word in words:
        merged = []
        index = 0
        while index < len(word):
            if index + 1 < len(word) and word[index:index + 2] == target:
                merged.append("".join(target))
                index += 2
            else:
                merged.append(word[index])
                index += 1
        output.append(tuple(merged))
    return output

for _ in range(2):
    best = pairs(corpus).most_common(1)[0]
    print("merge", best)
    corpus = merge(corpus, best[0])
print(corpus)
```

输出应先合并 `l+o`，再合并 `lo+w`。真实 BPE 还要处理词边界、并列频次、字节和特殊 Token。

## 实验结果解释

这个实验说明高频片段如何变成词表项，不代表任一真实模型会得到相同 ID。比较 Tokenizer 时，应在目标语料上报告 Token 数分布、截断率、字节回退、往返一致性和特殊 Token 行为。

## 质量延迟与成本影响

Attention 计算随序列长度增长，KV Cache 也随 Token 数增加。更大的词表可能缩短序列，却扩大输入 Embedding 和输出投影。中英文、代码、表格和 JSON 应分别测量，不能用统一“字符除以四”估算。

## 数据评测与安全风险

训练自有 Tokenizer 时，规范化可能抹掉大小写、空白或医学符号。把未转义的用户输入拼进特殊 Token 协议会形成提示边界问题。评测集必须使用实际部署的模板和 Tokenizer 版本。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 中文成本异常高 | 目标语料在词表中覆盖差 | 分语言 Token 分布、字节回退 |
| 输出乱码 | ID 解码或字节边界错误 | 同一 Tokenizer 往返、特殊 Token |
| 提前停止 | 普通文本被解析成终止符 | 特殊 Token 注入、解码参数 |
| 模型质量突然崩溃 | Tokenizer 与权重错配 | 词表哈希、大小、模板版本 |
| 窗口偶尔超限 | 只计算用户正文 | 系统消息、Schema、历史、输出预留 |

## 适用与不适用场景

所有 LLM 请求都需要准确 Token 计数。已有模型应使用配套 Tokenizer；只有从头预训练或有完整迁移方案时才考虑改变词表。Token 更短只是效率证据，不是质量证据。

## 学习收益

你应能解释文本怎样变成 ID，手算 BPE 合并，审计特殊 Token 与版本匹配，并在真实语料上估算窗口和成本。

## 给别人讲清楚

“Tokenizer 是模型的字典和切字规则。模型看到的不是字，而是字典编号；换错字典，就像拿着另一版密码本读同一串数字。”

## 自检问题

1. 为什么同一段中文在不同模型中 Token 数不同？
2. 更大词表有哪些成本？
3. 为什么 Tokenizer 必须与模型权重一起版本化？

## 相关主题

- [文本 Embedding](<02-文本 Embedding.md>)
- [大模型上下文工程](06-大模型上下文工程.md)
- [大模型从头预训练](19-大模型从头预训练.md)

## 资料来源

- Rico Sennrich 等, [Neural Machine Translation of Rare Words with Subword Units](https://aclanthology.org/P16-1162/), 2016，访问日期：2026-09-10。
- Taku Kudo, John Richardson, [SentencePiece](https://aclanthology.org/D18-2012/), 2018，访问日期：2026-09-10。
- Hugging Face, [Tokenizer](https://huggingface.co/docs/transformers/main_classes/tokenizer)，访问日期：2026-09-10。
