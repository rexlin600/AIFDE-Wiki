---
type: concept
domain: [RAG]
depth: L2
importance: core
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases: [RAG Metadata]
tags: [metadata, filtering]
---

# RAG 元数据

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

元数据描述 Chunk 的来源、版本、时间、语言、租户和访问范围。文本相似度回答“内容像不像”，元数据过滤回答“这位用户此刻能不能看、该看哪一版”。

## 不理解会造成什么错误

- 把权限写进正文，期待向量相似度自动阻止越权。
- 日期存成自由文本，无法可靠比较生效时间。
- 字段类型随数据源变化，过滤条件静默失效。
- 在召回后才过滤，导致 Top-k 为空或敏感候选泄漏。

## 它在 RAG 链路中的位置

`摄取与解析 → 生成标准元数据 → Chunk 继承 → 索引过滤 → 候选`。推荐区分不可变来源字段、版本字段和查询时授权上下文；动态用户权限不应复制成不可维护的正文。

## 从地区政策问答开始

用户问“当前上海差旅上限”。简单基线是只检索相似文本，可能返回北京旧版制度。加入 `region`、`valid_from`、`valid_to` 和 `acl` 的类型化过滤，先缩小到当前用户有权访问且在查询时刻生效的集合。

## 过滤集合怎样形成

设全部 Chunk 集合为 $D$，用户可访问集合为 $A(u)$，时刻 $t$ 有效集合为 $V(t)$，地区集合为 $R(r)$：

$$
C=D\cap A(u)\cap V(t)\cap R(r)
$$

检索只在 $C$ 中取 Top-k。条件是“与”，任一失败就排除。过滤后再取 Top-k 与先取 Top-k 再过滤不同：后者可能明明有授权结果，却因候选窗口被越权内容占满而返回不足。

## 最小手算

4 个 Chunk 中，上海有 3 个；当前有效有 3 个；员工可访问有 3 个。地区、时间和权限三集合的交集只有文档 A，因此候选集大小从 4 变为 1。相似度再高的旧版或越权文档都不得进入排序。

## 可执行实验

```python
from datetime import date

chunks = [
    {"id": "A", "region": "上海", "valid_from": date(2026, 1, 1),
     "valid_to": None, "acl": {"employee"}, "score": 0.80},
    {"id": "OLD", "region": "上海", "valid_from": date(2025, 1, 1),
     "valid_to": date(2025, 12, 31), "acl": {"employee"}, "score": 0.99},
    {"id": "SECRET", "region": "上海", "valid_from": date(2026, 1, 1),
     "valid_to": None, "acl": {"finance"}, "score": 1.00},
    {"id": "B", "region": "北京", "valid_from": date(2026, 1, 1),
     "valid_to": None, "acl": {"employee"}, "score": 0.90},
]

def allowed(item, role, region, when):
    active = item["valid_from"] <= when and (item["valid_to"] is None or when <= item["valid_to"])
    return role in item["acl"] and item["region"] == region and active

candidate_ids = [item["id"] for item in chunks if allowed(item, "employee", "上海", date(2026, 9, 10))]
print(candidate_ids)
assert candidate_ids == ["A"]
assert "SECRET" not in candidate_ids
assert "OLD" not in candidate_ids
```

## 实验结果边界

实验验证类型化日期、地区和角色的交集过滤。集合中的 ACL 只是教学模型，不代表完整 RBAC、ABAC 或行级安全；生产授权必须由可信身份与策略服务判定，并测试索引后端的过滤语义。

## 质量延迟与成本影响

过滤提高结果适用性并减少无效候选，但高基数字段、复杂谓词或选择率极低时可能增加查询开销。应监控过滤前后候选量、零结果率和授权判定耗时；常用字段建立合适索引。

## 数据评测与安全风险

字段命名、类型、空值语义和枚举需有 Schema。默认拒绝未知权限，不能把缺失 ACL 当公开。日志可记录策略 ID 和允许或拒绝原因，不记录敏感正文。删除和权限变更要传播到缓存。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 返回其他地区制度 | 地区缺失或过滤未下推 | Schema、查询谓词、过滤前后计数 |
| 旧版排名最高 | 日期为字符串或区间错误 | 类型、时区、闭开区间 |
| 授权用户无结果 | 空值默认拒绝或角色映射错 | ACL 字段、身份声明、拒绝原因 |
| 越权文档进入 Trace | 召回后才过滤 | 候选生成边界、缓存、日志 |
| 查询延迟突增 | 高基数字段或低选择率 | 执行计划、字段索引、谓词组合 |

## 适用与不适用场景

权限、地区、产品、时间和来源筛选都适合类型化元数据。语义概念不宜全部强塞进枚举字段，应由文本或向量检索处理。元数据过滤不是内容正确性的证明。

## 学习收益

你应能定义稳定 Schema，写出候选集合交集，解释过滤顺序，并区分文档属性与查询时授权状态。

## 给别人讲清楚

“相似度负责找得像，元数据负责找得对范围。权限、时间和地区是硬门槛，应该先过门再比赛排名。”

## 自检问题

1. 为什么先 Top-k 再做权限过滤可能漏掉授权结果？
2. 缺失 ACL 字段应默认公开还是拒绝？
3. 哪些元数据变化需要让缓存失效？

## 相关主题

- [RAG 权限控制](31-RAG%20权限控制.md)
- [RAG 知识时效](33-RAG%20知识时效.md)
- [RAG 向量索引](10-RAG%20向量索引.md)

## 资料来源

- NIST, [Role Based Access Control](https://csrc.nist.gov/projects/role-based-access-control)，访问日期：2026-09-10。
- NIST, [Attribute Based Access Control](https://csrc.nist.gov/pubs/sp/800/162/upd2/final)，访问日期：2026-09-10。
- Elasticsearch, [Boolean query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html)，访问日期：2026-09-10。
