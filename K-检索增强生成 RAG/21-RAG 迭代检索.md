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
  - Iterative Retrieval
tags:
  - iterative-retrieval
  - state-machine
---

# RAG 迭代检索

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

有些答案必须从上一批证据中发现新实体后再查。例如研发助手先从项目说明找到依赖库，再查该库的兼容版本。单轮检索看不到第二跳查询，迭代检索便根据中间结果更新查询。

不了解状态和终止条件会造成重复检索、查询漂移、证据来源丢失和成本失控。先用一次检索做基线；只有它在多跳问题上稳定缺证，才引入循环。

## 链路位置与状态

链路为 `初始查询 → 检索 → 观察缺口 → 构造下一查询 → 检索 → 停止`。状态可写成：

$$
s_t=(q_0,q_t,E_t,t,b,r)
$$

$q_0$ 是原问题，$q_t$ 是本轮查询，$E_t$ 是带来源的累计证据，$t$ 是步数，$b$ 是剩余查询预算，$r$ 是终止原因。状态转移为 $s_{t+1}=F(s_t,R(q_t))$。

每轮必须按顺序检查：答案是否已被支持、是否出现新信息、预算是否耗尽、是否超时。若最大步数为 $m$、每轮最多取 $k$ 条，候选处理量上界为 $mk$；串行检索延迟上界约为 $m(L_r+L_j)$，其中 $L_j$ 是缺口判断耗时。

## 最小手算

问题是“项目 A 使用的数据库要求哪个 Python 版本？”第一轮用 `项目 A 数据库` 找到“使用 DB-X”；第二轮用 `DB-X Python 版本` 找到“要求 3.11”。若 $m=3$，第二轮已支持答案，实际查询 2 次，终止原因为 `supported`，剩余预算 1。

## 可执行实验

```python
INDEX = {
    "项目 A 数据库": ["项目 A 使用 DB-X"],
    "DB-X Python 版本": ["DB-X 要求 Python 3.11"],
}
START_QUERIES = {
    "项目 A 的数据库要求什么 Python 版本？": "项目 A 数据库",
}

def iterative(question, max_steps=3):
    query, evidence, seen = START_QUERIES.get(question, question), [], set()
    for step in range(1, max_steps + 1):
        if query in seen:
            return evidence, "repeated_query", step - 1
        seen.add(query)
        docs = INDEX.get(query, [])
        evidence.extend(d for d in docs if d not in evidence)
        if any("Python 3.11" in d for d in evidence):
            return evidence, "supported", step
        if any("DB-X" in d for d in docs):
            query = "DB-X Python 版本"
        elif not docs:
            return evidence, "no_new_evidence", step
    return evidence, "max_steps", max_steps

evidence, reason, steps = iterative("项目 A 的数据库要求什么 Python 版本？")
assert reason == "supported" and steps == 2
assert evidence[-1] == "DB-X 要求 Python 3.11"
assert iterative("未知项目", max_steps=1)[1] == "no_new_evidence"
assert iterative("项目 A 的数据库要求什么 Python 版本？",
                 max_steps=1)[1] == "max_steps"
print(reason, steps, evidence)
```

实验验证初始问题映射、无结果、证据累积、最大步数和终止原因，不证明字符串规则可替代模型的缺口判断，也不证明检索材料真实。

## 质量延迟成本与风险

收益是补全跨文档证据链；代价是串行延迟、更多检索费用和错误累积。报告每步 Recall、证据链完整率、平均步数、各终止原因比例、P95 延迟及单答案成本，并与单轮基线做消融。

每轮只能访问当前用户获权的数据源，累计证据也要带权限和版本。中间文档是不可信数据，不能让其中的“继续查询私有库”改变授权。缓存键必须包含用户或租户边界。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 重复相同查询 | 未记录已见查询 | 查询轨迹与去重键 |
| 第二轮偏离原问题 | 只依据局部文档改写 | 原问题约束与实体变化 |
| 明明有证据仍循环 | 支持度判断失准 | 终止日志与主张证据映射 |
| 延迟超过上界 | 超时或最大步数未强制 | 状态机预算与调用计数 |

## 适用边界与学习收益

适合确需串行发现中间实体的多跳问题；若子查询可预先确定，应并行分解；单次检索足够时不应使用。学完应能画出状态、证明查询数上界并列出终止原因。

复述：迭代检索像查案，每轮依据新线索再查，但要保留原案目标、证据出处和查询次数上限。

自检：为什么“没有新证据”也是终止条件？如何区分答案支持与关键词命中？为什么累计证据要重新做权限判断？

## 相关主题

- [RAG 多跳检索](<19-RAG 多跳检索.md>)
- [RAG 纠错检索](<22-RAG 纠错检索.md>)
- [Agentic RAG](<24-Agentic RAG.md>)

## 资料来源

- Zhihong Shao 等, [Enhancing Retrieval-Augmented Large Language Models with Iterative Retrieval-Generation Synergy](https://arxiv.org/abs/2305.15294), 2023，访问日期：2026-09-10。
- Ofir Press 等, [Measuring and Narrowing the Compositionality Gap in Language Models](https://arxiv.org/abs/2210.03350), 2022，访问日期：2026-09-10。
