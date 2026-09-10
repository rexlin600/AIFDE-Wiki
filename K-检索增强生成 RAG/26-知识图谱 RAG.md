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
  - Knowledge Graph RAG
tags:
  - knowledge-graph
  - graph-query
---

# 知识图谱 RAG

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

文本相似度难以可靠回答精确关系和约束，例如“哪些已获批药物作用于靶点 T，且适应症为疾病 D”。知识图谱 RAG 把实体和有类型的关系保存为三元组，再执行受约束图查询，并把结果与原始文本证据一起交给生成器。

若不理解，会把实体抽取结果当真相、生成任意图查询、忽略方向与时间，或只给图中结论而没有原文依据。简单基线是元数据过滤加文本检索；只有关系约束稳定、问题确需精确遍历时才构图。

## 链路位置与图模型

离线链路为 `文档 → 实体对齐 → 关系抽取或导入 → 三元组和来源`；在线为 `查询 → 受限查询计划 → 图遍历 → 文本证据 → 生成`。三元组写作 $(h,r,t)$：头实体 $h$ 经关系 $r$ 指向尾实体 $t$。

给定关系序列 $r_1,r_2$，两跳答案集合为：

$$
A=\{z\mid\exists y:(x,r_1,y)\in E\land(y,r_2,z)\in E\}
$$

这只是集合连接。若第一跳有 $n_1$ 个候选，每个平均再连 $d$ 个节点，未过滤的中间结果最多约 $n_1d$；类型、权限和时间过滤应尽早执行以控制爆炸。

## 最小手算

三元组有 `(药物甲, 作用于, T)`、`(药物甲, 获批用于, D)`、`(药物乙, 作用于, T)`。同时满足两个关系的交集只有药物甲。只检索“作用于 T”会错误地把药物乙也作为答案。

## 可执行实验

```python
TRIPLES = [
    ("药物甲", "作用于", "T", "doc-1", "public"),
    ("药物甲", "获批用于", "D", "doc-2", "public"),
    ("药物乙", "作用于", "T", "doc-3", "public"),
    ("药物乙", "获批用于", "D", "doc-4", "restricted"),
    ("药物甲", "生产商", "公司丙", "doc-unrelated", "public"),
]

def subjects(relation, target, allowed_labels):
    return {
        head for head, rel, tail, _, label in TRIPLES
        if rel == relation and tail == target and label in allowed_labels
    }

def constrained_query(allowed_labels):
    targets = subjects("作用于", "T", allowed_labels)
    approved = subjects("获批用于", "D", allowed_labels)
    answers = sorted(targets & approved)
    required_edges = {("作用于", "T"), ("获批用于", "D")}
    sources = sorted(doc for h, rel, tail, doc, label in TRIPLES
                     if h in answers and (rel, tail) in required_edges
                     and label in allowed_labels)
    return answers, sources

answers, sources = constrained_query({"public"})
assert answers == ["药物甲"] and sources == ["doc-1", "doc-2"]
assert "doc-unrelated" not in sources
assert "药物乙" not in answers
assert constrained_query({"public", "restricted"})[0] == ["药物乙", "药物甲"]
print(answers, sources)
```

实验验证有类型关系的交集、来源回溯和边级权限，不验证三元组抽取是否正确，也不等同医学结论。

## 质量延迟成本与风险

知识图谱提升可解释的关系约束，却带来本体设计、实体消歧、关系抽取和更新成本。报告实体链接准确率、关系准确率、查询答案精确率和召回率、证据覆盖、图查询延迟与维护成本；和文本检索基线使用同一问题集。

图查询模板、关系类型和最大跳数需白名单化，不能直接执行模型生成的任意查询。节点与边均携带权限、有效期和来源；删除原文需删除或重建派生关系。高风险领域由权威数据库和人工审核兜底。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 查不到已知实体 | 别名未对齐 | 实体链接与规范 ID |
| 关系方向相反 | 谓词建模或抽取错误 | 三元组方向与原文 |
| 多跳结果爆炸 | 类型过滤太晚 | 每跳候选数与查询计划 |
| 出现受限关系 | 边级权限遗漏 | 图查询过滤与来源标签 |

## 适用边界与学习收益

适合实体、关系和约束相对稳定的合规、医药、供应链场景；开放叙事、小语料或变化极快的知识先用文本 RAG。学完应能手算关系交集，区分图事实、抽取判断和原文证据。

复述：知识图谱 RAG 像按关系类型查档案，先精确做集合连接，再拿原始文件给答案作证。

自检：为什么图查询仍需要文本证据？何时应早做过滤？GraphRAG 社区摘要与知识图谱精确查询有何不同？

## 相关主题

- [GraphRAG](<25-GraphRAG.md>)
- [RAG 多跳检索](<19-RAG 多跳检索.md>)
- [RAG 权限控制](<31-RAG 权限控制.md>)

## 资料来源

- Heiko Paulheim, [Knowledge Graph Refinement A Survey of Approaches and Evaluation Methods](https://doi.org/10.3233/SW-160218), 2017，访问日期：2026-09-10。
- Yu Gu 等, [A Survey of Knowledge Graph Reasoning on Graph Types](https://arxiv.org/abs/2212.11774), 2022，访问日期：2026-09-10。
