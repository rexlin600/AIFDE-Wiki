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
  - 表格数据检索增强
tags:
  - structured-data
  - text-to-sql
---

# 结构化数据 RAG

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

企业问题常同时需要文档解释和数据库中的实时数值。例如“华东区本月退款额为什么上升”，退款额来自受权限控制的订单表，原因可能来自政策、工单和运营记录。结构化数据 RAG 把自然语言问题转换为受控查询，取得可追踪结果，再交给模型解释。

## 不理解会造成什么错误

- 把整张表序列化进 Prompt，既昂贵又容易过期。
- 让模型直接执行任意 SQL，造成越权、写入或资源耗尽。
- 查询语法正确就认为答案正确，忽略连接键和时间口径。
- 把空结果解释成数值为零。
- 只引用数据库名，不保留查询、参数和快照时间。

## 它在 RAG 链路中的位置

自然语言问题先映射为允许的数据源、字段、过滤条件和聚合，再由确定性程序校验和执行只读查询。结果以小型表格和来源元数据进入上下文，模型负责解释，不负责授权和事务提交。

## 简单基线

若只有固定的十个业务问题，参数化报表 API 通常比 Text-to-SQL 更可靠。只有查询组合多、用户表达变化大且 Schema 可治理时，才需要模型生成查询计划。

## 查询计划比 SQL 字符串更容易控制

先让模型提出结构化计划：

```text
数据集：orders
指标：sum(refund_amount)
过滤：region = 华东，month = 2026-09
分组：reason
```

程序检查数据集、字段、操作符、行级权限和扫描预算，再编译为参数化 SQL。模型输出是提议，数据库驱动负责转义，授权层负责限制可见行。

## 聚合口径推导

若过滤后的记录集合为 $R$，退款总额为：

$$
S=\sum_{r\in R}r.\text{refund\_amount}
$$

占比不是各行百分比的平均，而是：

$$
p_j=\frac{\sum_{r\in R_j}r.\text{refund\_amount}}{S}
$$

连接一对多明细表可能重复订单金额。先按业务主键聚合，或明确指标粒度，才能避免重复计数。

## 最小手算

三笔退款为 `(订单 A, 100, 延迟)`、`(订单 B, 50, 延迟)`、`(订单 C, 50, 质量)`。总额 200，延迟占比为 $(100+50)/200=75\%$。若订单 A 有两条标签记录，直接连接后求和可能把 100 计算两次，错误得到 300。

## 可执行实验

```python
ROWS = [
    {"tenant": "acme", "region": "east", "amount": 100},
    {"tenant": "acme", "region": "east", "amount": 50},
    {"tenant": "beta", "region": "east", "amount": 900},
]
ALLOWED_METRICS = {"sum_amount", "count"}

def execute_plan(plan, current_tenant):
    if plan.get("dataset") != "orders":
        raise ValueError("dataset_not_allowed")
    if plan.get("metric") not in ALLOWED_METRICS:
        raise ValueError("metric_not_allowed")
    if set(plan.get("filters", {})) - {"region"}:
        raise ValueError("filter_not_allowed")
    visible = [row for row in ROWS if row["tenant"] == current_tenant]
    for key, value in plan.get("filters", {}).items():
        visible = [row for row in visible if row[key] == value]
    if plan["metric"] == "sum_amount":
        return sum(row["amount"] for row in visible)
    return len(visible)

safe = {"dataset": "orders", "metric": "sum_amount",
        "filters": {"region": "east"}}
assert execute_plan(safe, "acme") == 150
try:
    execute_plan({"dataset": "orders", "metric": "delete",
                  "filters": {}}, "acme")
except ValueError as error:
    assert str(error) == "metric_not_allowed"
else:
    raise AssertionError("危险操作应被拒绝")
```

实验验证白名单和租户过滤，不能证明模型能生成正确 SQL。生产系统还需数据库权限、超时、扫描上限和审计日志。

## 结果怎样进入上下文

返回数据应包含列名、单位、过滤条件、时区、快照时间、查询 ID 和有限行数。模型回答中的数值引用查询结果 ID；文档原因引用文档 Chunk ID。这样可以分别核验“数字从哪里来”和“解释依据是什么”。

## 质量延迟与成本影响

复杂查询、全表扫描和大结果集会拉高数据库与 Prompt 成本。限制行数、预聚合、缓存只读结果和按问题路由到固定指标 API，通常比无限制 Text-to-SQL 稳定。缓存键必须包含租户、权限、参数和数据版本。

## 数据评测与安全风险

测试集应覆盖同义表达、时间边界、空值、连接、多租户、不可回答和危险操作。执行账户只授予必要的只读视图；敏感列不应仅靠 Prompt 隐藏。记录生成计划、校验结果、参数化查询摘要、快照时间和返回行数，日志本身也要脱敏。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 数字被重复计算 | 一对多连接改变粒度 | 主键、连接基数、聚合前去重 |
| 查询成功但口径错误 | 时间或指标定义歧义 | 时区、自然月、指标目录 |
| 空结果被回答为零 | 无数据与零值混淆 | 行数、NULL、拒答规则 |
| 返回其他租户数据 | 权限只写在 Prompt | 行级策略、执行身份、缓存键 |
| 数据库延迟升高 | 扫描过大或查询失控 | EXPLAIN、超时、行数和扫描上限 |

## 适用与不适用场景

适合实时指标、库存、订单和其他结构化事实。不适合让模型绕过业务 API 执行写操作；动作应走工具调用和独立授权。固定报表能覆盖时，优先使用更简单的参数化接口。

## 学习收益

你应能区分查询计划、授权、执行和解释，识别连接粒度错误，设计只读白名单，并让数值回答可追溯。

## 给别人讲清楚

“结构化 RAG 不是让模型拿到数据库钥匙，而是让它填写受控查询单。程序检查权限并取回小表格，模型只根据结果解释。”

## 自检问题

1. 为什么语法正确的 SQL 仍可能给出错误业务数字？
2. 缓存键为什么必须包含租户和数据版本？
3. 什么情况下固定指标 API 优于 Text-to-SQL？

## 相关主题

- [RAG 检索路由](16-RAG 检索路由.md)
- [RAG 权限控制](31-RAG 权限控制.md)
- [RAG 引用生成](36-RAG 引用生成.md)

## 资料来源

- Tao Yu 等, [Spider](https://aclanthology.org/D18-1425/), 2018，访问日期：2026-09-10。
- NIST, [Attribute Based Access Control](https://csrc.nist.gov/publications/detail/sp/800-162/upd-2/final)，访问日期：2026-09-10。
- SQLite, [Query Language](https://www.sqlite.org/lang.html)，访问日期：2026-09-10。

