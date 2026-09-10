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
  - RAG Context Construction
tags:
  - context-budget
  - citation-map
---

# RAG 上下文构建

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

检索器返回的是候选，不是可以原样塞给模型的最终上下文。上下文构建在授权边界内完成过滤、去重、冲突标记、排序、必要压缩和 Token 分配，同时保存“上下文片段到原始来源”的引用映射。

## 不理解会造成什么错误

- top-k 全部拼接，重复内容挤走真正互补的证据。
- 没给系统指令、查询和输出预留 Token，答案中途截断。
- 压缩后只保留摘要，无法追踪原文页码和引用。
- 先装配再过滤权限，未授权文本已进入模型输入或日志。
- 冲突版本被静默混合，模型选择了过期结论。

## 它在 RAG 链路中的位置

```text
检索与重排候选 → 权限时效过滤 → 去重与冲突分组
→ 预算排序与压缩 → 编号证据块 + 引用映射 → LLM → 引用校验
```

LLM 通用上下文窗口原理见[大模型上下文工程](../J-大模型%20LLM/06-大模型上下文工程.md)；本篇聚焦 RAG 证据的装配与可追溯性。

## 从政策问答开始

用户问“2026 年上海住宿上限”。候选含新版 600 元、旧版 500 元、三份转载和一份无权限财务说明。正确流程先按身份与生效时间过滤，再按内容和来源去重，保留新版政策及必要适用条件，每段标成 `[E1]` 并映射到原文。

简单基线是只放重排第一条证据。新增更多片段前，要证明它们提高证据覆盖而非只增加 Token。

## 输入输出与数据形状

候选项至少包含：`chunk_id`、文本、Token 数、相关性、来源、版本、有效期、权限和原文位置。输出包含：

```text
context_text
citation_map: E1 → source_id, chunk_id, page, offsets, version
excluded: chunk_id → reason
budget_snapshot
```

压缩文本与原文要分开存，`E1` 必须始终指回原始、可打开且经过授权的来源。

## 上下文预算推导

设模型窗口为 $W$，系统指令为 $S$，用户查询为 $Q$，证据为 $E$，输出预留为 $O$，安全余量为 $M$：

$$
S+Q+E+O+M\le W
$$

所以证据预算为：

$$
B_E=W-S-Q-O-M
$$

若 $B_E<0$，必需部分已超限，应缩短任务、拒绝或换模型，不能删除权限和安全规则。对候选 $i$ 定义相关性 $r_i$、可信度 $t_i$、新鲜度 $f_i$、Token 成本 $c_i$，可用启发式单位价值：

$$
v_i=\frac{r_it_if_i}{c_i}
$$

它便于排序，但不能替代冲突检查、覆盖多样性和业务硬规则。

## 最小手算

$W=4096$，系统 500、查询 200、输出预留 800、余量 200，则证据预算：

$$
B_E=4096-500-200-800-200=2396
$$

三个候选分别为 900、800、1000 Token，总计 2700，至少压缩或删除 304 Token。若前两段内容重复，去掉第二段可剩 1900，并留 496 Token 余量。

证据 `[E1]` 压缩成 80 Token 后，映射仍是 `E1 → doc-policy-v2, page 3, chunk c17`，引用不能改指向摘要本身。

## 可执行实验

```python
def assemble(window, system_tokens, query_tokens, output_reserve, margin,
             candidates, actor_roles):
    budget = window - system_tokens - query_tokens - output_reserve - margin
    if budget < 0:
        raise ValueError("mandatory parts exceed context window")

    # 权限和时效应在文本进入装配器之前生效；此处显式演示两种过滤。
    excluded = {}
    allowed = []
    for item in candidates:
        if not actor_roles & item["roles"]:
            excluded[item["id"]] = "unauthorized"
        elif not item["current"]:
            excluded[item["id"]] = "expired"
        else:
            allowed.append(item)
    dedup = {}
    for item in allowed:
        key = item["content_hash"]
        if key not in dedup or item["score"] > dedup[key]["score"]:
            if key in dedup:
                excluded[dedup[key]["id"]] = "duplicate"
            dedup[key] = item
        else:
            excluded[item["id"]] = "duplicate"
    ranked = sorted(dedup.values(),
                    key=lambda c: c["score"] * c["trust"] / c["tokens"],
                    reverse=True)

    blocks, citation_map, used = [], {}, 0
    for item in ranked:
        if used + item["tokens"] > budget:
            excluded[item["id"]] = "over_budget"
            continue
        eid = f"E{len(blocks) + 1}"
        blocks.append(f"[{eid}] {item['text']}")
        citation_map[eid] = {
            "source": item["source"], "chunk": item["id"],
            "page": item["page"], "version": item["version"]
        }
        used += item["tokens"]
    snapshot = {"budget": budget, "used": used, "excluded": excluded}
    return "\n".join(blocks), citation_map, snapshot

candidates = [
    {"id": "c17", "text": "上海住宿上限为 600 元。", "tokens": 80,
     "score": 0.95, "trust": 1.0, "roles": {"staff"}, "current": True,
     "content_hash": "h1", "source": "policy-v2", "page": 3, "version": 2},
    {"id": "copy", "text": "上海住宿上限为 600 元。", "tokens": 80,
     "score": 0.80, "trust": 0.7, "roles": {"staff"}, "current": True,
     "content_hash": "h1", "source": "mirror", "page": 1, "version": 2},
    {"id": "old", "text": "上海住宿上限为 500 元。", "tokens": 70,
     "score": 0.90, "trust": 1.0, "roles": {"staff"}, "current": False,
     "content_hash": "h-old", "source": "policy-v1", "page": 3, "version": 1},
    {"id": "secret", "text": "财务内部预算。", "tokens": 60,
     "score": 0.99, "trust": 1.0, "roles": {"finance"}, "current": True,
     "content_hash": "h-secret", "source": "finance", "page": 2, "version": 1},
]

context, mapping, usage = assemble(500, 100, 50, 150, 20, candidates, {"staff"})
assert context == "[E1] 上海住宿上限为 600 元。"
assert mapping["E1"] == {"source": "policy-v2", "chunk": "c17",
                         "page": 3, "version": 2}
assert usage["used"] <= usage["budget"]
assert "secret" not in {m["chunk"] for m in mapping.values()}
assert "old" not in {m["chunk"] for m in mapping.values()}
assert usage["excluded"] == {
    "copy": "duplicate", "old": "expired", "secret": "unauthorized"
}

try:
    assemble(200, 100, 50, 80, 20, [], {"staff"})
    raise AssertionError("negative evidence budget should fail")
except ValueError:
    pass

print(context, mapping, usage)
```

## 实验结果解释

实验先排除越权与旧版本，再按内容哈希去重，在预算内装配唯一证据，并同时返回每个排除原因与来源映射；必需部分超限时明确失败。人工 Token 和分数不能替代真实 Tokenizer、冲突检测或答案 Faithfulness 评测。

## 质量延迟与成本影响

- 更多证据可能提高覆盖，也增加 Prefill 延迟、输入费用与噪声。
- 去重通常同时降低成本和重复偏置；语义去重本身可能误删互补细节。
- 压缩节省 Token，却可能删除限定词、数字或否定，应保留原文映射并评测。
- 装配算法要记录候选、排除原因和最终快照，便于定位是检索错还是装配错。

## 数据评测与安全风险

评测证据覆盖、上下文精度、答案支持率、引用可打开率、Token 使用和位置切片。权限过滤在候选读取边界生效，未授权文本不能先送入压缩模型。检索文档是不可信数据，可能包含提示注入；必须和系统指令分隔，工具执行仍重新授权。删除与权限变更要传播到索引、缓存、装配日志和引用页面。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 关键证据召回却未回答 | 装配排序或预算淘汰 | 候选与最终快照、排除原因 |
| 上下文充满重复段落 | 去重键或版本设计错误 | 内容哈希、规范化、父子 ID |
| 引用打不开或对不上 | 压缩后丢失映射 | citation_map、原文位置、版本 |
| 旧政策与新政策混用 | 时效过滤或冲突标记缺失 | valid time、版本、来源优先级 |
| 模型看到越权内容 | 过滤晚于读取或压缩 | ACL 执行点、缓存键、调用日志 |
| 输出被截断 | 未预留输出 Token | 预算公式、停止原因、长度分布 |

## 适用与不适用场景

任何把多条检索证据交给生成模型的 RAG 都需要上下文构建。若任务是精确数据库查询并可直接模板化返回，没必要为了“像 RAG”而拼接文本；若必需材料本身超窗，应分阶段处理而非静默截断。

## 学习收益

你应能推导证据预算，按正确顺序执行授权、时效、去重和装配，保存稳定引用映射，并联合权衡质量、延迟、成本与安全。

## 给别人讲清楚

“检索结果像一桌候选材料：先过门禁和有效期，再去重、按预算摆上工作台；每张材料都贴编号，编号能回到原件。”

## 自检问题

1. 为什么必须在分配证据预算前预留输出 Token？
2. 权限过滤为什么要早于压缩？
3. 压缩证据后如何保证引用仍能追溯原文？

## 相关主题

- [RAG 重排序](11-RAG%20重排序.md)
- [父子文档检索](12-父子文档检索.md)
- [RAG 知识时效](33-RAG%20知识时效.md)
- [RAG 引用生成](36-RAG%20引用生成.md)

## 资料来源

- Liu 等, [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/)，访问日期：2026-09-10。
- OpenAI, [Retrieval](https://platform.openai.com/docs/guides/retrieval)，访问日期：2026-09-10。
- OWASP, [Vector and Embedding Weaknesses](https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/)，访问日期：2026-09-10。
