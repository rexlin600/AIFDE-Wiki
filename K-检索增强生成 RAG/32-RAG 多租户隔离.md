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
  - RAG 租户隔离
tags:
  - multi-tenancy
  - isolation
---

# RAG 多租户隔离

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

多租户 RAG 让多个客户或组织共享服务能力，同时隔离文档、索引、查询、缓存、配额、加密密钥和日志。核心目标是：在定义的机密性、完整性和可用性边界内，租户 A 不能读取或篡改租户 B 的知识，也不能无配额地挤占其服务能力。共享基础设施仍可能存在残余侧信道和资源干扰，需要风险评估。

## 不理解会造成什么错误

- 文档带租户字段，但向量查询忘记过滤。
- 查询缓存只用文本作键，跨租户复用答案。
- 临时文件、批处理和评测输出混入其他租户数据。
- 一个大租户耗尽并发和索引资源，拖慢所有客户。
- 删除租户时只删原文，Embedding 和备份仍保留。

## 它在 RAG 链路中的位置

租户上下文从认证网关注入，贯穿摄取、对象存储、索引、检索、重排、上下文、模型调用、缓存、日志和删除。任何中间层丢失租户标识，都可能成为跨租户泄露点。

## 简单基线

高敏感或规模较小客户可使用物理独立索引与存储，边界清楚但成本高。共享索引配租户过滤更省资源，却要求每条路径都强制执行策略。选择取决于风险、规模、过滤能力和合规要求。

## 隔离不只是一列 tenant_id

可以把资源键写成复合键：

$$
k=(tenant\_id, resource\_id, version)
$$

缓存键还需包含权限摘要与索引版本：

$$
k_{cache}=H(tenant,visibility,acl\_version,query,index,config)
$$

若遗漏 tenant，相同查询会碰撞；`visibility` 是由服务端可信角色、组和 ABAC 属性得到的可见范围摘要，不能由客户端自报。只有策略版本而没有主体可见范围时，租户内普通用户和管理员仍可能错误共享。

## 最小手算

两个租户都问“退款政策是什么”。只以查询哈希作缓存键，两者得到同一个键；若加入租户 ID，则成为两个独立键。若同一租户内普通员工和管理员可见范围不同，还必须加入权限摘要。

## 可执行实验

```python
import hashlib

def cache_key(tenant, visibility, acl_version, query, index_version):
    raw = "|".join((tenant, visibility, acl_version, query, index_version))
    return hashlib.sha256(raw.encode()).hexdigest()

query = "退款政策是什么"
key_a = cache_key("tenant-a", "groups:staff", "acl-3", query, "index-7")
key_b = cache_key("tenant-b", "groups:staff", "acl-3", query, "index-7")
key_a_admin = cache_key("tenant-a", "groups:admin", "acl-3", query, "index-7")
key_a_new_acl = cache_key("tenant-a", "groups:staff", "acl-4", query, "index-7")
assert key_a != key_b
assert key_a != key_a_admin
assert key_a != key_a_new_acl

store = {("tenant-a", "doc-1"): "A 的政策"}
def read(tenant, document_id):
    return store.get((tenant, document_id))

assert read("tenant-a", "doc-1") == "A 的政策"
assert read("tenant-b", "doc-1") is None
print(key_a[:8], key_b[:8], "isolation passed")
```

实验验证租户、主体可见范围和策略版本共同进入复合键，不能证明底层数据库、队列、GPU 内存或日志平台已经隔离。真实系统需要端到端穿透测试。

## 资源和故障隔离

隔离还包括公平性。为租户设置并发、Token、索引写入和存储配额；调度器避免单个长请求占满批次；熔断与降级按租户生效。共享模型可以降低成本，但 Prompt 和 KV Cache 不得跨请求错误复用。

## 租户生命周期

创建租户时生成命名空间、策略和密钥；迁移时对账文档与索引；停用时拒绝新请求；删除时传播到原文、Chunk、向量、缓存、日志派生物和备份保留流程。完成删除需要可核验清单，而不是单个 API 的 200 响应。

## 质量延迟与成本影响

物理隔离质量边界简单但资源利用率低；逻辑隔离提高共享率，但复杂过滤可能降低召回和 ANN 性能。按租户报告空结果、Recall、P95 延迟和成本，避免总体指标掩盖小租户退化。

## 数据评测与安全风险

构造相同文档 ID、相同查询、不同权限、缓存命中、批量摄取、重试、导出与删除等跨租户攻击用例。评测环境也必须隔离，不能拿客户文档组成共享基准。日志和指标标签避免包含敏感正文或无限高基数字段。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 相同查询返回他人政策 | 缓存键缺租户或 ACL | 键构造、缓存命中 Trace |
| 小租户延迟突然升高 | 邻居占满共享资源 | 配额、队列、批户切片指标 |
| 删除后仍能搜到 | 派生索引或缓存残留 | 资源清单、墓碑、对账 |
| 批量导入串租户 | 任务上下文丢失 | 队列载荷、服务端认证 |
| 相同文档 ID 覆盖 | 主键未命名空间化 | 复合键、索引分区 |

## 适用与不适用场景

任何 SaaS 或共享平台都需要多租户隔离。单组织内部仍可能需要部门和项目隔离，但这更接近权限控制。高监管数据可能要求物理隔离，不能只依据成本选择共享索引。

## 学习收益

你应能列出租户上下文贯穿的全部层次，设计复合缓存键和资源配额，并规划租户创建、迁移与删除验证。

## 给别人讲清楚

“多租户隔离不是给文档贴一张客户标签，而是让这张标签跟着数据走完整条链路：索引、缓存、队列、日志和删除都不能丢。”

## 自检问题

1. 为什么租户内仍可能需要 ACL 版本进入缓存键？
2. 物理隔离和逻辑隔离分别付出什么代价？
3. 怎样证明一个租户已经被完整删除？

## 相关主题

- [RAG 权限控制](31-RAG 权限控制.md)
- [RAG 数据摄取](03-RAG 数据摄取.md)
- [RAG 流式更新](34-RAG 流式更新.md)

## 资料来源

- NIST, [Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)，访问日期：2026-09-10。
- Cloud Security Alliance, [Security Guidance for Critical Areas of Focus in Cloud Computing](https://cloudsecurityalliance.org/artifacts/security-guidance-v4)，访问日期：2026-09-10。
- OWASP, [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)，访问日期：2026-09-10。
