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
  - RAG 技术决策
tags:
  - architecture-decision
  - evaluation
---

# RAG 方案选型

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

RAG 方案选型决定某个 AI 应用应该使用直接生成、长上下文、检索、工具、微调，还是有限组合。目标是用最简单、可验证的系统满足知识时效、引用、权限、质量、延迟和成本要求，而不是堆叠最多技术名词。

## 不理解会造成什么错误

- 为静态小文档建设复杂向量平台，本可直接放入上下文。
- 用微调记忆每天变化的价格和政策。
- 用 RAG 回答实时库存，本应调用权威工具。
- 基础召回没测好就增加 GraphRAG 或 Agentic RAG。
- 只比较答案质量，不算更新、索引、延迟和安全成本。

## 它在 RAG 链路中的位置

选型发生在需求定义和错误代价明确之后，也在每轮错误分析之后重新发生。先建立无检索、关键词检索或固定上下文基线，再按失败类型添加组件，并用消融证明每个组件有净收益。

## 五种主要手段

- Prompt：改变当次行为，不提供缺失事实，也不是权限边界。
- 长上下文：材料规模可控且单次相关时直接输入，简单但可能有位置与噪声问题。
- RAG：知识量大、动态、需要权限和引用时按查询选择证据。
- 工具：实时状态、精确计算和动作由权威系统执行。
- 微调：学习稳定格式、语气和行为模式，不适合频繁变化的事实。

## 先检查硬约束

隐私、数据驻留、许可证、最大延迟、必须引用和必须实时等条件是淘汰门槛。不能让高质量分抵消越权或不合规。通过门槛后，再比较质量收益与总成本。

## 加权决策

把候选在质量、延迟、成本、可更新、可引用等维度归一化为收益 $z_{ij}\in[0,1]$：

$$
S_j=\sum_iw_iz_{ij},\qquad \sum_iw_i=1
$$

总分依赖权重，必须做敏感性分析。还要展示原始指标，不能只给分数。

## 最小手算

RAG 的质量、时效、成本收益为 `[0.8,0.9,0.5]`，长上下文为 `[0.75,0.4,0.8]`。权重 `[0.5,0.3,0.2]` 时，RAG 得 0.77，长上下文得 0.655。若任务完全静态而成本权重上升，排序可能反转。

## 可执行实验

```python
candidates = {
    "rag": {"quality": 0.80, "freshness": 0.90, "cost": 0.50,
            "can_update": True, "can_cite": True, "private": True},
    "long_context": {"quality": 0.75, "freshness": 0.40, "cost": 0.80,
                     "can_update": False, "can_cite": True, "private": True},
}

def choose(weights, required=None):
    required = required or {}
    eligible = {
        name: values for name, values in candidates.items()
        if all(values.get(key) == value for key, value in required.items())
    }
    if not eligible:
        raise ValueError("no_candidate_meets_hard_constraints")
    scores = {name: sum(weights[key] * values[key] for key in weights)
              for name, values in eligible.items()}
    return max(scores, key=scores.get), scores

dynamic = choose({"quality": 0.5, "freshness": 0.3, "cost": 0.2},
                 required={"can_update": True, "can_cite": True})
static = choose({"quality": 0.3, "freshness": 0.1, "cost": 0.6})
print("dynamic", dynamic, "static", static)
assert dynamic[0] == "rag"
assert static[0] == "long_context"

# 同一固定评测分别运行完整系统与移除 Rerank 的系统。
runs = {
    "full": {"quality": 0.86, "latency_ms": 120, "cost": 0.018},
    "without_rerank": {"quality": 0.83, "latency_ms": 90, "cost": 0.014},
}
quality_delta = runs["full"]["quality"] - runs["without_rerank"]["quality"]
latency_delta = runs["full"]["latency_ms"] - runs["without_rerank"]["latency_ms"]
assert quality_delta > 0
assert latency_delta > 0
assert runs["full"]["quality"] >= 0.85  # 预先声明的质量门槛

try:
    choose({"quality": 1.0}, required={"private": False})
except ValueError as error:
    assert str(error) == "no_candidate_meets_hard_constraints"
else:
    raise AssertionError("硬约束不合格的候选不得进入加权")
```

实验先按可更新、可引用和私有部署等硬条件淘汰候选，再说明权重变化可改变结论。消融把完整系统与移除 Rerank 视为两次独立观测，展示 0.03 质量提升伴随 30 ms 延迟增加，不假设各组件收益可加。示例数值不代表真实模型，生产分数必须来自固定数据、负载和费用证据。

## 根据错误选择组件

| 观察到的错误 | 优先尝试 | 先不要做 |
| --- | --- | --- |
| 精确编号搜不到 | BM25 或 Hybrid | GraphRAG |
| 语义改写搜不到 | Dense 与困难负例评测 | 增大生成模型 |
| 相关文档已召回但排后 | Rerank | 重做全部索引 |
| 文档太碎缺上下文 | 父子文档与上下文构建 | 无限制增大 k |
| 实时数值错误 | 权威工具或结构化查询 | SFT 记忆数值 |
| 跨文档关系推理失败 | 分解、多跳，再评估图方法 | 直接上 Agentic RAG |
| 输出格式不稳定 | 结构化输出或 SFT | 增加检索复杂度 |

## 消融怎样证明价值

固定数据和配置，逐一移除 Dense、BM25、Rerank、查询改写或高级循环，比较检索、生成、延迟和成本。若组件提升总体均值却伤害关键切片，不能只凭总分保留。高级方法还要与“多取几个候选”这种简单基线比较。

## 质量延迟与成本影响

总成本包括摄取、Embedding、索引存储、查询、重排、上下文 Token、生成、更新、评测与值班。P50 之外看 P95/P99；一次检索之外看重复查询、缓存和重试。组合方案每加一层都会增加故障状态和观测要求。

## 数据评测与安全风险

选型评测覆盖真实权限、时效、不可回答、删除、提示注入和数据驻留。供应商模型与 Embedding 升级会改变结果，应锁定版本。采用高级方法前形成决策记录：问题、基线、证据、风险、回滚条件和负责人。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 组件越来越多但质量不升 | 没有错误归因和消融 | 基线、逐层 Trace、切片 |
| 离线方案好线上很慢 | 负载和长度分布错配 | TTFT、P95、候选和 Token 数 |
| 成本估算持续偏低 | 漏算更新、重试和闲置 | 端到端账单、利用率 |
| 排名随权重变化 | 候选各有取舍 | 硬门槛、敏感性、业务代价 |
| 新方案不能回退 | 索引或协议不兼容 | 版本、影子索引、回滚演练 |

## 适用与不适用场景

所有新建、升级或成本治理项目都应做方案选型。早期原型可用少量代表样本快速排除方案，但不能替代上线评测。需求未定义时，没有稳定的“最佳 RAG 架构”。

## 学习收益

你应能区分五类手段，先应用硬约束，再做加权和敏感性分析，根据失败选择组件，并用消融证明净收益。

## 给别人讲清楚

“RAG 不是默认答案。先问知识会不会变、要不要引用、是否实时、材料有多大，再从最简单基线出发；只有明确错误需要时才加复杂组件。”

## 自检问题

1. 为什么实时库存更适合工具而不是文档 RAG？
2. 硬约束与加权指标有什么区别？
3. GraphRAG 上线前应与哪些简单基线比较？

## 相关主题

- [RAG 检索评测](37-RAG 检索评测.md)
- [RAG 生成评测](38-RAG 生成评测.md)
- [Agentic RAG](<24-Agentic RAG.md>)

## 资料来源

- Patrick Lewis 等, [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401), 2020，访问日期：2026-09-10。
- Nelson F. Liu 等, [Lost in the Middle](https://arxiv.org/abs/2307.03172), 2023，访问日期：2026-09-10。
- Percy Liang 等, [Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110), 2022，访问日期：2026-09-10。
