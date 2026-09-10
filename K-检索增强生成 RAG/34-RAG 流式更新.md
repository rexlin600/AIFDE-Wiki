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
  - RAG 增量索引
tags:
  - streaming
  - indexing
---

# RAG 流式更新

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

RAG 流式更新把新增、修改、权限变更和删除持续传播到解析产物、Chunk、Embedding 与检索索引。目标不是抽象的“实时”，而是在明确时间内让可查询状态与权威源一致，并能发现和修复漏事件。

## 不理解会造成什么错误

- 重复消费事件，产生重复 Chunk。
- 修改文档只写新向量，旧版本仍被召回。
- 删除原文但没有删除向量和缓存。
- 事件乱序使旧版本覆盖新版本。
- 消费延迟正常就认为索引完整，忽略永久漏数。

## 它在 RAG 链路中的位置

权威源产生变更事件，摄取服务解析并按内容哈希判断是否重算，写入版本化索引，再更新可见水位。查询只读取已发布的一致索引版本；对账任务周期性比较源清单与索引清单。

## 简单基线

小型且低频更新的知识库可定时全量重建，并以原子别名切换。这最容易验证。只有全量窗口无法满足新鲜度或成本要求时，才引入持续增量更新，同时保留全量重建作为恢复路径。

## 事件状态

事件至少包含：

```text
event_id resource_id version operation source_time content_hash
```

对资源 $r$，只接受版本严格更新的事件：

$$
v_{event}>v_{stored}
$$

相同 `event_id` 重放必须无副作用；删除用墓碑表示，防止较晚到达的旧写入让资源“复活”。

## 延迟怎样计算

源到可查询索引的延迟为：

$$
L_{fresh}=t_{queryable}-t_{source}
$$

队列延迟、解析、Embedding、索引提交和发布应分别记录。P95 水位健康仍不能证明无漏数，因此还需要集合对账。

## 最小手算

版本 3 已存储，依次到达版本 4、重复版本 4、迟到版本 2、删除版本 5。只有首次版本 4 和删除版本 5改变状态；重复与旧版本跳过。最终资源版本为 5，状态为已删除。

## 可执行实验

```python
state = {}
seen_events = set()

def apply(event, fail_before_commit=False):
    if event["event_id"] in seen_events:
        return "duplicate"
    current = state.get(event["resource_id"])
    if current and event["version"] <= current["version"]:
        seen_events.add(event["event_id"])
        return "stale"
    next_state = {
        "version": event["version"],
        "deleted": event["operation"] == "delete",
    }
    if fail_before_commit:
        return "failed"
    # 生产中以下状态和幂等记录必须在同一事务或原子写入中提交。
    state[event["resource_id"]] = next_state
    seen_events.add(event["event_id"])
    return "applied"

events = [
    {"event_id": "e4", "resource_id": "doc-1", "version": 4,
     "operation": "upsert"},
    {"event_id": "e4", "resource_id": "doc-1", "version": 4,
     "operation": "upsert"},
    {"event_id": "e2", "resource_id": "doc-1", "version": 2,
     "operation": "upsert"},
    {"event_id": "e5", "resource_id": "doc-1", "version": 5,
     "operation": "delete"},
]
results = [apply(event) for event in events]
print(results, state)
assert results == ["applied", "duplicate", "stale", "applied"]
assert state["doc-1"] == {"version": 5, "deleted": True}
retry = {"event_id": "e6", "resource_id": "doc-2", "version": 1,
         "operation": "upsert"}
assert apply(retry, fail_before_commit=True) == "failed"
assert "e6" not in seen_events and "doc-2" not in state
assert apply(retry) == "applied"
```

实验验证失败前不抢先记录幂等键，并覆盖重试、版本和墓碑规则。生产中状态与幂等记录必须用同一事务或等价原子提交；实验不涵盖两个写入者并发或底层索引的可见性保证。

## 发布与恢复

小更新可原子写入文档及其全部 Chunk；大批次先构建影子索引，验证数量、哈希、权限和抽样查询后切换别名。保留上一版本以便回滚。事件日志能重放，但只有定期从权威源全量重建，才能验证恢复能力。

## 对账怎样发现漏数

按资源 ID、版本、内容哈希和删除状态比较源与索引，输出源有索引无、索引有源无、版本不等和内容不等四类差异。不要只比总数，因为一个遗漏与一个重复可能互相抵消。

## 质量延迟与成本影响

逐条 Embedding 新鲜但吞吐低，微批能摊薄调用和索引提交成本，却增加等待。选择批大小要同时测 P95 新鲜度、吞吐、失败重试和费用。频繁修改可做去抖，前提是业务允许中间版本不可见。

## 数据评测与安全风险

测试重复、乱序、毒消息、部分失败、权限撤销、删除、重放和全量恢复。死信队列中的内容仍是敏感数据。权限事件通常比正文更新优先级更高；无法及时撤权时应阻断资源读取。日志记录 ID 和哈希，避免复制完整正文。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 同一文档重复出现 | 幂等键或 Chunk ID 不稳定 | event_id、资源版本、确定性 ID |
| 删除后又被召回 | 旧事件覆盖墓碑 | 版本比较、墓碑保留、缓存 |
| 水位正常但缺文档 | 漏事件未被发现 | 源索引对账、死信队列 |
| 更新成本突然上升 | 无变化内容重复编码 | 内容哈希、去抖、微批 |
| 发布时查询结果混杂 | 非原子切换 | 影子索引、别名、读版本 |

## 适用与不适用场景

适合更新频繁且有明确新鲜度目标的知识库。日更或周更语料往往用全量重建更简单可靠。即便使用流式更新，也必须保留可重建、可对账和可回滚路径。

## 学习收益

你应能设计幂等事件、版本规则和墓碑删除，拆解新鲜度延迟，比较微批与逐条更新，并用对账证明完整性。

## 给别人讲清楚

“流式更新像持续修订图书目录：同一通知可能来两次，旧通知可能晚到，撤下的书不能复活。事件处理要幂等，版本要单调，还要定期拿书架和目录逐本对账。”

## 自检问题

1. 为什么队列无积压不能证明索引完整？
2. 墓碑怎样阻止旧写入让删除资源复活？
3. 有增量事件日志后为什么仍要演练全量重建？

## 相关主题

- [RAG 数据摄取](03-RAG 数据摄取.md)
- [RAG 知识时效](33-RAG 知识时效.md)
- [RAG 权限控制](31-RAG 权限控制.md)

## 资料来源

- Pat Helland, [Immutability Changes Everything](https://www.cidrdb.org/cidr2015/Papers/CIDR15_Paper16.pdf), 2015，访问日期：2026-09-10。
- Apache Kafka, [Design](https://kafka.apache.org/documentation/#design)，访问日期：2026-09-10。
- Debezium, [Documentation](https://debezium.io/documentation/)，访问日期：2026-09-10。
