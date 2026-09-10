---
type: concept
domain:
  - RAG
depth: L3
importance: extension
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Corrective RAG
tags:
  - corrective-rag
  - retrieval-quality
---

# RAG 纠错检索

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

检索成功返回不等于证据可用：结果可能无关、过期或互相冲突。合规问答若在内部制度库只找到旧规定，应判断质量后补检权威源、换查询或明确拒答，而不是把低质量文本交给生成器。

简单基线是单次检索后直接生成。只有离线错误分析表明低质量召回是主要瓶颈，纠错分支才值得其额外延迟；它不能修复源数据本身不存在的事实。

## 链路位置与状态机

链路为 `初检 → 证据评估 → 接受或改写补检或换源 → 合并 → 生成或拒答`。令相关度、时效性和来源可信度分别为 $r,f,a\in[0,1]$，简单质量分为：

$$
Q=w_rr+w_ff+w_aa,\qquad w_r+w_f+w_a=1
$$

当 $Q\ge\tau_h$ 接受；$\tau_l\le Q<\tau_h$ 补检；$Q<\tau_l$ 换获权的权威源。该线性分数只是可解释基线，不代表三者真正可互相补偿。状态必须记录尝试次数、已查源、剩余预算和终止原因。

最多尝试 $m$ 次、每次至多耗时 $L_e+L_r$ 时，串行延迟上界是 $m(L_e+L_r)$。达到预算后只能用已有充分证据回答，否则拒答。

## 最小手算

取权重 `[0.5, 0.3, 0.2]`，高低阈值为 0.75 和 0.45。结果的相关度 0.8、时效 0.2、权威性 0.5，则 $Q=0.5\times0.8+0.3\times0.2+0.2\times0.5=0.56$，进入补检，而非直接接受。

## 可执行实验

```python
def quality(item):
    return 0.5 * item["relevance"] + 0.3 * item["freshness"] + 0.2 * item["authority"]

def corrective(results_by_source, allowed_sources, max_attempts=3,
               low=0.45, high=0.75):
    trace = []
    source = "internal" if "internal" in allowed_sources else "official"
    while len(trace) < max_attempts and source:
        if source not in allowed_sources:
            source = "official" if source != "official" else None
            continue
        items = results_by_source.get(source, [])
        best = max((quality(x) for x in items), default=0.0)
        if best >= high:
            trace.append((source, best, "accept"))
            return source, "accepted", trace
        if best >= low:
            trace.append((source, best, "supplement"))
            source = "supplement"
        else:
            trace.append((source, best, "switch_source"))
            source = "official"
    reason = "max_attempts" if len(trace) >= max_attempts else "insufficient_evidence"
    return None, reason, trace

data = {
    "internal": [{"relevance": 0.8, "freshness": 0.2, "authority": 0.5}],
    "supplement": [{"relevance": 0.9, "freshness": 0.8, "authority": 0.8}],
    "official": [{"relevance": 0.9, "freshness": 1.0, "authority": 1.0}],
}
source, reason, trace = corrective(data, {"internal", "supplement", "official"})
assert source == "supplement" and reason == "accepted" and len(trace) == 2
assert trace[0][2] == "supplement"
assert corrective(data, {"internal"})[0] is None
assert corrective(data, {"official"})[0] == "official"
assert corrective(data, {"internal"}, max_attempts=1)[1] == "max_attempts"
low_data = {**data, "internal": [
    {"relevance": 0.1, "freshness": 0.1, "authority": 0.1}]}
assert corrective(low_data, {"internal", "official"})[0] == "official"
print(reason, trace)
```

实验分别验证中分补检、低分换源、高分接受、来源白名单和预算分支。人工设定的分数不是业务评测结果；真实质量评估器必须用独立标注集校准并监测误拒和误收。

## 质量延迟成本与风险

纠错能减少无依据回答，但可能因评估器偏差丢弃正确证据。报告初检接受率、纠错成功率、拒答率、支持度、额外查询数、P95 延迟和成本。应消融“无纠错”“只补检”“允许换源”。

换源必须来自授权白名单；禁止让检索文本指定新 URL 或凭据。冲突版本要保留时间与来源，不可静默拼接。评测集要封存，来源更新后重新核验，日志避免记录敏感正文。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 好证据被大量拒绝 | 阈值过高或评估器漂移 | 分数校准与误拒样本 |
| 换源后仍是旧内容 | 时效字段缺失 | 来源版本与生效时间 |
| 反复查询同一来源 | 已查源未进入状态 | 检索轨迹与预算计数 |
| 出现未授权来源 | 文本驱动了换源 | 数据源白名单与权限日志 |

## 适用边界与学习收益

适合来源质量不稳定且有可用备选权威源的系统；数据唯一、低延迟要求极严或基线质量稳定时不适合。学完应能计算质量分、画出纠错状态机并解释拒答边界。

复述：纠错检索像验货，先检查相关、是否过期和来源；不合格才补货或换供应商，次数用尽仍不合格就不交付。

自检：为什么相关但过期的材料不能直接用？质量分的权重如何校准？为什么换源不是越多越好？

## 相关主题

- [RAG 知识时效](<33-RAG 知识时效.md>)
- [RAG 迭代检索](<21-RAG 迭代检索.md>)
- [RAG 生成评测](<38-RAG 生成评测.md>)

## 资料来源

- Shi-Qi Yan 等, [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884), 2024，访问日期：2026-09-10。
- Patrick Lewis 等, [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401), 2020，访问日期：2026-09-10。
