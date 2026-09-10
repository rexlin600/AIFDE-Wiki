---
type: concept
domain:
  - RAG
depth: L4
importance: extension
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - Self-RAG
tags:
  - self-rag
  - reflection-token
---

# Self-RAG 自反思检索

<!-- markdownlint-disable MD013 -->

## 它解决什么 RAG 问题

固定 RAG 总会检索且不会检查证据是否支持回答。Self-RAG 让模型学习离散反思标签：是否需要检索、文档是否相关、回答是否受支持以及回答是否有用。研究助手因此可以跳过常识寒暄，并在引用不能支持主张时拒绝输出。

“模型自评”不是事实裁判；标签也会预测错误。先做静态检索加主张支持度评测，只有检索时机和证据使用仍是主要错误才考虑 Self-RAG。

## 链路位置与反思状态

它把控制信号插入生成链路：`查询 → RETRIEVE → 证据 → RELEVANT → 生成 → SUPPORTED → USEFUL`。这些是离散标签，不是普通自然语言理由。可为候选输出 $y$ 定义：

$$
S(y)=\lambda_s\log P(y\mid x,d)+\lambda_rR+\lambda_eE+\lambda_uU
$$

$R,E,U$ 分别是相关、支持、有用标签的概率或映射分数；$\lambda$ 是验证集上确定的权重。若最低支持阈值未达到，必须补检或拒答，不能用“有用”抵消“不受支持”。

状态为 `(动作, 证据, 草稿, 步数, 剩余预算, 终止原因)`。即使原论文可在生成中多次控制，生产实现也必须限定最多 $m$ 次检索。

## 最小手算

两个答案的生成对数分数分别为 -0.4 和 -0.2，支持度为 0.9 和 0.3。令 $\lambda_s=1,\lambda_e=1$，得 0.5 和 0.1，第一个总体更好。若支持硬阈值为 0.5，第二个应直接淘汰，而不是靠流畅度胜出。

## 可执行实验

```python
def decide(need_retrieval, relevance, support, useful,
           step=0, max_steps=2):
    if not need_retrieval:
        return "answer_without_retrieval", "not_needed"
    if relevance < 0.5:
        return (("abstain", "max_steps") if step >= max_steps
                else ("retrieve_again", "irrelevant"))
    if support < 0.6:
        return (("abstain", "max_steps") if step >= max_steps
                else ("retrieve_again", "unsupported"))
    if useful < 0.5:
        return "revise", "not_useful"
    return "answer", "supported"

assert decide(False, 0, 0, 0)[1] == "not_needed"
assert decide(True, 0.9, 0.4, 0.9)[0] == "retrieve_again"
assert decide(True, 0.9, 0.9, 0.8)[0] == "answer"
assert decide(True, 0.1, 0.1, 0.1, step=2)[1] == "max_steps"
assert decide(True, 0.9, 0.9, 0.8, step=2)[0] == "answer"
print("reflection branches passed")
```

`step` 表示当前证据产生前已经使用的检索次数；充分证据优先接受，只有准备再次检索时才检查预算。实验只展示标签怎样控制分支和预算，并未训练反思 Token，也未证明自评分数准确。

## 质量延迟成本与风险

反思可提高证据使用的可控性，却增加训练数据、推理标签和可能的重复检索成本。报告各标签准确率、支持度、拒答率、平均检索数、Token 数与延迟；和普通 RAG 做相同检索器下的消融。

反思不能替代权限、来源白名单和人工高风险规则。恶意文档可能诱导“相关”判断；标签训练数据也可能包含偏见或评测答案。日志应记录标签和来源 ID，敏感正文最小化保存。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 总判断证据受支持 | 支持标签训练失衡 | 标签混淆矩阵与反例 |
| 频繁重复检索 | 相关或支持阈值失准 | 标签轨迹与最大步数 |
| 有证据却大量拒答 | 硬阈值过高 | 校准曲线与风险切片 |
| 自评好但人工评差 | 自评器与生成器共偏差 | 独立评审与外部证据 |

## 适用边界与学习收益

适合已有高质量反思标注、确需细粒度控制的研究或高价值系统；普通知识库问答若简单支持度检查已足够，不应先上 Self-RAG。学完应能区分生成分数、反思标签和硬安全约束。

复述：Self-RAG 像边写边打四种检查标记，但自己检查自己仍会看漏，所以还需要预算、权限和独立评测。

自检：支持度为何适合硬门槛？标签概率为何不是证据？Self-RAG 与普通纠错检索的控制粒度有何不同？

## 相关主题

- [RAG 自适应检索](<20-RAG 自适应检索.md>)
- [RAG 纠错检索](<22-RAG 纠错检索.md>)
- [RAG 引用生成](<36-RAG 引用生成.md>)

## 资料来源

- Akari Asai 等, [Self-RAG](https://arxiv.org/abs/2310.11511), 2023，访问日期：2026-09-10。
- Shi-Qi Yan 等, [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884), 2024，访问日期：2026-09-10。
