---
type: concept
domain:
  - RAG
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - 检索授权
tags:
  - authorization
  - security
---

# RAG 权限控制

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

企业 RAG 会把许多用户原本分散可见的文档放进统一检索系统。权限控制保证每次检索只能产生当前主体有权读取的候选，避免模型在回答、引用、缓存或日志中泄露机密内容。

## 不理解会造成什么错误

- 检索全部文档后才让模型“不要引用”越权内容。
- 只隐藏正文，却从标题、摘要、命中数或相似度泄露存在性。
- 文档权限变更后，旧 Chunk 和缓存仍可见。
- 用用户传入的角色字符串决定权限。
- 只测试正常用户，不注入跨部门和权限撤销样例。

## 它在 RAG 链路中的位置

身份由可信认证系统建立，授权策略把主体、资源、动作和上下文映射为允许或拒绝。过滤必须在向量或倒排候选被读取的边界内执行；返回的 Chunk、父文档、引用和缓存都继承同一权限判定。

## 简单基线

小型单团队知识库可按独立索引隔离。数据共享复杂后，使用文档或 Chunk 元数据的检索前过滤与统一策略服务。无论哪种方案，都不能依赖 Prompt 充当权限层。

## 授权关系

属性访问控制可抽象为：

$$
\operatorname{allow}(s,r,a,c)\in\{0,1\}
$$

$s$ 是可信主体属性，$r$ 是资源属性，$a$ 是动作，$c$ 是时间、网络或用途等上下文。RAG 的读取集合为：

$$
C_{visible}=\{d\in C\mid \operatorname{allow}(s,d,\mathrm{read},c)=1\}
$$

检索应在 $C_{visible}$ 内排名，而不是先对 $C$ 排名再把结果交给模型过滤。

## 最小手算

候选前 3 名中，第 1 和第 2 名越权，第 3 名可见。若先取 Top-2 再过滤，结果为空；若在检索边界内过滤再排序，可见文档成为第 1 名。这说明权限过滤的位置还会影响召回质量。

## 可执行实验

```python
DOCUMENTS = [
    {"id": "d1", "score": 0.99, "groups": {"finance"}},
    {"id": "d2", "score": 0.95, "groups": {"legal"}},
    {"id": "d3", "score": 0.80, "groups": {"support"}},
]

def retrieve(user_groups, top_k):
    visible = [doc for doc in DOCUMENTS if doc["groups"] & user_groups]
    return sorted(visible, key=lambda doc: doc["score"], reverse=True)[:top_k]

support_results = retrieve({"support"}, 2)
finance_results = retrieve({"finance"}, 2)
assert [doc["id"] for doc in support_results] == ["d3"]
assert [doc["id"] for doc in finance_results] == ["d1"]
assert not ({doc["id"] for doc in support_results} & {"d1", "d2"})
print("support", support_results, "finance", finance_results)
```

实验验证集合过滤，不覆盖真实搜索引擎是否把过滤下推到索引、策略缓存是否及时失效，或父子文档权限是否一致。

## 权限传播

原文档、派生 Chunk、摘要、Embedding、父文档和引用必须共享资源标识与权限版本。权限撤销或删除形成事件，更新所有索引并使相关缓存失效。无法证明传播完成时，应宁可拒绝读取，而不是继续使用旧权限。

## 缓存与日志

缓存键至少包含主体可见性范围或不可伪造的权限摘要、查询、索引版本和模型配置。共享缓存不能返回高权限用户生成的答案。日志避免记录越权候选正文；审计应能回答谁在何时以哪个策略版本读取了哪些资源。

## 质量延迟与成本影响

复杂过滤可能降低 ANN 索引效率，过细 ACL 也增加元数据和策略调用成本。可按权限域分区或使用支持过滤的索引，但要防止分区爆炸。优化前先测不同权限选择性的 Recall、P95 延迟和空结果率。

## 数据评测与安全风险

建立授权矩阵和否定测试：无权限、权限撤销、嵌套组、临时授权、父子资源冲突、缓存复用和引用打开。提示注入无法提升权限。不要把敏感内容交给模型后再靠回答过滤；中间候选、Embedding 和 Trace 都属于受保护数据。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 回答泄露机密标题 | 只过滤正文或生成结果 | 候选、元数据、引用与日志 |
| 合法用户召回为空 | Top-k 后过滤 | 过滤下推、候选窗口、策略 |
| 撤权后仍能查询 | 索引或缓存未失效 | 权限版本、事件、缓存键 |
| 父 Chunk 可见子 Chunk 越权 | 派生资源未继承策略 | 资源 ID、ACL 传播、重建 |
| 用户伪造角色成功 | 信任请求参数 | 身份令牌、服务端属性 |

## 适用与不适用场景

任何包含非公开或分级数据的 RAG 都必须实施。公开语料也要考虑删除与地区限制。Prompt 安全措辞、答案后处理和客户端隐藏都不是授权替代品。

## 学习收益

你应能说明授权为何必须进入检索边界，设计主体资源属性，处理权限传播与缓存，并编写越权否定测试。

## 给别人讲清楚

“先把无权看的书从书架视野中拿走，再做排名。不能把机密页先交给模型，然后提醒它别说出去。”

## 自检问题

1. Top-k 后过滤为什么会同时造成安全和召回问题？
2. 权限撤销需要传播到哪些派生对象？
3. 为什么缓存键只含查询文本不安全？

## 相关主题

- [RAG 元数据](07-RAG 元数据.md)
- [RAG 多租户隔离](32-RAG 多租户隔离.md)
- [RAG 流式更新](34-RAG 流式更新.md)

## 资料来源

- NIST, [Attribute Based Access Control](https://csrc.nist.gov/publications/detail/sp/800-162/upd-2/final)，访问日期：2026-09-10。
- NIST, [Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)，访问日期：2026-09-10。
- OWASP, [LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)，访问日期：2026-09-10。
