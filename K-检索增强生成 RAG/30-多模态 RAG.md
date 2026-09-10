---
type: concept
domain:
  - RAG
depth: L4
importance: extension
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - 图文检索增强
tags:
  - multimodal
  - document-retrieval
---

# 多模态 RAG

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

很多知识不只存在于连续文本：财报有表格，维修手册有部件图，合同扫描件有版面和印章。多模态 RAG 让查询能召回文字、图片、页面区域或跨模态证据，并把原始位置交给多模态模型解释。

## 不理解会造成什么错误

- 只做 OCR，丢失表格行列、图片和页面关系。
- 图像向量命中，却只把 OCR 文本交给生成模型。
- 将整页截图当成一个 Chunk，无法精确引用区域。
- 文本和图像分数未经校准直接相加。
- 不记录 OCR 与解析版本，重建后结果无法复现。

## 它在 RAG 链路中的位置

摄取时保留文件、页码、区域坐标、模态、父子关系和派生文本。索引可包含 OCR 文本向量、图像向量和版面表示。查询在各模态召回后融合，返回可打开的原始页面与区域，而不是只有一段脱离版面的文字。

## 简单基线

对以正文为主、图片只作装饰的文档，带页码的 OCR 文本检索是合理基线。只有错误分析证明信息藏在图、表或版面关系中，才增加图像编码器或页面级模型。

## 统一证据单元

一个证据单元可以表示为：

```text
e = 文件 ID 页码 区域 模态 派生文本 向量 解析版本
```

父页面用于展示，子区域用于检索。区域坐标通常归一化到 `[0,1]`，便于不同分辨率之间映射：

$$
x'=\frac{x}{W},\qquad y'=\frac{y}{H}
$$

显示到新画布 $(W',H')$ 时再用 $x=x'W'$、$y=y'H'$ 还原。

## 跨模态检索

若文本查询向量 $q$ 与图像区域向量 $v_i$ 位于兼容空间，可用余弦相似度：

$$
s_i=\frac{q^Tv_i}{\lVert q\rVert\lVert v_i\rVert}
$$

若使用不同编码器，分数尺度可能不同，应在固定集上校准或用名次融合。相似度只表明表示接近，不证明区域真的回答问题。

## 最小手算

页面宽 1000、高 2000，图表区域为 `(100,400,600,1200)`。归一化后是 `(0.1,0.2,0.6,0.6)`。在宽 500、高 1000 的预览图中还原为 `(50,200,300,600)`，仍指向同一相对区域。

## 可执行实验

```python
def normalize_box(box, width, height):
    x1, y1, x2, y2 = box
    return x1 / width, y1 / height, x2 / width, y2 / height

def restore_box(box, width, height):
    x1, y1, x2, y2 = box
    return tuple(round(value) for value in
                 (x1 * width, y1 * height, x2 * width, y2 * height))

original = (100, 400, 600, 1200)
normalized = normalize_box(original, 1000, 2000)
preview = restore_box(normalized, 500, 1000)
print("normalized", normalized, "preview", preview)
assert normalized == (0.1, 0.2, 0.6, 0.6)
assert preview == (50, 200, 300, 600)

evidence = {"file_id": "manual-7", "page": 4, "box": normalized,
            "modality": "chart", "parser_version": "v3"}
required = {"file_id", "page", "box", "modality", "parser_version"}
assert required <= evidence.keys()

registry = {
    "E-text": {**evidence, "modality": "text", "box": (0.1, 0.1, 0.9, 0.2)},
    "E-chart": evidence,
}
def resolve_citation(evidence_id):
    if evidence_id not in registry:
        raise ValueError("unknown_evidence")
    item = registry[evidence_id]
    return item["file_id"], item["page"], item["box"], item["modality"]

assert resolve_citation("E-text")[-1] == "text"
assert resolve_citation("E-chart") == ("manual-7", 4, normalized, "chart")
try:
    resolve_citation("E-missing")
except ValueError as error:
    assert str(error) == "unknown_evidence"
else:
    raise AssertionError("未知证据必须拒绝")
```

实验验证坐标与来源协议，并让文本和图表证据都回到文件、页码、区域与模态；未知引用会被拒绝。它不能证明 OCR 或跨模态 Embedding 的质量，真实系统需在人工标注的页级、区域级相关性上评测。

## 上下文怎样交给模型

生成模型需要看到与任务相符的表示：文字问题可提供 OCR 片段；图表推理还应提供裁剪图和周围标题；表格应保留行列结构。上下文中使用不可伪造的证据 ID，最终引用链接回原文件、页码和高亮区域。

## 质量延迟与成本影响

页面渲染、OCR、图像编码和多模态推理比纯文本昂贵。可先用便宜文本召回，再对候选页做视觉重排；但这会漏掉没有有效 OCR 的纯视觉证据。索引大小、图像分辨率、候选页数和生成输入像素都要纳入预算。

## 数据评测与安全风险

按扫描质量、语言、版面、表格、图表和手写内容切片。OCR 文本可能泄露原图中的个人信息，图片本身也需权限过滤。外部图片和 PDF 可包含提示注入文字，作为不可信证据处理。记录原文件哈希、解析器、OCR、模型和索引版本。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 文字命中但表格答错 | 行列结构在 OCR 中丢失 | 原始区域、表格解析、单元格关系 |
| 引用页正确但位置错误 | 坐标系或旋转未统一 | 页尺寸、旋转、归一化坐标 |
| 图片查询召回随机 | 编码空间不兼容 | 模型版本、归一化、跨模态评测 |
| 纯文本效果变差 | 多模态分支分数支配 | 分支切片、校准、名次融合 |
| 重建后引用打不开 | 文件或解析版本漂移 | 文件哈希、页码映射、对象版本 |

## 适用与不适用场景

适合图表、扫描件、产品图片和版面结构决定含义的语料。纯文本已覆盖目标事实时，多模态链路可能只增加成本。视觉模型本身的训练属于多模态 AI，本篇只讨论检索证据链。

## 学习收益

你应能设计带页码与区域的证据单元，区分 OCR 基线与视觉检索，解释跨模态分数边界，并建立区域级引用。

## 给别人讲清楚

“多模态 RAG 不只是把图片转成字，而是保留这段信息在哪一页、哪个区域、是什么模态。模型看到证据，用户也能回到原图核验。”

## 自检问题

1. 为什么 OCR 文本不能完整替代页面图像？
2. 不同模态的原始相似度为什么不能随意相加？
3. 区域坐标为什么要和解析版本一起保存？

## 相关主题

- [RAG 文档解析](04-RAG 文档解析.md)
- [RAG 上下文构建](35-RAG 上下文构建.md)
- [RAG 引用生成](36-RAG 引用生成.md)

## 资料来源

- Alec Radford 等, [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020), 2021，访问日期：2026-09-10。
- Yupan Huang 等, [LayoutLMv3](https://arxiv.org/abs/2204.08387), 2022，访问日期：2026-09-10。
- Manuel Faysse 等, [ColPali](https://arxiv.org/abs/2407.01449), 2024，访问日期：2026-09-10。
