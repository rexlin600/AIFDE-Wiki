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
  - Multi Hop Retrieval
tags:
  - multi-hop
  - evidence-chain
---

# RAG 多跳检索

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

有些答案不存在于单篇文档中：第一份材料给出中间实体，第二份材料才给出目标事实。多跳检索逐步构建带来源的证据链，并在答案充分、缺证、重复或预算耗尽时停止。

## 不理解会造成什么错误

- 把两篇各自相关但互不连接的文档拼成答案。
- 中间实体由模型猜出，没有来源，却用于下一跳。
- 找不到证据时继续无限检索，延迟和费用失控。
- 同一实体循环出现，系统在 A 与 B 之间往返。
- 某一跳越权或过期，整条链仍被当作可信。

## 它在 RAG 链路中的位置

```text
问题 → 第 1 跳检索 → 提取有来源的中间实体
→ 第 2 跳检索 → 验证连接关系 → 证据充分则回答
       └→ 缺证 / 重复 / 最大跳数 / 超预算时停止
```

查询分解预先规划子问题；多跳检索强调后一步查询依赖前一步检索所得实体。

## 从产品责任人查询开始

用户问“生产 X2 的团队负责人是谁？”文档一说明“X2 由 Atlas 团队维护”，文档二说明“Atlas 团队负责人是林青”。简单基线是一次检索完整问题；若知识库确实没有同时包含两条关系的段落，才需要第二跳。

## 输入输出与状态机

状态至少包含当前查询、已访问实体、证据边、跳数、剩余预算和终止原因。状态转移为：

```text
SEARCH → EXTRACT → VERIFY → SEARCH
                   ├→ ANSWERABLE
                   ├→ NO_EVIDENCE
                   ├→ LOOP
                   └→ MAX_HOPS
```

中间实体必须绑定 `source_id` 和支持它的原文片段，不能只保存字符串。

## 证据链得分

若一条 $h$ 跳证据链各边支持度为 $p_1,\ldots,p_h$，在简化独立假设下，链支持度可写为：

$$
P_{chain}=\prod_{i=1}^{h}p_i
$$

乘积提醒我们：链越长，任一薄弱环节都拉低整体可信度。但真实边并不独立，分数也未必校准，不能把结果直接称为事实概率。

## 最小手算

第一条关系支持度 0.9，第二条为 0.8，则简化链分数为 $0.9\times0.8=0.72$。若第三跳再乘 0.7，只剩 0.504。设每跳最多 120 毫秒、最多 3 跳，纯检索最坏约 360 毫秒，还未含模型和重排。

## 可执行实验

```python
from dataclasses import dataclass, field

GRAPH = {
    "X2": [("mentions", "DeadEnd", "doc-noise", "public", 2),
           ("maintained_by", "Atlas", "doc-1", "public", 2),
           ("maintained_by", "Secret", "doc-secret", "restricted", 2)],
    "Atlas": [("led_by", "林青", "doc-2", "public", 2)],
    "CycleA": [("links_to", "CycleB", "doc-3", "public", 2)],
    "CycleB": [("links_to", "CycleA", "doc-4", "public", 2)],
}

@dataclass
class State:
    entity: str
    visited: set = field(default_factory=set)
    evidence: list = field(default_factory=list)
    remaining: int = 0
    reason: str = "SEARCH"

def walk(start, target_relation, max_hops=3, allowed={"public"}, version=2):
    frontier = [State(start, {start}, [], max_hops)]
    last = frontier[0]
    for _ in range(max_hops):
        following, saw_cycle, saw_edge = [], False, False
        for state in frontier:
            for relation, next_entity, source, acl, edge_version in GRAPH.get(
                    state.entity, []):
                if acl not in allowed or edge_version != version:
                    continue
                saw_edge = True
                if next_entity in state.visited:
                    saw_cycle = True
                    continue
                evidence = state.evidence + [{
                    "subject": state.entity, "relation": relation,
                    "object": next_entity, "source": source,
                    "acl": acl, "version": edge_version}]
                candidate = State(next_entity, state.visited | {next_entity},
                                  evidence, state.remaining - 1)
                if relation == target_relation:
                    candidate.reason = "ANSWERABLE"
                    return candidate
                following.append(candidate)
                last = candidate
        if not following:
            last.reason = "LOOP" if saw_cycle else "NO_EVIDENCE"
            return last
        frontier = following
    last = frontier[0]
    last.reason = "MAX_HOPS"
    return last

ok = walk("X2", "led_by", max_hops=3)
assert ok.reason == "ANSWERABLE" and ok.entity == "林青"
assert [edge["source"] for edge in ok.evidence] == ["doc-1", "doc-2"]
assert ok.remaining == 1
assert all(edge["acl"] == "public" and edge["version"] == 2
           for edge in ok.evidence)

missing = walk("Unknown", "led_by")
assert missing.reason == "NO_EVIDENCE" and missing.evidence == []
loop = walk("CycleA", "never", max_hops=5)
assert loop.reason == "LOOP" and len(loop.evidence) == 1
limited = walk("X2", "led_by", max_hops=1)
assert limited.reason == "MAX_HOPS"
print(ok.reason, ok.entity, missing.reason, loop.reason, limited.reason)
```

## 实验结果解释

实验以队列探索多条分支而不是固定取第一条边，用两份来源连接 X2 到负责人，同时验证每跳 ACL、版本、剩余预算，并触发缺证、循环和最大跳数终止。内存图把实体提取和关系验证都简化为人工边，不能证明真实文本检索能正确构图，也不能替代来源内容核验。

## 质量延迟与成本影响

- 多跳可回答跨文档关系问题，也会累积召回错误和生成错误。
- 延迟至少受依赖链长度限制，后跳通常无法与前跳并行。
- 限制最大跳数、每跳 top-k、总 Token、墙钟时间和允许源。
- 缓存中间结果需包含知识版本、权限域和有效期。

## 数据评测与安全风险

除最终答案外，逐跳评测中间实体、关系、来源和链完整性。测试无答案、同名实体、循环、冲突版本、越权边和恶意文档指令。任一跳无授权或证据不足，链必须停止；日志可审计但不能泄露未授权中间实体。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 答案关系拼错 | 文档相关但证据边不连接 | 每跳主客体、来源片段 |
| 循环检索不停止 | 未记录访问实体 | visited 集、终止原因 |
| 延迟偶发极高 | 无跳数或总预算 | max_hops、top-k、墙钟时间 |
| 中间实体不存在 | 模型猜测而非证据提取 | 实体来源 ID、原文跨度 |
| 最终答案越权 | 某跳未执行权限过滤 | 每跳 ACL、缓存权限域 |

## 适用与不适用场景

适合实体关系分散在多份文档、且证据链可明确验证的问题。不适合单事实检索、开放式联想，或无法追踪中间关系来源的场景。

## 学习收益

你应能表示逐跳状态与证据边，解释链分数为何随薄弱环节下降，并实现答案充分、缺证、循环和预算终止。

## 给别人讲清楚

“每一跳都像拿上一张有出处的线索去找下一张；线索断了、绕回原地或步数用完，就必须停。”

## 自检问题

1. 中间实体为什么必须带来源？
2. 多跳检索至少需要哪些终止原因？
3. 为什么更长证据链通常更脆弱？

## 相关主题

- [RAG 查询分解](15-RAG%20查询分解.md)
- [RAG 迭代检索](21-RAG%20迭代检索.md)
- [知识图谱 RAG](26-知识图谱%20RAG.md)
- [RAG 引用生成](36-RAG%20引用生成.md)

## 资料来源

- Yang 等, [HotpotQA](https://aclanthology.org/D18-1259/)，访问日期：2026-09-10。
- Trivedi 等, [Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions](https://aclanthology.org/2023.acl-long.557/)，访问日期：2026-09-10。
