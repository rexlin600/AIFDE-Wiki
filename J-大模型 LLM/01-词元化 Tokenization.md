---
type: concept
domain:
  - LLM
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - Tokenization
  - Tokenizer
tags:
  - core
  - llm
---

# 词元化（Tokenization）

## 一句话定义

词元化（Tokenization）把原始文本按固定规则转换为模型词表中的 Token ID 序列，并在生成后把 ID 序列解码回文本。

## 为什么重要

模型并不直接读取字符或单词，而是读取 Token ID 对应的向量。分词结果同时决定序列长度、上下文窗口占用、训练与推理计算量，以及按 Token 计费的 API 成本。它还影响中文、代码、罕见词和特殊格式能否被紧凑且稳定地表示。

## 工作原理

### 粒度选择

- **字符级（Character-level）**词表小，几乎不会遇到未知词，但序列通常更长，模型需要从更细粒度学习词义。
- **词级（Word-level）**序列较短且易解释，但词形变化、拼写变化和新词会快速扩大词表，并产生词表外问题。
- **子词级（Subword-level）**在两者之间折中：常见片段保留为一个 Token，罕见词可拆成多个已知片段。现代 LLM 通常采用这一粒度或其字节级变体。

### 常见算法

- **Byte Pair Encoding（BPE）**从细粒度符号开始，反复合并训练语料中高频的相邻符号对，得到固定大小的子词词表。应用到文本时按学习到的合并规则组合符号。
- **WordPiece**也建立子词词表；常见实现编码时从当前位置选择词表中可匹配的最长片段。它与 BPE 的训练准则和边界标记并不相同，不能只凭名称互换分词器。
- **Unigram Language Model**先保留较大的候选子词集合，用概率模型评价不同切分，再逐步删减对语料似然贡献较小的候选；编码时选择高概率切分。SentencePiece 可直接从原始句子训练 BPE 或 Unigram 模型。

### 特殊 Token

分词器还定义模型协议中的特殊 Token，例如序列开始/结束、填充、未知项、消息角色或工具调用边界。它们可能不对应用户可见文本，却参与掩码、停止条件和对话模板。把普通文本与特殊 Token 混用，可能改变提示结构或提前终止生成。

### 词表大小的权衡

较大词表通常能用更少 Token 表示常见文本，但会扩大输入嵌入和输出投影，并让低频词项得到更少训练样本；较小词表减少这些参数，却可能拉长序列。不能只比较词表大小，应同时测量目标语料的 Token 数、未知/字节回退行为、模型质量、延迟和成本。

## 最小示例

假设词表含有 `play`、`ing`、`player`，而不含 `playing`：

```text
输入：playing
一种可能切分：[play] [ing]
输出：两个 Token ID
```

这只是机制示意；实际边界、空格标记、大小写处理和 ID 完全由具体分词器文件决定，不能据此推断任一真实模型的切分结果。

## 适用场景

- 估算提示与响应能否放入上下文窗口，以及预算和截断策略。
- 比较模型处理中文、英文、代码、JSON、标识符和领域术语的表示效率。
- 训练或适配模型前选择词表、规范化、字节回退和特殊 Token 协议。
- 排查输出乱码、异常重复、停止条件失效或消息模板不兼容。

## 不适用场景

- Token 数不能代替字符数、词数或用户可见内容长度；不同分词器的计数不可直接互换。
- 分词更短不自动意味着模型质量更好；训练数据、架构和任务共同决定效果。
- 不应在没有重新训练或明确迁移过程时给既有模型随意更换词表。

## 常见误区

- **“一个汉字就是一个 Token”**：中文可能按单字、多字片段或 UTF-8 字节组合切分，结果取决于词表和算法。
- **“一行代码的 Token 数与字符数成固定比例”**：缩进、空白、运算符、长标识符和少见 API 名称都会改变切分。
- **“同系列模型必然共用 Tokenizer”**：版本、词表、特殊 Token 和对话模板都可能变化，必须读取具体模型配置。
- **“Token ID 有跨模型含义”**：ID 只是某个词表中的索引；同一个整数在另一个词表里可能代表完全不同的片段。

## 工程实践

Tokenizer 必须与模型权重匹配，因为 Token ID 会索引模型已经训练好的嵌入行，输出 ID 也要由同一词表解码。错配会让输入片段映射到错误向量，或者让特殊 Token、词表大小与输出头不一致；即使程序因尺寸相同而能运行，语义仍可能完全错误。

对生产输入应使用实际模型的官方 Tokenizer 计数，并把系统消息、工具 Schema、检索上下文和预留输出一起计入窗口。对中文与代码分别建立代表性样本，记录每类输入的 Token 分布和截断位置，而不是依赖“字符数乘固定系数”的估算。

## 相关概念

- [LLM MOC](./00-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM-MOC.md)：分词是从文本到 Transformer 输入的第一步。
- Context Window：上限按 Token 而不是用户可见字符计算。
- Embedding：Tokenizer 产生的 ID 用来查找 Token Embedding；句向量模型也有自己的配套分词器。
- KV Cache：同一请求的 Token 数增加会扩大 Prefill 工作量和缓存占用。

## 资料来源

- Sennrich、Haddow 与 Birch，[Neural Machine Translation of Rare Words with Subword Units](https://aclanthology.org/P16-1162/)，ACL 2016；BPE 子词方法原始论文，访问于 2026-09-09。
- Kudo 与 Richardson，[SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing](https://aclanthology.org/D18-2012/)，EMNLP 2018；介绍直接从原始句子训练 BPE/Unigram 分词模型，访问于 2026-09-09。
- Google Research，[BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://research.google/pubs/bert-pre-training-of-deep-bidirectional-transformers-for-language-understanding/)，2018；记录 BERT 使用 WordPiece 词表，访问于 2026-09-09。
