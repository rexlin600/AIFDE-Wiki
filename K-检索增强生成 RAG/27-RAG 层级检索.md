---
type: concept
domain:
  - RAG
depth: L3
importance: extension
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Hierarchical Retrieval
tags:
  - hierarchical-retrieval
  - tree-search
---

# RAG 层级检索

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

企业手册天然有目录、章节和段落。把全部段落放在一个平面索引中，通用词可能召回错误章节。层级检索先选文档或章节，再在其子节点中检索细节。例如先定位“报销制度”，再定位“差旅住宿标准”。

它会产生级联错误：父层选错，正确段落就永远看不到。先用全库平面检索做基线；只有范围噪声明显、层级可靠时才采用。

## 链路位置与树状态

离线保留 `文档 → 章节 → 段落` 的父子 ID 和权限。在线：`查询 → 父节点候选 → 子节点候选 → 原文`。若第 $l$ 层保留 $b_l$ 个节点，查询评分次数约为：

$$
C=\sum_{l=1}^{L}|\operatorname{children}(B_{l-1})|
$$

$B_{l-1}$ 是上一层保留集合。它通常小于对所有叶子评分，但正确叶子的可达概率受每层召回限制。若每层条件召回为 $r_l$，粗略的端到端可达率为：

$$
R_{\text{path}}=\prod_{l=1}^{L}r_l
$$

这是在按路径条件统计时的乘法。例如两层各 0.9，完整路径只有 $0.9^2=0.81$。

## 最小手算

两章各有 3 段。平面检索需比较 6 段；层级法先比较 2 章，再比较入选章的 3 段，共 5 次。若章级漏掉正确章节，段级再强也无法恢复，因此父层常需保留 top-2 或设置低置信回退到平面检索。

## 可执行实验

```python
TREE = {
    "root": ["报销", "安全"],
    "报销": ["交通", "住宿", "餐饮"],
    "安全": ["密码", "门禁", "备份"],
}
TEXT = {
    "报销": "差旅 费用", "安全": "系统 防护",
    "交通": "车票", "住宿": "酒店 标准", "餐饮": "餐补",
    "密码": "口令", "门禁": "访客", "备份": "恢复",
}

def score(query, node):
    return len(set(query.split()) & set(TEXT[node].split()))

def hierarchical(query, allowed, parent_k=1):
    parents = sorted(TREE["root"], key=lambda n: score(query, n), reverse=True)
    parents = [p for p in parents if p in allowed][:parent_k]
    leaves = [leaf for p in parents for leaf in TREE[p] if leaf in allowed]
    return sorted(leaves, key=lambda n: score(query, n), reverse=True), parents

allowed = set(TEXT)
leaves, parents = hierarchical("差旅 酒店 标准", allowed)
assert parents == ["报销"] and leaves[0] == "住宿"
restricted = allowed - {"安全", "密码", "门禁", "备份"}
assert "安全" not in hierarchical("系统 防护", restricted)[1]
print(parents, leaves)
```

实验验证内存树的逐层缩小与权限过滤，不证明词重叠评分适合真实语义，也未模拟父层召回率。

## 质量延迟成本与风险

层级检索减少候选和跨章节噪声，但增加父层查询，且误差逐层累积。报告每层 Recall@k、完整路径召回、最终段落质量、评分节点数、延迟和索引大小；与平面检索和父层不同 top-k 做消融。

权限须在父节点和子节点都生效；父标题、节点计数也可能泄露信息。重命名或移动章节时要原子更新父子关系和缓存。提示注入文本仍只能作为数据。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 正确段落完全不可见 | 父层被剪枝 | 各层 Recall 与路径日志 |
| 候选没有减少 | 父层 top-k 过大 | 每层展开节点数 |
| 移动章节后重复 | 父子关系更新不完整 | 树版本与孤儿节点 |
| 标题暴露敏感项目 | 父层未做权限过滤 | 节点级 ACL 与缓存 |

## 适用边界与学习收益

适合具有可靠目录的大型手册、代码库和法规；结构扁平、层级经常变化或查询跨多个章节时，平面或混合检索更稳。学完应能推导路径召回乘积并解释父层回退。

复述：层级检索像先找书架、再找书、最后找页；省了搜索范围，但第一步走错就看不到正确页。

自检：为什么每层 90% 并不等于整体 90%？何时保留多个父节点？为何父标题也要授权？

## 相关主题

- [父子文档检索](<12-父子文档检索.md>)
- [RAPTOR 递归检索](<28-RAPTOR 递归检索.md>)
- [RAG 文档切分](<06-RAG 文档切分.md>)

## 资料来源

- Luyu Gao 等, [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496), 2022，访问日期：2026-09-10。
- Parth Sarthi 等, [RAPTOR](https://arxiv.org/abs/2401.18059), 2024，访问日期：2026-09-10。
