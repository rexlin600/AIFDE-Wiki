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
  - RAPTOR
tags:
  - raptor
  - recursive-summary
---

# RAPTOR 递归检索

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

叶子 Chunk 保留细节，却难回答跨多段的高层问题。RAPTOR 递归地聚类语义相近节点、为每簇生成摘要，再把摘要继续聚类成树；查询可同时检索不同层的摘要与原文。长报告问答因而既能找局部数字，也能找跨章节主题。

摘要会丢信息甚至引入错误，树构建和更新也昂贵。先比较平面 Chunk 检索与简单章节摘要；只有跨段综合问题仍明显不足才采用递归树。

## 链路位置与递归结构

离线：`叶子 Chunk → 向量 → 聚类 → 摘要父节点 → 重复直到根或停止`。在线：`查询 → 跨层评分或树遍历 → 原文回溯 → 生成`。定义第 0 层为原文节点集合 $V_0$：

$$
V_{l+1}=\{\operatorname{summary}(C)\mid C\in\operatorname{cluster}(V_l)\}
$$

若每个父节点平均合并 $b>1$ 个子节点，$n$ 个叶子的理想平衡树深度约为 $\lceil\log_b n\rceil$。忽略每层向上取整、假设满树时，总节点数近似为：

$$
n+\frac{n}{b}+\frac{n}{b^2}+\cdots < \frac{bn}{b-1}
$$

实际分组要向上取整，精确递推是 $n_0=n$、$n_{l+1}=\lceil n_l/b\rceil$，总数为 $\sum_l n_l$，因此上式不是任意 $n$ 的严格上界。例如 $n=5,b=2$ 时各层为 5、3、2、1，总数 11，大于 $2n=10$。停止条件应包含最大层数、只剩一个节点或节点数不再减少。

## 最小手算

8 个叶子每 2 个合成一个父节点：各层节点数是 8、4、2、1，深度 3，总节点 15，小于 $2\times8=16$。若某个父摘要遗漏“退款期限 7 天”，只检索该摘要就会丢失事实，因此答案要回溯叶子证据。

## 可执行实验

```python
def build_tree(leaves, branch=2, max_levels=4):
    levels = [list(leaves)]
    reasons = []
    for _ in range(max_levels):
        current = levels[-1]
        if len(current) <= 1:
            reasons.append("single_root")
            break
        parents = []
        for i in range(0, len(current), branch):
            children = current[i:i + branch]
            parents.append({"summary": " | ".join(str(x) for x in children),
                            "children": children})
        if len(parents) >= len(current):
            reasons.append("no_reduction")
            break
        levels.append(parents)
        if len(parents) == 1:
            reasons.append("single_root")
            break
    else:
        reasons.append("max_levels")
    return levels, reasons[-1]

levels, reason = build_tree(list("ABCDEFGH"), branch=2, max_levels=4)
assert [len(level) for level in levels] == [8, 4, 2, 1]
assert sum(map(len, levels)) == 15 and reason == "single_root"
limited, limited_reason = build_tree(list("ABCDEFGH"), max_levels=1)
assert len(limited) == 2 and limited_reason == "max_levels"
exact, exact_reason = build_tree(list("ABCDEFGH"), max_levels=3)
assert [len(level) for level in exact] == [8, 4, 2, 1]
assert exact_reason == "single_root"
uneven, _ = build_tree(list("ABCDE"), branch=2, max_levels=4)
assert [len(level) for level in uneven] == [5, 3, 2, 1]
assert sum(map(len, uneven)) == 11
print([len(level) for level in levels], reason)
```

实验验证递归节点数、最大层数和终止原因。拼接字符串并非摘要，连续配对也不是语义聚类；实验不能证明 RAPTOR 的真实检索收益。

## 检索和更新怎样做

可把所有层节点放入同一索引做跨层 top-k，或从高层向下展开。前者召回灵活但候选多，后者便宜却有父层剪枝风险。无论哪种，摘要命中后都应返回其子树中的原文节点作引用。

叶子变更会使祖先摘要失效。更新一个叶子时，理想平衡树需重算从叶到根约 $O(\log_b n)$ 个祖先，但重新聚类可能改变更多分支；因此语料高频更新时成本可能不可接受。

## 质量延迟成本与风险

RAPTOR 可能改善概括和跨段问题，却增加嵌入、聚类、摘要、索引节点及更新成本。分别报告细节题和综合题质量、叶子证据支持率、各层命中率、节点膨胀、构建时间、更新范围、查询延迟和 Token 成本；消融平面检索、单层摘要和递归树。

父摘要继承所有子节点的最严格权限，或按权限域分树，不能混合后再过滤。删除传播到祖先并重建摘要。摘要和聚类模型版本必须记录；不可信原文中的指令不能控制摘要流程。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 综合答案仍遗漏事实 | 摘要信息损失 | 摘要到叶子的支持映射 |
| 树层数异常多 | 分支因子或停止条件错误 | 每层节点数与最大层数 |
| 更新后返回旧结论 | 祖先摘要未失效 | 叶到根依赖和索引版本 |
| 摘要泄露受限子节点 | 跨权限聚类 | 聚类域与父节点 ACL |

## 适用边界与学习收益

适合相对稳定的长文档集合和跨段综合问题；高频更新、严格逐字引用或平面检索已足够时不适合。学完应能推导节点数量级、说明递归终止条件，并解释为何摘要命中仍需回到叶子。

复述：RAPTOR 像把段落逐层整理成小结、章摘要和全书摘要；越高层越看全局，也越可能漏细节，所以作答仍回原页举证。

自检：二叉摘要树为何约有 $2n$ 个节点？跨层索引与自顶向下遍历各有什么风险？删除叶子为何必须传播到祖先？

## 相关主题

- [RAG 层级检索](<27-RAG 层级检索.md>)
- [GraphRAG](<25-GraphRAG.md>)
- [RAG 上下文构建](<35-RAG 上下文构建.md>)

## 资料来源

- Parth Sarthi 等, [RAPTOR](https://arxiv.org/abs/2401.18059), 2024，访问日期：2026-09-10。
- Leland McInnes 等, [UMAP](https://arxiv.org/abs/1802.03426), 2018，访问日期：2026-09-10。
