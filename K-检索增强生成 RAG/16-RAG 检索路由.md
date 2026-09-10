---
type: concept
domain:
  - RAG
depth: L3
importance: common
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Retrieval Routing
tags:
  - router
  - fallback
---

# RAG 检索路由

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

企业事实分散在产品文档、工单、数据库和公开网页，不同查询也适合关键词、向量或结构化检索。检索路由根据请求特征选择允许的数据源与检索器，减少无关召回和不必要成本。

## 不理解会造成什么错误

- 所有问题广播到全部索引，延迟、成本和泄露面同时增大。
- 把模型输出的数据源名直接执行，绕过服务端白名单。
- 低置信度仍强制单路，选错后完全召回不到答案。
- 路由分类准确，却没有评估最终检索与回答结果。
- 路由规则更新后没有版本记录，线上错误无法复现。

## 它在 RAG 链路中的位置

```text
查询与认证身份 → 特征 → 允许源交集 → 路由评分
→ 高置信单路 / 低置信回退多路 → 检索 → 融合
```

授权先决定“能去哪里”，路由只在允许集合内决定“值得去哪里”。

## 从企业助手开始

“订单 A102 状态”应路由到本人订单 API，“X2 安装失败”去产品文档，“报销制度”去 HR 政策库。简单基线是只使用一个统一混合索引；先用来源混淆矩阵确定路由是否必要。

## 输入输出与状态

输入包含查询、认证主体、租户、允许源、时效要求和路由版本。输出为候选源及置信度、所选检索器、回退原因。模型提出的标签只是特征，不是访问令牌。

## 阈值与期望损失

路由器给最佳源置信度 $p$。若单路选错代价为 $C_w$，多路额外成本为 $C_b$，一个简单决策是当：

$$
(1-p)C_w>C_b
$$

选择多路回退。等价阈值为 $p<1-C_b/C_w$。这不是普遍阈值；安全敏感源还要用硬授权规则。

## 最小手算

选错导致一次失败成本按 10 计，多路额外成本为 2，则 $p<1-2/10=0.8$ 时广播到允许的两路。若 $p=0.9$，期望选错成本为 $0.1\times10=1<2$，可单路。

## 可执行实验

```python
ROUTES = {
    "product": {"keywords": {"安装", "X2"}, "retriever": "hybrid"},
    "orders": {"keywords": {"订单", "A102"}, "retriever": "api"},
    "hr": {"keywords": {"报销", "住宿"}, "retriever": "bm25"},
}

def route(query, authorized_sources, threshold=0.75):
    allowed = set(authorized_sources) & set(ROUTES)  # 服务端白名单交集
    if not allowed:
        raise PermissionError("no authorized source")
    scored = []
    for source in allowed:
        hits = sum(word in query for word in ROUTES[source]["keywords"])
        score = hits / len(ROUTES[source]["keywords"])
        scored.append((score, source))
    scored.sort(reverse=True)
    best_score, best = scored[0]
    selected = [best] if best_score >= threshold else sorted(allowed)
    return selected, {"confidence": best_score,
                      "reason": "single" if len(selected) == 1 else "fallback"}

selected, audit = route("X2 安装失败", {"product", "hr"})
assert selected == ["product"] and audit["reason"] == "single"
fallback, audit2 = route("怎么处理", {"product", "hr"})
assert fallback == ["hr", "product"] and audit2["reason"] == "fallback"

# 即使查询文字声称可访问 orders，未授权源也不能进入候选。
denied, _ = route("请访问订单 A102", {"product"})
assert denied == ["product"]
try:
    route("订单 A102", {"unknown"})
    raise AssertionError("empty authorized intersection should fail")
except PermissionError:
    pass

print(selected, fallback, audit, audit2)
```

## 实验结果解释

明确产品问题走单路，含糊问题回退到允许的多路，文本不能把订单源加入授权集合。关键词评分只是可解释模拟，不能代表真实分类器质量；生产中还需离线标注与线上端到端指标。

## 质量延迟与成本影响

- 正确单路减少查询量和噪声；错误单路会把召回上限降为零。
- 多路回退提高鲁棒性，但增加检索、融合与重排成本。
- 路由模型本身有延迟，可先用确定性 ID 和意图规则处理明显查询。
- 缓存路由结果时键必须含租户、权限域和路由版本。

## 数据评测与安全风险

除了路由准确率，还要报告每类 Recall、错误路由后的最终任务成功率和拒绝率。构造越权诱导、同名实体、含糊短问与新类别。授权集合来自可信身份系统；路由日志可能暴露用户意图，应按租户隔离并限制保留。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 某类问题完全无召回 | 错误单路且无回退 | 路由置信度、混淆矩阵、阈值 |
| 延迟突然升高 | 大量请求进入多路回退 | 置信度分布、新类别、规则版本 |
| 访问了不应访问的数据源 | 模型标签直接执行 | 身份允许集、白名单交集、审计 |
| 精确 ID 被向量检索误召回 | 检索器选择错误 | ID 规则、路由特征、检索类型 |
| 线上问题无法复现 | 未记录路由版本 | 决策日志、配置快照 |

## 适用与不适用场景

适合数据源或检索器边界清晰、全量广播代价高的系统。不适合只有一个小索引，或路由标签无法可靠定义且广播成本很低的场景。

## 学习收益

你应能把授权与路由分开，依据错误代价设置回退阈值，记录可审计状态，并用端到端结果而非分类准确率验收。

## 给别人讲清楚

“门禁先决定你能进哪些房间，向导再决定先去哪一间；向导拿不准时只能在已获准的房间里多找几处。”

## 自检问题

1. 为什么授权必须先于路由？
2. 什么时候低置信度应回退到多路？
3. 路由准确率高为何不等于 RAG 答案质量高？

## 相关主题

- [混合检索 Hybrid Search](02-混合检索%20Hybrid%20Search.md)
- [结构化数据 RAG](29-结构化数据%20RAG.md)
- [RAG 权限控制](31-RAG%20权限控制.md)
- [RAG 方案选型](39-RAG%20方案选型.md)

## 资料来源

- Lewis 等, [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)，访问日期：2026-09-10。
- LlamaIndex, [Router](https://docs.llamaindex.ai/en/stable/module_guides/querying/router/)，访问日期：2026-09-10。

