---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [Document Parsing]
tags: [parsing, provenance]
---

# RAG 文档解析

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

文档解析把 PDF、HTML 等载体转换为统一结构，同时保留标题、段落、表格、页码和来源坐标。若只抽取一长串文本，检索可能把表头与单元格拆散，引用也无法打开到原页。

## 不理解会造成什么错误

- 按视觉顺序错误拼接双栏 PDF，句子互相穿插。
- 丢掉标题层级，切分后无法理解段落所属章节。
- 把页眉页脚混进正文，重复噪声主导召回。
- OCR 文本没有置信度和区域坐标，无法核验引用。

## 它在 RAG 链路中的位置

`原始字节与来源记录 → 格式检测 → 解析或 OCR → 统一文档块 → 清洗与切分`。解析输出可表示为 `Document → Block[]`，每个 Block 至少含 `kind`、`text`、`page`、`heading_path` 和可选区域坐标。

## 从 PDF 制度问答开始

员工询问报销上限，答案在第 12 页“差旅标准”表格。简单基线是 PDF 全文复制；它可能丢表格关系。结构解析保留页码、标题和表格行，使后续 Chunk 能携带可核验来源。

## 从坐标到阅读顺序

设页面块 $b_i=(x_i,y_i,w_i,h_i,t_i)$。单栏页面可先按纵坐标、再按横坐标排序：

$$
b_i < b_j\iff y_i<y_j\ \text{或}\ (y_i=y_j\land x_i<x_j)
$$

双栏、浮动图注和跨页表格不能只靠此规则，需要版面模型或显式启发式。来源映射为：

$$
\operatorname{origin}(b_i)=(source\_id,version,page,bbox)
$$

它让检索文本能够反查原文，而不是只保存不可验证的纯文本。

## 最小手算

页面有标题块 `(y=10,x=10)`、左栏正文 `(30,10)`、右栏正文 `(30,300)`。单栏排序得到标题、左栏、右栏。但若左右两栏各有多行，逐行按 y 排序会左右交错，说明排序假设必须与版面类型一起记录。

## 可执行实验

```python
blocks = [
    {"text": "每天不超过 500 元", "kind": "paragraph", "page": 2, "x": 20, "y": 80},
    {"text": "差旅标准", "kind": "heading", "page": 2, "x": 20, "y": 20},
    {"text": "住宿费", "kind": "table_header", "page": 2, "x": 20, "y": 60},
]
ordered = sorted(blocks, key=lambda block: (block["page"], block["y"], block["x"]))
heading, records = None, []
for block in ordered:
    if block["kind"] == "heading":
        heading = block["text"]
    records.append({"text": block["text"], "page": block["page"],
                    "heading_path": [heading] if heading else []})
print(records)
assert [item["text"] for item in records] == ["差旅标准", "住宿费", "每天不超过 500 元"]
assert records[-1]["heading_path"] == ["差旅标准"]
assert all(item["page"] == 2 for item in records)
invalid = {"text": "未知来源", "page": None}
assert invalid["page"] is None  # 失败分支：不能生成可核验页码引用
```

## 实验结果边界

实验说明结构和页码可沿阅读顺序传播，不代表简单坐标排序能解析真实双栏 PDF、扫描件或合并单元格。生产解析器要用代表性版面集测量顺序、表格和来源映射准确率。

## 质量延迟与成本影响

结构解析通常比纯文本提取慢，却可能改善切分和引用。OCR 进一步增加计算成本。可按 MIME 类型路由：原生文本走快速路径，扫描页才 OCR；缓存应绑定原始哈希与解析器版本。

## 数据评测与安全风险

加密或受限文档不可绕过权限解析。日志不应记录全文和敏感表格。对标题、段落、表格、页码、阅读顺序分别抽样评测；解析器升级要做版本对照，防止静默改变 Chunk ID。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 句子顺序混乱 | 双栏被当作单栏 | 页面布局、坐标排序、代表性样本 |
| 表格答案缺字段 | 单元格关系丢失 | 表头映射、跨页表、合并单元格 |
| 引用打不开原处 | 页码或 bbox 未传播 | origin 字段、页码基准、版本 |
| 搜索命中大量页脚 | 模板未标记 | block kind、重复频率、清洗规则 |
| 扫描件为空 | 未触发 OCR | MIME 检测、文字层、OCR 状态 |

## 适用与不适用场景

适合 PDF、HTML、演示稿等有结构和来源要求的材料。纯文本日志可用简单解析器，但仍要保留行号和来源。解析不负责删除业务无效内容，也不应在不确定时悄悄改写原文。

## 学习收益

你应能设计统一 Block 模型，解释阅读顺序假设，保留来源坐标，并为不同格式制定解析评测。

## 给别人讲清楚

“解析不是把文件变成一串字，而是把字连同它在哪一页、属于哪个标题、在表格哪里一起保存。这样检索结果才有上下文和出处。”

## 自检问题

1. 为什么页码和标题属于检索数据而非展示附属物？
2. 单纯按纵坐标排序为什么会破坏双栏页面？
3. 解析器升级为什么可能要求重建索引？

## 相关主题

- [RAG 数据摄取](03-RAG%20数据摄取.md)
- [RAG 文档清洗](05-RAG%20文档清洗.md)
- [多模态 RAG](30-多模态%20RAG.md)

## 资料来源

- W3C, [Document Object Model](https://www.w3.org/TR/dom/)，访问日期：2026-09-10。
- Adobe, [PDF Reference](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdflsdk/)，访问日期：2026-09-10。
- Smith, [An Overview of the Tesseract OCR Engine](https://ieeexplore.ieee.org/document/4376991), 2007，访问日期：2026-09-10。
