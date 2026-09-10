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
  - RAG 证据引用
tags:
  - citation
  - attribution
---

# RAG 引用生成

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

引用生成把回答中的可核验主张连接到具体证据，使用户能判断答案根据什么得出。企业政策问答不能只给“来源：员工手册”，而应指出版本、章节和支持该句话的片段。

## 不理解会造成什么错误

- 有链接就判定引用正确，不检查内容是否支持主张。
- 一段末尾堆多个引用，无法知道各自支持哪句话。
- 引用检索 Chunk，但用户打开后找不到原文位置。
- 模型生成不存在的文档 ID 或 URL。
- 答案正确就忽略引用错误，掩盖证据链故障。

## 它在 RAG 链路中的位置

检索返回不可伪造的证据 ID、来源和原文位置；上下文构建保留 ID；模型只能引用提供的 ID；程序验证 ID 存在与权限；评测再判断引用是否支持相邻主张。引用是生成和检索之间的可审计接口。

## 简单基线

最简单方法是在每个回答段落后附使用的 Chunk ID。若答案包含多个独立事实，应进一步拆成主张级引用。没有证据时明确拒答，比生成看似专业的引用更可靠。

## 三层引用正确性

1. 有效性：引用 ID 存在、可访问且版本匹配。
2. 归属：证据内容确实支持对应主张。
3. 完整性：需要证据的主张都得到支持。

设答案有 $m$ 个可核验主张，$s_i=1$ 表示主张 $i$ 至少有一个支持证据，则引用覆盖率为：

$$
Coverage=\frac{\sum_{i=1}^{m}s_i}{m}
$$

设共给出 $n$ 个引用关系，$e_j=1$ 表示第 $j$ 个关系真正蕴含主张，则归属正确率为：

$$
Precision=\frac{\sum_{j=1}^{n}e_j}{n}
$$

## 最小手算

回答有 3 个主张，其中 2 个有支持证据，覆盖率为 $2/3$。共给出 4 个引用关系，其中 3 个真正支持相邻主张，归属正确率为 $3/4$。两个指标必须同时报告：多贴链接可能提高覆盖，却降低精确归属。

## 可执行实验

```python
claims = {
    "c1": {"citations": ["e1"], "needs_evidence": True},
    "c2": {"citations": ["e2", "e3"], "needs_evidence": True},
    "c3": {"citations": [], "needs_evidence": True},
}
support = {("c1", "e1"), ("c2", "e2")}
allowed_evidence = {"e1", "e2", "e3"}

def citation_metrics(claim_items, supported):
    required = [(claim_id, item) for claim_id, item in claim_items.items()
                if item["needs_evidence"]]
    relations = [(claim_id, evidence_id)
                 for claim_id, item in claim_items.items()
                 for evidence_id in item["citations"]]
    covered = sum(any((claim_id, evidence_id) in supported
                      for evidence_id in item["citations"])
                  for claim_id, item in required)
    # 无待核验主张或无引用时返回 None，表示 N/A，而不是伪造 0 分。
    coverage = covered / len(required) if required else None
    precision = (sum(pair in supported for pair in relations) / len(relations)
                 if relations else None)
    return coverage, precision, relations

coverage, precision, relations = citation_metrics(claims, support)
print("coverage", round(coverage, 3), "precision", round(precision, 3))
assert coverage == 2 / 3
assert precision == 2 / 3
assert all(evidence_id in allowed_evidence for _, evidence_id in relations)
assert citation_metrics({}, set())[:2] == (None, None)
```

实验区分覆盖和归属，并把无待核验主张或无引用明确报告为 N/A，避免除零。`support` 是人工给定金标准；真实自动蕴含判断可能出错，关键领域需要人工抽样或规则核验。

## 引用协议

上下文给每个证据分配短 ID，如 `[E3]`，模型输出结构化的主张与 ID。程序拒绝未知 ID，再将 ID 渲染为可打开链接。真实 URL 不交给模型自由拼接。父子文档检索还要把子 Chunk 映射回父文档页码和高亮范围。

## 答案正确与引用正确分开评测

模型可能凭参数记忆答对，却引用无关文档；也可能忠实复述错误证据。分别测答案正确性、证据事实质量、引用覆盖和归属，才能定位是检索、来源还是生成出了问题。

## 质量延迟与成本影响

主张拆分和蕴含核验增加模型或人工成本，精细引用也占用 Token。高风险回答做主张级检查，低风险摘要可按段落引用。短 ID 比长 URL 节省 Token，并降低模型篡改链接的机会。

## 数据评测与安全风险

评测集应包含部分支持、矛盾、多来源、不可回答、失效链接和越权来源。用户点击引用时必须再次授权，不能因为答案中出现 ID 就绕过权限。证据 URL 若含签名应短期生成，不写入长期模型上下文或日志。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 引用 ID 不存在 | 模型自由生成标识 | 允许 ID 集、结构校验 |
| 链接能开但不支持 | 只验证有效性 | 主张证据蕴含、人工抽样 |
| 关键数字没有引用 | 主张拆分或覆盖不足 | 数值规则、Coverage |
| 打开文档找不到片段 | Chunk 缺原始位置 | 页码、区域、字符偏移 |
| 用户可打开越权来源 | 点击时未重新授权 | 资源权限、短期链接 |

## 适用与不适用场景

事实问答、研究、合规和企业知识助手应提供可核验引用。创意写作不一定需要引用，但若混入事实主张仍应标明来源。引用不能修复低质量来源，只能暴露证据链。

## 学习收益

你应能区分引用有效性、归属和覆盖，计算两个核心指标，设计不可伪造的证据 ID，并将 Chunk 映射回原文。

## 给别人讲清楚

“引用不是答案末尾放几个链接，而是给每个需要核验的说法配一张可打开、确实支持它的证据卡。”

## 自检问题

1. 为什么答案正确不代表引用正确？
2. 多贴引用会怎样影响覆盖率和归属正确率？
3. 用户点击引用时为什么仍要重新鉴权？

## 相关主题

- [RAG 上下文构建](35-RAG 上下文构建.md)
- [RAG 生成评测](38-RAG 生成评测.md)
- [父子文档检索](12-父子文档检索.md)

## 资料来源

- Ori Ram 等, [In-Context Retrieval-Augmented Language Models](https://arxiv.org/abs/2302.00083), 2023，访问日期：2026-09-10。
- Tianyu Gao 等, [Enabling Large Language Models to Generate Text with Citations](https://arxiv.org/abs/2305.14627), 2023，访问日期：2026-09-10。
- Akari Asai 等, [Self-RAG](https://arxiv.org/abs/2310.11511), 2023，访问日期：2026-09-10。
