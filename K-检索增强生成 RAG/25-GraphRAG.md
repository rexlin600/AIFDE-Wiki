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
  - GraphRAG
tags:
  - graph-rag
  - community-summary
---

# GraphRAG

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

向量检索擅长找与查询相似的片段，却不天然回答“整个投诉库有哪些主要问题以及它们如何关联”。GraphRAG 从文本抽取实体关系图、发现社区并生成分层摘要：局部问题检索实体邻域，全局问题聚合社区报告。

它不是所有图 RAG 的统称。本篇侧重文本语料的图抽取和社区摘要；显式本体与精确图查询见知识图谱 RAG。只有普通检索在全局主题问题上不足，且图构建成本合理时才采用。

## 链路位置与数据形状

离线：`Chunk → 实体关系抽取 → 图 G=(V,E) → 社区 → 社区摘要`。在线：`查询分类 → 局部邻域或全局社区 → 原文证据 → 回答`。每条边必须保存来源 Chunk，摘要也要能回溯原文。

局部检索可用节点 $v$ 的一跳邻域：

$$
N(v)=\{u\mid(v,u)\in E\}
$$

全局聚合若社区 $C_i$ 的相关分为 $s_i$、摘要为 $z_i$，可取预算内 top-k，再生成答案。不能把社区摘要本身当无损事实；它是有信息损失的派生索引。

无权图的度数为 $d(v)=|N(v)|$。访问一个节点及其一跳邻域的节点量至多 $1+d(v)$；全局路径要读多个社区摘要，成本随社区数和摘要长度增加。

## 最小手算

图有边 `支付—重复扣款`、`支付—退款慢`、`登录—验证码失败`。查询“支付相关问题”从“支付”出发得到两个邻居，共访问 3 个节点；查询“全部主要问题”则要读取支付社区和登录社区两个摘要。前者是局部，后者是全局。

## 可执行实验

```python
GRAPH = {
    "支付": {"重复扣款", "退款慢"},
    "重复扣款": {"支付"},
    "退款慢": {"支付"},
    "登录": {"验证码失败"},
    "验证码失败": {"登录"},
}
COMMUNITIES = {
    "支付社区": {"支付", "重复扣款", "退款慢"},
    "登录社区": {"登录", "验证码失败"},
    "混合社区": {"支付", "验证码失败"},
}

def local(entity, allowed):
    nodes = {entity} | GRAPH.get(entity, set())
    return sorted(nodes & allowed)

def global_reports(allowed):
    # 摘要可能包含全部支撑节点的信息，只有全部节点可见时才可返回。
    return sorted(name for name, nodes in COMMUNITIES.items()
                  if nodes and nodes <= allowed)

allowed = {"支付", "重复扣款", "退款慢"}
assert local("支付", allowed) == ["支付", "退款慢", "重复扣款"]
assert global_reports(allowed) == ["支付社区"]
assert "混合社区" not in global_reports(allowed)
assert "验证码失败" not in local("支付", allowed)
print(local("支付", allowed), global_reports(allowed))
```

实验用内存图验证局部路径，并断言混合权限社区摘要不可见。这里采用“全部支撑节点均可见”这一保守规则；生产系统也可按权限域分别生成摘要。实验不执行实体抽取、社区发现或摘要生成，不能证明真实 GraphRAG 的质量。

## 质量延迟成本与风险

GraphRAG 可能提升全局主题覆盖和关系导航，却增加抽取、消歧、社区重建与摘要成本。评测实体和边准确率、社区覆盖、主张到原文支持率、局部与全局任务质量、索引构建时间、在线延迟和 Token 成本；与向量检索基线分题型比较。

权限必须作用于节点、边、社区摘要和原文；一个混合权限社区摘要可能泄露受限事实。删除文档时传播到边、社区和摘要。防范恶意文本伪造关系，图版本应和语料版本绑定。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 同一实体被拆成多个节点 | 实体消歧失败 | 别名表与来源样本 |
| 全局答案遗漏主题 | 社区划分或摘要丢失 | 社区覆盖与原文回溯 |
| 图中关系与原文不符 | 抽取幻觉 | 边的来源 Chunk |
| 摘要泄露受限信息 | 社区跨权限聚合 | 节点边摘要权限标签 |

## 适用边界与学习收益

适合大语料的全局主题、跨文档关系和探索式问题；精确事实查找、小语料或频繁更新场景通常先用普通 RAG。学完应能区分局部邻域与全局社区，并解释摘要的信息损失。

复述：GraphRAG 先把材料画成关系地图，再为地图分区写摘要；问附近路线看邻域，问全城概况看分区，但最终仍要回原文核实。

自检：GraphRAG 为什么比向量索引更新更贵？社区摘要为何不能直接视为事实？权限过滤要覆盖哪些派生对象？

## 相关主题

- [知识图谱 RAG](<26-知识图谱 RAG.md>)
- [RAPTOR 递归检索](<28-RAPTOR 递归检索.md>)
- [RAG 引用生成](<36-RAG 引用生成.md>)

## 资料来源

- Darren Edge 等, [From Local to Global A Graph RAG Approach](https://arxiv.org/abs/2404.16130), 2024，访问日期：2026-09-10。
- Microsoft Research, [GraphRAG](https://github.com/microsoft/graphrag), 访问日期：2026-09-10。
