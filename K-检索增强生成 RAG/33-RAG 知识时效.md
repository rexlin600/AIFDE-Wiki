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
  - RAG 时间感知检索
tags:
  - freshness
  - temporal-retrieval
---

# RAG 知识时效

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

政策、价格、组织和产品状态会变化。RAG 知识时效保证系统针对问题所指时间选择当时有效的证据，而不是简单偏爱最新文档。例如用户问“2025 年 3 月的报销上限”，答案可能必须引用已经失效的历史版本。

## 不理解会造成什么错误

- 只保留最新版，历史问题无法回答。
- 只按更新时间排序，把未来生效政策用于当前问题。
- 新旧冲突时让模型自行猜测哪个有效。
- 缓存不含时间与索引版本，持续返回旧答案。
- 数据源中断却仍显示“最新”。

## 它在 RAG 链路中的位置

摄取时记录事件时间、系统接收时间、生效区间和版本关系；查询理解提取目标时间；候选检索先应用权限，再按有效区间过滤；回答引用具体版本和“截至何时”。流式更新负责让索引追上源数据。

## 简单基线

知识很少且只需当前状态时，可覆盖旧版本并显示最后更新时间。只要存在历史追溯、预约生效、延迟到达或多源冲突，就需要显式时间模型。

## 四个时间字段

- `event_time`：事实在业务世界发生的时间。
- `ingested_at`：系统收到记录的时间。
- `valid_from`：该版本开始适用的时间。
- `valid_to`：该版本停止适用的时间，可为空表示尚未结束。

版本 $d$ 对查询时间 $t_q$ 有效的条件是：

$$
d.valid\_from\le t_q<d.valid\_to
$$

右端使用开区间可避免相邻版本在切换时同时有效。没有结束时间时可视为正无穷。

## 新鲜度与相关度

当前事实查询可以给陈旧度惩罚。若文档年龄为 $\Delta t$，指数衰减权重为：

$$
w_{time}=e^{-\lambda\Delta t},\qquad
s'=s_{relevance}w_{time}
$$

但时间权重不能替代有效期硬过滤；否则高相关但已失效政策仍可能排第一。历史查询也不应偏爱当前版本。

## 最小手算

旧政策有效区间 `[2025-01-01, 2026-01-01)`，新政策从 `2026-01-01` 起生效。查询 `2025-12-31` 只命中旧政策；查询 `2026-01-01` 只命中新政策。半开区间让边界没有重叠。

## 可执行实验

```python
from datetime import date

VERSIONS = [
    {"id": "policy-v1", "start": date(2025, 1, 1),
     "end": date(2026, 1, 1), "limit": 1000},
    {"id": "policy-v2", "start": date(2026, 1, 1),
     "end": None, "limit": 1500},
]

def valid_at(when):
    return [item for item in VERSIONS
            if item["start"] <= when
            and (item["end"] is None or when < item["end"])]

before = valid_at(date(2025, 12, 31))
boundary = valid_at(date(2026, 1, 1))
assert [item["id"] for item in before] == ["policy-v1"]
assert [item["id"] for item in boundary] == ["policy-v2"]
assert valid_at(date(2024, 12, 31)) == []
print(before, boundary)
```

实验验证有效区间边界，不能证明来源本身正确，也不能处理同一时间有两个冲突版本的业务裁决。

## 冲突和缺失怎样处理

为来源设置权威等级和明确的冲突规则，但不要悄悄覆盖。若同一资源在同一时间存在两个有效版本，进入冲突队列并拒绝确定性回答；若索引水位落后于服务等级目标，答案标示“数据更新至”或降级到实时工具。

## 质量延迟与成本影响

保留历史版本会增大索引；时间过滤可能降低 ANN 效率；频繁更新增加 Embedding 与重建成本。可分冷热索引、只重算改变的 Chunk，并监控源到索引的延迟分布。费用与新鲜度要求必须一起确定。

## 数据评测与安全风险

测试当前、历史、未来生效、边界时刻、延迟到达、撤销、冲突和无时间问题。时间解析要明确时区。过期不等于可公开，历史版本仍受权限与保留策略约束。回答应展示证据有效期和索引水位，而不是只给模糊的“最新”。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 回答引用旧政策 | 索引延迟或缓存未失效 | 数据水位、版本、缓存键 |
| 历史问题引用新版 | 查询时间未提取 | 时间意图、有效期过滤 |
| 切换日命中两版 | 区间边界定义重叠 | 半开区间、时区、日期精度 |
| 系统声称最新但源已停 | 未监控摄取水位 | event time、ingested_at、告警 |
| 同一时间答案冲突 | 多源权威或版本关系缺失 | 来源优先级、冲突队列 |

## 适用与不适用场景

适合政策、新闻、价格、产品状态和任何随时间变化的知识。完全静态语料仍应记录版本，但不必构建复杂时间排序。实时交易状态通常优先查询权威工具，而不是等待文档索引。

## 学习收益

你应能区分业务时间和摄取时间，设计半开有效区间，处理历史问题与冲突，并量化源到索引延迟。

## 给别人讲清楚

“最新文档不一定是问题所问时间的正确文档。时效 RAG 像查法规档案：先确定问题发生在哪一天，再找那天有效的版本，并说明数据更新到了什么时候。”

## 自检问题

1. 为什么更新时间不能替代有效期？
2. 半开区间怎样避免切换日重复命中？
3. 数据源中断时系统应该怎样降级？

## 相关主题

- [RAG 元数据](07-RAG 元数据.md)
- [RAG 流式更新](34-RAG 流式更新.md)
- [RAG 方案选型](39-RAG 方案选型.md)

## 资料来源

- Ricardo Baeza-Yates, [Searching the Future](https://dl.acm.org/doi/10.1145/1772690.1772698), 2005，访问日期：2026-09-10。
- Apache Beam, [Programming Guide Event Time](https://beam.apache.org/documentation/programming-guide/#event-time-and-watermarks)，访问日期：2026-09-10。
- Elasticsearch, [Date range query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html)，访问日期：2026-09-10。

