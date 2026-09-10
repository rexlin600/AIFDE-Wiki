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
  - 检索智能体
tags:
  - agentic-rag
  - tool-loop
---

# Agentic RAG

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

复杂研究任务可能要选择数据源、执行检索工具、观察结果后修改计划。例如运维助手先查服务手册，再根据版本号查变更记录。Agentic RAG 将这些动作组织成受控工具循环，重点仍是获得证据，不覆盖通用 Agent 的记忆和任务执行。

不理解边界会让模型自行访问未授权源、无限试错或把文档中的指令当工具命令。先使用静态检索或预定义查询分解；只有工具选择确实随观察变化时才采用 Agentic RAG。

## 链路位置与状态机

链路是 `计划 → 请求工具 → 参数校验和授权 → 执行 → 观察 → 停止或再计划`。状态：

$$
s_t=(g,h_t,E_t,c_t,b_t,r_t)
$$

$g$ 是不变目标，$h_t$ 是动作历史，$E_t$ 是证据，$c_t$ 是累计成本，$b_t$ 是剩余步数，$r_t$ 是终止原因。只有控制器能执行工具；模型只提出结构化动作。

若每步最多一次工具调用、最大步数 $m$，则调用数 $Q\le m$。再设成本上限 $C$、截止时间 $T$，任一达到就停止。正常终止包括 `supported`、`no_progress`、`max_steps`、`cost_limit`、`timeout` 和 `denied`。

## 最小手算

最多 3 步、预算 6 单位。查手册成本 2，查变更记录成本 3；两步共 5，证据齐全后以 `supported` 停止，不能为“也许还有信息”使用剩余 1。若模型请求成本 4 的外网搜索，预算不足且不在白名单，应以 `denied` 停止。

## 可执行实验

```python
TOOLS = {
    "manual": {"cost": 2, "duration": 1, "result": "服务 S 使用版本 v2"},
    "changes": {"cost": 3, "duration": 2, "result": "v2 修复了重试缺陷"},
}

def run_agent(plan, allowed, max_steps=3, cost_limit=6, time_limit=10):
    evidence, spent, elapsed = [], 0, 0
    for step, tool in enumerate(plan, start=1):
        if step > max_steps:
            return evidence, spent, elapsed, "max_steps"
        if tool not in allowed or tool not in TOOLS:
            return evidence, spent, elapsed, "denied"
        if spent + TOOLS[tool]["cost"] > cost_limit:
            return evidence, spent, elapsed, "cost_limit"
        if elapsed + TOOLS[tool]["duration"] > time_limit:
            return evidence, spent, elapsed, "timeout"
        result = TOOLS[tool]["result"]
        if result in evidence:
            return evidence, spent, elapsed, "no_progress"
        evidence.append(result)
        spent += TOOLS[tool]["cost"]
        elapsed += TOOLS[tool]["duration"]
        if any("修复" in item for item in evidence):
            return evidence, spent, elapsed, "supported"
    return evidence, spent, elapsed, "plan_exhausted"

ev, cost, elapsed, reason = run_agent(["manual", "changes"], set(TOOLS))
assert reason == "supported" and cost == 5 and elapsed == 3
assert run_agent(["web"], set(TOOLS))[3] == "denied"
assert run_agent(["manual", "manual"], set(TOOLS))[3] == "no_progress"
assert run_agent(["manual", "changes"], set(TOOLS), cost_limit=4)[3] == "cost_limit"
assert run_agent(["manual", "changes"], set(TOOLS), time_limit=1)[3] == "timeout"
print(reason, cost, elapsed, ev)
```

实验验证授权、费用、时间、无进展和终止状态，不证明固定计划具有智能，也不覆盖网络、重试和并发故障。真实截止时间应使用单调时钟，并把取消信号传给工具。

## 质量延迟成本与风险

Agentic RAG 可能找到静态流水线遗漏的路径，但串行工具调用增加尾延迟、费用和不可复现性。报告任务成功率、证据支持率、工具选择准确率、拒绝率、平均步数、终止原因、P95 延迟和成本，并与固定两步流程比较。

参数采用 Schema 校验，工具使用最小权限，读写工具隔离；RAG 循环通常只需只读检索。外部文档按数据处理，不能提升为指令。日志记录动作和来源 ID，凭据永不进入提示或模型输出。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 循环到预算耗尽 | 无进展检测缺失 | 重复动作与证据增量 |
| 调用了错误数据源 | 规划与授权混在一起 | 工具白名单和授权层 |
| 工具结果污染指令 | 未区分数据和控制 | 消息角色与参数 Schema |
| 尾延迟很高 | 串行步骤过多 | 步数分布与每工具耗时 |

## 适用边界与学习收益

适合检索路径依赖中间观察且任务价值覆盖额外成本的场景；固定知识库问答不适合。学完应能描述模型提议、控制器授权、工具执行三种权责，并证明调用上界。

复述：Agentic RAG 像研究员申请查档，模型可提议查哪里，但门禁决定能否查，预算决定还能查几次。

自检：为何模型不能直接执行工具？`no_progress` 怎样定义？Agentic RAG 与通用 Agent 的边界在哪里？

## 相关主题

- [RAG 迭代检索](<21-RAG 迭代检索.md>)
- [RAG 检索路由](<16-RAG 检索路由.md>)
- [智能体 Agent MOC](<../L-智能体 Agent/00-智能体 Agent-MOC.md>)

## 资料来源

- Shunyu Yao 等, [ReAct](https://arxiv.org/abs/2210.03629), 2022，访问日期：2026-09-10。
- Omar Khattab 等, [DSPy](https://arxiv.org/abs/2310.03714), 2023，访问日期：2026-09-10。
