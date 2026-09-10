---
type: concept
domain: [RAG]
depth: L2
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Document Cleaning]
tags: [cleaning, deduplication]
---

# RAG 文档清洗

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

文档清洗删除导航、页眉、重复版本和无意义空白，却保留真正的业务正文。它减少噪声竞争，让有限的 Top-k 和上下文预算留给有效证据。

## 不理解会造成什么错误

- 用过强正则误删“免责声明”章节中的关键限制。
- 只按整文档哈希去重，漏掉模板页和近重复版本。
- 清洗时改写数字或否定词，让证据含义改变。
- 清洗后丢失原文偏移，引用无法回到源文档。

## 它在 RAG 链路中的位置

`解析块 → 规范化 → 模板检测 → 去重与敏感信息策略 → 清洗块 → 切分`。清洗输出要保留原始 Block ID、规则版本和删除原因，原文仍是审计依据。

## 从帮助中心开始

每个网页都含同一导航栏“首页 产品 联系我们”。简单基线是不清洗直接切分，导航词会出现在大量 Chunk 中。清洗器可根据跨文档重复率和块类型删除模板，但不能因为一句话常见就删除正文。

## 用频率理解模板检测

设语料有 $N$ 篇文档，标准化块文本 $s$ 出现在 $df(s)$ 篇中，其文档频率为：

$$
p(s)=\frac{df(s)}{N}
$$

当 $p(s)$ 很高且块被解析为 `header` 或 `footer` 时，可标记为模板。仅凭高频不足以删除，因为“安全须知”等正文也可能高频。精确去重可用规范化文本哈希，近重复需要单独评测指纹阈值。

## 最小手算

5 篇网页中“联系我们”出现在 5 篇，$p=1$；“退款期限 7 天”出现在 2 篇，$p=0.4$。若阈值 0.8，前者且类型为 footer 可删除；后者保留。即使“安全须知”出现 5 次，只要是正文也不能按此规则自动删除。

## 可执行实验

```python
from collections import Counter

docs = [
    [("header", "产品中心"), ("body", "退款期限 7 天"), ("footer", "联系我们")],
    [("header", "产品中心"), ("body", "保修期限 1 年"), ("footer", "联系我们")],
    [("header", "产品中心"), ("body", "安全须知"), ("footer", "联系我们")],
]
frequency = Counter(text for doc in docs for _, text in set(doc))

def clean(doc, threshold=0.8):
    output, removed = [], []
    for kind, text in doc:
        ratio = frequency[text] / len(docs)
        if kind in {"header", "footer"} and ratio >= threshold:
            removed.append((kind, text, "repeated_template"))
        else:
            output.append((kind, " ".join(text.split())))
    return output, removed

cleaned, removed = clean(docs[2])
print(cleaned, removed)
assert ("body", "安全须知") in cleaned  # 高频正文不得误删
assert all(kind not in {"header", "footer"} for kind, _ in cleaned)
assert len(removed) == 2
```

## 实验结果边界

实验验证“高频 + 结构类型”的保守规则能保留高频正文。它不代表该阈值适合真实网站，也没有解决近重复、OCR 噪声或 PII 自动识别；这些需要人工标注样本验证误删率与漏删率。

## 质量延迟与成本影响

清洗可减少索引体积、Embedding 计算和重复召回。全语料频率统计需要额外扫描，增量系统要维护计数或定期重算。过度清洗造成不可恢复的信息损失，因此保留原始快照和规则版本。

## 数据评测与安全风险

敏感信息不能只靠正则删除，需分类、访问策略和人工复核。记录清洗前后字符数、删除类型、误删样本和版本。测试集不能与阈值调参样本混用，避免只对已知模板有效。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 关键限制消失 | 规则按关键词误删正文 | 删除日志、原文映射、误删率 |
| Top-k 全是导航 | 模板检测漏删 | block kind、跨文档频率、规范化 |
| 重复答案仍很多 | 仅做整文档去重 | 块哈希、近重复版本、canonical URL |
| 数字含义改变 | 清洗规则重写内容 | 规则差异、数字和否定词单测 |
| 引用位置错乱 | 未保留偏移映射 | 原始 Block ID、字符映射、版本 |

## 适用与不适用场景

适合模板多、重复多或 OCR 噪声明显的语料。小型高质量纯文本可只做空白规范化。清洗不应替代权限控制，也不应为“更通顺”而生成式改写事实原文。

## 学习收益

你应能用结构类型和语料统计设计保守清洗规则，解释误删与漏删，并保留原文可追踪性。

## 给别人讲清楚

“清洗像给知识除尘：删的是包装和重复，不是改写内容。每次删除都要能说明规则，并能回到原文核验。”

## 自检问题

1. 为什么高频文本不一定是模板？
2. 清洗为什么要保存删除原因与规则版本？
3. 降低索引体积是否足以证明清洗有效？

## 相关主题

- [RAG 文档解析](04-RAG%20文档解析.md)
- [RAG 文档切分](06-RAG%20文档切分.md)
- [RAG 数据摄取](03-RAG%20数据摄取.md)

## 资料来源

- Bar-Yossef 与 Rajagopalan, [Template Detection via Data Mining and its Applications](https://dl.acm.org/doi/10.1145/956863.956901), 2002，访问日期：2026-09-10。
- W3C, [HTML Standard](https://html.spec.whatwg.org/)，访问日期：2026-09-10。
- NIST, [Privacy Framework](https://www.nist.gov/privacy-framework)，访问日期：2026-09-10。
