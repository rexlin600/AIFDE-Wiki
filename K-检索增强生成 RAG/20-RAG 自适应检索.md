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
  - Adaptive RAG
tags:
  - adaptive-rag
  - retrieval-routing
---

# RAG 自适应检索

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

固定检索会给“你好”增加无用延迟，也可能让“比较两版制度差异”只检索一次而缺证。自适应检索先判断问题需要多少检索：不检索、单次检索或深检索。客服机器人可直接回答寒暄，查询退款规则时检索一次，比较跨年度政策时进入多步流程。

不理解它，容易把分类置信度当事实、让敏感问题绕过权威数据源，或让深检索无限循环。**只有静态单次检索在分层评测中确实不足，才值得增加路由器。**

## 链路位置与简单基线

它位于查询理解之后、检索器之前：`查询 → 路径判定 → 无检索或单次或深检索 → 上下文`。简单基线是所有问题都执行一次混合检索；先测基线的正确率、空召回率和延迟。

输入是查询及允许的数据源，输出是离散动作 $a\in\{N,S,D\}$、置信度和预算。$N$ 表示不检索，$S$ 表示单次，$D$ 表示最多 $m$ 次深检索。

## 判定机制与公式

设路由器给出三个概率 $p_N,p_S,p_D$，总和为 1。最简单决策是：

$$
a=\arg\max_{c\in\{N,S,D\}}p_c
$$

但高风险问题不能只看最大值。可先用规则把“账户余额”等问题限制到授权数据源；若最大概率低于阈值 $\tau$，回退到一次安全检索。一次请求的查询数上界为：

$$
Q_{\max}=\begin{cases}0&a=N\\1&a=S\\m&a=D\end{cases}
$$

若每次检索最多耗时 $L_r$，路由耗时 $L_g$，则忽略并行时延迟上界约为 $L_g+Q_{\max}L_r$。这让“深检索”成为有预算的工程动作。

## 最小手算

阈值 $\tau=0.6$。寒暄的概率为 `[0.8, 0.15, 0.05]`，选择不检索；制度查询为 `[0.1, 0.7, 0.2]`，检索一次；比较题为 `[0.1, 0.2, 0.7]`，最多检索 3 次。若概率 `[0.35, 0.34, 0.31]`，最大值低于阈值，应回退到安全的单次检索，而不是自信地跳过检索。

## 可执行实验

```python
PATHS = ("none", "single", "deep")

def route(probs, high_risk=False, threshold=0.6, max_steps=3):
    assert len(probs) == 3 and abs(sum(probs) - 1.0) < 1e-9
    if high_risk:
        return {"path": "single", "max_queries": 1, "reason": "risk_guard"}
    best = max(range(3), key=lambda i: probs[i])
    if probs[best] < threshold:
        return {"path": "single", "max_queries": 1, "reason": "low_confidence"}
    path = PATHS[best]
    budget = {"none": 0, "single": 1, "deep": max_steps}[path]
    return {"path": path, "max_queries": budget, "reason": "classified"}

assert route([0.8, 0.15, 0.05])["max_queries"] == 0
assert route([0.1, 0.2, 0.7], max_steps=3)["max_queries"] == 3
assert route([0.35, 0.34, 0.31])["reason"] == "low_confidence"
assert route([0.9, 0.05, 0.05], high_risk=True)["path"] == "single"
print("adaptive routing checks passed")
```

实验只验证路径、风险回退和查询预算，不证明这些模拟概率能代表真实分类器。真实系统需用标注查询按意图、风险和语言切片评测。

## 质量延迟成本与风险

自适应检索可减少简单问题的延迟与费用，并为复杂问题增加召回机会；错误地选择 $N$ 会直接失去证据，错误地选择 $D$ 会放大噪声和成本。报告各路径占比、路由混淆矩阵、端到端正确率、P95 延迟和平均查询数。

权限检查不能由路由器取消；查询和检索文档都可能含提示注入，路径判定不得赋予文本更高权限。保留模型、规则、索引和数据版本，防止评测污染掩盖漂移。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 事实题经常直接回答 | 不检索类别过宽 | 路由混淆矩阵与风险规则 |
| 深检索占比异常高 | 阈值或训练分布漂移 | 路径分布与近期查询切片 |
| 延迟偶发失控 | 深检索预算未生效 | 最大步数与超时日志 |
| 敏感问题绕过数据源 | 把授权交给分类器 | 检索前权限强制点 |

## 适用边界与学习收益

它适合查询复杂度差异大、静态基线浪费明显的系统；低流量、查询同质或一次检索已足够时不适合。学完后应能解释三条路径、置信回退和延迟上界。

复述：自适应检索像分诊，先决定不查、查一次还是深入查；分诊会犯错，所以高风险规则和预算不能省。

自检：为什么低置信度不应默认不检索？$m$ 增大时质量、延迟和噪声怎样变化？授权为何不能由路由概率决定？

## 相关主题

- [RAG 迭代检索](<21-RAG 迭代检索.md>)
- [RAG 检索路由](<16-RAG 检索路由.md>)
- [RAG 检索评测](<37-RAG 检索评测.md>)

## 资料来源

- Soyeong Jeong 等, [Adaptive-RAG](https://arxiv.org/abs/2403.14403), 2024，访问日期：2026-09-10。
- Akari Asai 等, [Self-RAG](https://arxiv.org/abs/2310.11511), 2023，访问日期：2026-09-10。
