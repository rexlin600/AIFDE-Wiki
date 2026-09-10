---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [RAG Ingestion]
tags: [ingestion, lineage]
---

# RAG 数据摄取

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

数据摄取把网页、工单和文件的变化可靠地变成可解析事件。它回答“内容来自哪里、是哪一版、是否重复、删除能否传播”。没有可靠入口，后面的检索再好也只是在错误知识上排序。

## 不理解会造成什么错误

- 定时任务重复写入同一内容，近重复 Chunk 挤占 Top-k。
- 只保存文本而丢失来源版本，答案无法追溯。
- 更新覆盖旧文档却不生成删除事件，过期内容仍可召回。
- 把抓取成功等同于索引可用，忽略解析或索引失败。

## 它在 RAG 链路中的位置

`来源 → 发现变化 → 获取字节 → 计算身份与版本 → 事件清单 → 解析`。输出不是 Chunk，而是带来源身份、内容哈希、时间和动作的原始文档记录。

## 从制度更新开始

人事助手每天同步制度库。简单基线是每晚全量重建；它容易实现，但数据量大时成本高、空窗长。增量摄取只处理新增、改变和删除内容，同时保留全量重建能力用于灾难恢复。

## 身份版本和幂等

来源身份 `source_id` 表示逻辑文档。对原始字节 $x$ 计算内容哈希：

$$
h(x)=\operatorname{SHA256}(x)
$$

稳定的 `source_id` 标识逻辑文档，来源系统提供的 `event_id` 或单调游标标识一次变更，内容哈希只用于判断当前内容是否变化。不能把 $(source\_id,h)$ 当作全局事件键：内容从 `h1` 变成 `h2` 后合法回滚到 `h1`，仍应产生新版本。若相邻状态哈希变化：

$$
v_{new}=v_{old}+\mathbb{1}[h_{new}\ne h_{old}]
$$

删除用墓碑事件表达，不能只让源文件消失，否则下游不知道该清理哪些 Chunk。

## 最小手算

文档 A 首次哈希 `h1` 产生版本 1；重试仍是 `h1`，版本保持 1；内容变为 `h2`，版本成为 2；随后删除，记录版本 3 的墓碑。四次投递只有三次状态变化。

## 可执行实验

```python
import hashlib

state, events = {}, []
def ingest(source_id, content=None):
    digest = "DELETE" if content is None else hashlib.sha256(content).hexdigest()
    previous = state.get(source_id)
    if previous and previous["hash"] == digest:
        return False
    version = 1 if previous is None else previous["version"] + 1
    record = {"source_id": source_id, "hash": digest,
              "version": version, "deleted": content is None}
    state[source_id] = record
    events.append(record.copy())
    return True

assert ingest("policy-A", b"leave=5")
assert not ingest("policy-A", b"leave=5")
assert ingest("policy-A", b"leave=7")
assert ingest("policy-A", None)
assert not ingest("policy-A", None)
print(events)
assert [event["version"] for event in events] == [1, 2, 3]
assert state["policy-A"]["deleted"]
assert ingest("policy-A", b"leave=5")  # 删除后恢复旧内容仍是新状态
assert state["policy-A"]["version"] == 4
```

## 实验结果边界

实验验证相邻内容幂等、版本递增、墓碑和旧内容合法恢复。它没有模拟来源事件 ID、事务、并发竞争、对象存储故障或哈希碰撞；生产系统还需持久化事件唯一约束、重试队列和对账。

## 质量延迟与成本影响

增量摄取缩短知识更新延迟并减少重算，但事件日志、原始快照和重建流水线占用存储。内容哈希是线性扫描成本 $O(n)$。应分别监控发现延迟、获取延迟、端到端可检索延迟和失败积压。

## 数据评测与安全风险

获取凭证采用最小权限，原始文件与日志不得泄露令牌。记录数据许可、保留期、PII 分类和租户。删除需传播到解析产物、索引、缓存与备份策略；不能用“搜索不到”代替合规删除证明。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 同文档大量重复 | 幂等键缺失或 URL 未规范化 | source_id、内容哈希、唯一约束 |
| 更新后仍答旧内容 | 下游未消费新版本 | 事件位点、索引版本、端到端水位 |
| 删除后仍可召回 | 没有墓碑或缓存未失效 | 删除事件、Chunk 映射、缓存键 |
| 突然漏同步 | 凭证过期或游标跳跃 | 权限、分页游标、失败队列 |
| 无法复现索引 | 原始快照或配置未版本化 | 清单、快照、解析器版本 |

## 适用与不适用场景

持续更新的 RAG 都需要可追踪摄取。极小且静态的本地材料可全量重建，但仍应保留来源与哈希。摄取不负责理解 PDF 布局，也不负责决定 Chunk 边界。

## 学习收益

你应能区分逻辑身份、内容版本与处理状态，设计幂等键和墓碑，并说明怎样从原始快照重建索引。

## 给别人讲清楚

“摄取像知识库的收件台：每件材料有来源身份证和内容指纹。重复投递不重复入库，修改产生新版，删除也必须送达下游。”

## 自检问题

1. 为什么文件路径不能总是充当稳定身份？
2. 内容哈希相同的重试为什么不应创建新版本？
3. 删除事件需要传播到哪些派生产物？

## 相关主题

- [RAG 文档解析](04-RAG%20文档解析.md)
- [RAG 流式更新](34-RAG%20流式更新.md)
- [RAG 知识时效](33-RAG%20知识时效.md)

## 资料来源

- Apache Kafka, [Message Delivery Semantics](https://kafka.apache.org/documentation/#semantics)，访问日期：2026-09-10。
- Amazon Web Services, [Make mutating operations idempotent](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_prevent_interaction_failure_idempotent.html)，访问日期：2026-09-10。
- NIST, [Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)，访问日期：2026-09-10。
