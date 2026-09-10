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
  - Query Decomposition
tags:
  - decomposition
  - dependency-graph
---

# RAG 查询分解

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

复合问题常同时包含多个可独立核验的条件，单次检索难以让一段文档覆盖全部条件。查询分解把问题拆成较小子问题，显式记录依赖，再合并证据回答原问题。

## 不理解会造成什么错误

- 把“比较 A 与 B 的退款期”只拆出 A，漏掉 B。
- 依赖上一步实体的子问题提前执行，用占位符检索出噪声。
- 子答案互相矛盾却被强行拼成确定结论。
- 分解不断扩张，没有子问题数、Token 和时间上限。
- 子查询丢失用户、地区、时间或权限约束。

## 它在 RAG 链路中的位置

```text
原问题 → 分解计划 DAG → 就绪子问题 → 检索与证据
                           ↓
                    依赖结果代入 → 合成 → 完整性检查
```

若只需换一种措辞，使用[查询改写](13-RAG%20查询改写.md)；分解适用于原问题确有多个事实槽位或依赖。

## 从产品合规比较开始

问题：“比较 X2 和 Y3 在中国 2026 年保修期，并指出哪个更长。”至少需要分别查 X2 和 Y3 的中国有效政策，然后做确定性比较。简单基线是原问题一次检索；先观察是否稳定漏掉其中一个实体。

## 输入输出与依赖状态

每个节点含 `id`、问题模板、依赖 ID、不可变约束、状态和证据来源。状态从 `PENDING` 进入 `READY`、`DONE`，缺证时进入 `FAILED`；下游不得把失败节点当事实。

依赖图必须是有向无环图。若有 $n$ 个子问题，每个最多检索 $k$ 条，则初始候选上界为 $n k$；这解释了为何必须限制规模。

## 完整性与合成

设原问题需要的事实槽位集合为 $F$，已被可靠证据填充的槽位为 $E$，完整率为：

$$
C=\frac{|F\cap E|}{|F|}
$$

对于必须全部满足的比较题，$C<1$ 时应说明缺失并停止比较，而不是猜测。节点 $v$ 仅在全部前驱完成时就绪：

$$
ready(v)\iff \forall u\in deps(v),\ state(u)=DONE
$$

## 最小手算

原问题需要 `{X2 保修期, Y3 保修期, 比较}` 三个槽位。只检索到 X2，则 $C=1/3$；两个期限都有后可确定比较，$C=3/3=1$。若单次检索 80 毫秒，两个独立查询并行的检索阶段约取较慢一路，而依赖查询至少需要两轮。

## 可执行实验

```python
def topological_order(tasks):
    done, order = set(), []
    while len(order) < len(tasks):
        ready = [name for name, task in tasks.items()
                 if name not in done and set(task["deps"]) <= done]
        if not ready:
            raise ValueError("cycle or missing dependency")
        for name in sorted(ready):
            done.add(name)
            order.append(name)
    return order

COMMON = {"region": "中国", "year": 2026, "scope": "tenant:acme"}
tasks = {
    "x2": {"query": "X2 中国 2026 保修期", "deps": [],
           "constraints": COMMON},
    "y3": {"query": "Y3 中国 2026 保修期", "deps": [],
           "constraints": COMMON},
    "compare": {"query": "比较 x2 与 y3 的月数", "deps": ["x2", "y3"],
                "constraints": COMMON},
}
order = topological_order(tasks)
assert set(order[:2]) == {"x2", "y3"} and order[-1] == "compare"
assert all(task["constraints"] == COMMON for task in tasks.values())

evidence = {"x2": {"months": 24, "source": "doc-x2"},
            "y3": {"months": 12, "source": "doc-y3"}}
assert set(evidence) == {"x2", "y3"}

def execute(task_plan, facts):
    states = {name: "PENDING" for name in task_plan}
    for name in topological_order(task_plan):
        dependencies = task_plan[name]["deps"]
        if any(states[dep] != "DONE" for dep in dependencies):
            states[name] = "FAILED"
            continue
        states[name] = "READY"
        if name in ("x2", "y3"):
            states[name] = "DONE" if name in facts else "FAILED"
        else:
            states[name] = "DONE"  # 只有两个依赖均完成才允许合成。
    return states

states = execute(tasks, evidence)
assert states == {"x2": "DONE", "y3": "DONE", "compare": "DONE"}
answer = ("X2" if evidence["x2"]["months"] > evidence["y3"]["months"]
          else "Y3")
assert answer == "X2"

incomplete_states = execute(tasks, {"x2": evidence["x2"]})
assert incomplete_states == {"x2": "DONE", "y3": "FAILED",
                             "compare": "FAILED"}

try:
    topological_order({"a": {"deps": ["b"]}, "b": {"deps": ["a"]}})
    raise AssertionError("cyclic plan should fail")
except ValueError:
    pass

print(order, states, answer, evidence)
```

## 实验结果解释

实验让节点经历 `PENDING → READY → DONE/FAILED`，检查每个节点继承地区、年份和租户约束；只有两项证据齐全才比较，失败节点不会进入合成，并拒绝循环计划。它使用人工事实，不验证模型能正确分解自然语言，也没有处理证据冲突。

## 质量延迟与成本影响

- 分解可提高复杂问题的证据覆盖，也会成倍增加检索与重排调用。
- 无依赖节点可并行；有依赖节点决定最短轮数。
- 子问题过细会失去全局语义，过粗则仍难检索。
- 预算需同时限制节点数、每节点候选、总 Token 和总时限。

## 数据评测与安全风险

分别评测分解完整率、依赖正确率、子问题召回、证据合成和最终答案。所有节点继承原身份、租户、地区和时间约束；中间实体是不可信数据，不能借它扩大数据源。日志保存节点与来源链，但对敏感实体最小化记录。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 答案漏比较对象 | 分解不完整 | 原问题槽位、节点列表、完整率 |
| 子查询含未替换占位符 | 依赖提前执行 | DAG、节点状态、拓扑顺序 |
| 查询数量失控 | 递归分解无预算 | 最大节点数、深度、总时限 |
| 证据齐全但合成错误 | 单位或时间范围不一致 | 结构化结果、来源、比较代码 |
| 子问题越权 | 未继承原范围 | 身份上下文、源白名单、ACL |

## 适用与不适用场景

适合比较、汇总、多条件核验以及有明确依赖的复杂问题。不适合单事实 ID 查询、无法定义合成规则的开放式闲聊，或延迟预算只容许一次检索的请求。

## 学习收益

你应能把复合问题表示为依赖图，计算完整率，拒绝缺证合成，并估算节点数带来的调用上界。

## 给别人讲清楚

“先把大问题拆成一张有先后关系的清单，每项都带证据；清单没填完，就不能假装已经比较完。”

## 自检问题

1. 查询分解与查询改写的根本差异是什么？
2. 为什么缺少一个比较对象时必须停止？
3. 哪些子问题可以并行？

## 相关主题

- [RAG 多跳检索](19-RAG%20多跳检索.md)
- [RAG 迭代检索](21-RAG%20迭代检索.md)
- [RAG 检索路由](16-RAG%20检索路由.md)
- [RAG 生成评测](38-RAG%20生成评测.md)

## 资料来源

- Press 等, [Measuring and Narrowing the Compositionality Gap in Language Models](https://aclanthology.org/2023.findings-emnlp.378/)，访问日期：2026-09-10。
- Zhou 等, [Least-to-Most Prompting Enables Complex Reasoning in Large Language Models](https://arxiv.org/abs/2205.10625)，访问日期：2026-09-10。
