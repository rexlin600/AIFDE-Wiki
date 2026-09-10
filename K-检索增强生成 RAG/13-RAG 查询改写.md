---
type: concept
domain:
  - RAG
depth: L2
importance: common
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Query Rewriting
tags:
  - query-understanding
  - intent-preservation
---

# RAG 查询改写

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

用户语言和文档语言往往不同：用户说“钱怎么还没到”，知识库写“退款到账周期”。查询改写把口语、缩写或含糊表达转换为更适合检索的表达，同时必须保留实体、否定、时间、权限范围和用户真正意图。

## 不理解会造成什么错误

- 把“不要取消订单 A102”改写成“取消订单”，丢失否定。
- 把产品 X2 改成更常见的 X1，召回看似相关却答错实体。
- 将“我的工资单”扩展为“公司工资单”，越过本人权限范围。
- 为提高关键词覆盖加入不存在的条件，发生查询漂移。
- 只看检索命中率，不评估改写后答案是否仍回应原问题。

## 它在 RAG 链路中的位置

```text
原始查询 q → 提取不可变约束 → 生成候选 q' → 约束校验
→ 检索 → 用原始问题生成答案
                └→ 校验失败时回退 q
```

改写只服务检索，原始问题和约束必须保留到生成与审计阶段。

## 从售后知识库开始

用户问“X2 昨天申请的退款怎么还没到？”可改为“产品 X2 昨天申请的退款到账进度”。其中 `X2`、退款意图和时间条件不可丢失。简单基线是直接用原查询检索；只有固定失败集证明术语不匹配时才引入改写。

## 输入输出与约束状态

输入状态可表示为：

```text
原文 + 实体集合 + 否定词 + 时间条件 + 权限范围 + 语言
```

输出包含 `rewritten_query`、保留检查结果、改写版本和失败原因。不要只保存一条不可解释的字符串。

## 意图保持怎样量化

设必须保留的约束集合为 $C(q)$，改写中仍可识别的集合为 $C(q')$。约束保持率为：

$$
P_c=\frac{|C(q)\cap C(q')|}{|C(q)|}
$$

高风险场景通常要求 $P_c=1$，因为 0.9 可能恰好丢失唯一否定词。整体评测还需比较原查询和改写查询的检索指标：

$$
\Delta R@k=R@k(q')-R@k(q)
$$

只有约束通过且 $\Delta R@k$ 在代表性数据上改善，改写才有价值。

## 最小手算

原查询约束为 `{X2, 退款, 昨天, 我的}`，共 4 个。改写保留 `{X2, 退款, 我的}`，保持率为 $3/4=0.75$。即使 Recall@5 从 0.6 升到 0.8，丢失“昨天”仍可能返回旧政策，不能直接上线。

## 可执行实验

```python
import re

def constraints(text):
    entities = set(re.findall(r"\b[A-Z]\d+\b", text))
    flags = {word for word in ["不", "不要", "未", "昨天", "我的"]
             if word in text}
    intents = {word for word in ["退款", "取消", "订单", "进度"]
               if word in text}
    return entities | flags | intents

def safe_rewrite(original, candidate):
    required = constraints(original)
    kept = constraints(candidate)
    missing = required - kept
    if missing:
        return original, {"accepted": False, "missing": sorted(missing)}
    return candidate, {"accepted": True, "missing": []}

original = "不要取消我的 X2 订单，查询昨天的退款进度"
good = "查询我的 X2 订单昨天的退款进度，不要取消订单"
bad = "取消 X1 订单并查询退款"

rewritten, audit = safe_rewrite(original, good)
assert audit["accepted"] and rewritten == good
fallback, rejected = safe_rewrite(original, bad)
assert not rejected["accepted"]
assert fallback == original
assert {"X2", "不要", "我的", "昨天", "进度"}.issubset(
    set(rejected["missing"]))
drift, drift_audit = safe_rewrite(original, "不要吃我的 X2，昨天")
assert drift == original and "退款" in drift_audit["missing"]

# 改写不授予新权限；权限过滤仍使用认证身份，而不是查询文字。
actor_scope = {"owner:u1"}
assert "company:all" not in actor_scope
print(audit, rejected)
```

## 实验结果解释

正常候选完整保留约束；错误候选丢实体、否定、时间和所有权后被拒绝并回退原查询。词表规则只是最小护栏，不能理解复杂否定作用域、同义实体或隐含时间，生产中需结构化抽取、回归集与人工审查。

## 质量延迟与成本影响

- 一次模型改写增加生成延迟、Token 成本和新故障点，可对高频稳定查询缓存。
- 改写可能提高 Recall，却降低 Precision；同时观察检索和最终答案指标。
- 规则规范化便宜稳定，模型改写覆盖复杂表达但更难控制。
- 校验失败应回退原查询，不要无限重写。

## 数据评测与安全风险

测试集要覆盖实体相近、双重否定、时间、数字、语言混合和权限词。用户输入可能诱导改写器泄露系统提示或访问其他数据源；数据源授权由服务端身份决定，绝不能从改写文本推断。保存原文、候选、约束差异和版本，但对个人信息做脱敏与限期保留。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 召回更多但答非所问 | 查询漂移 | 原文与改写、实体和意图差异 |
| 否定问题返回正向操作 | 否定词或作用域丢失 | 约束抽取、失败回退 |
| 新型号被旧型号替换 | 实体规范化错误 | 实体字典版本、候选日志 |
| 改写延迟波动 | 额外模型调用 | P95、缓存命中、超时回退 |
| 出现越权结果 | 把文本当授权 | 认证身份、检索前 ACL 过滤 |

## 适用与不适用场景

适合用户语言与文档术语有稳定差异、缩写或口语较多的知识库。不适合原查询已经精确、强实时低延迟，或无法可靠保留法律和交易约束的高风险请求。

## 学习收益

你应能区分“更像文档”与“仍是同一问题”，抽取不可变约束，设计校验和回退，并联合评价 Recall 与意图保持。

## 给别人讲清楚

“查询改写像把口语翻译成知识库用语，但姓名、型号、否定、时间和门禁卡都不能翻丢。”

## 自检问题

1. 为什么 Recall 提升不能证明改写正确？
2. 哪些字段应作为不可变约束？
3. 校验失败后为什么优先回退而不是不断重写？

## 相关主题

- [RAG 多查询检索](14-RAG%20多查询检索.md)
- [多轮对话检索](18-多轮对话检索.md)
- [RAG 权限控制](31-RAG%20权限控制.md)
- [大模型提示设计](../J-大模型%20LLM/05-大模型提示设计.md)

## 资料来源

- Ma 等, [Query Rewriting for Retrieval-Augmented Large Language Models](https://aclanthology.org/2023.emnlp-main.322/)，访问日期：2026-09-10。
- OWASP, [Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)，访问日期：2026-09-10。
