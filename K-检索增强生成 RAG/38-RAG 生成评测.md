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
  - RAG 回答评测
tags:
  - generation-evaluation
  - faithfulness
---

# RAG 生成评测

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 RAG 问题

RAG 生成评测判断答案是否完成用户任务、是否由给定证据支持、引用是否正确，以及证据不足时能否拒答。它避免把“文字流畅”或“与参考答案相似”误当成可靠回答。

## 不理解会造成什么错误

- 答案和参考文本措辞不同就判错，忽略语义等价。
- 答案事实正确就认为 RAG 成功，实际可能没有使用检索证据。
- 忠实复述错误证据就给高分，忽略来源真实性。
- 只测可回答问题，系统学会遇事强答。
- 让同一个模型生成答案又无校准地给自己打分。

## 它在 RAG 链路中的位置

检索评测先确认候选是否包含证据；生成评测固定检索结果，检查答案正确性、Faithfulness、引用与拒答；端到端评测再让完整链路运行。三层分开后，才能定位检索和生成各自贡献。

## 简单基线

可抽取问题先用规则从证据中返回原句；若生成模型没有显著改善可读性或任务成功，不必承担额外幻觉风险。开放问答使用人工评分规范和最小关键词规则作基线。

## 四个独立维度

- 答案正确性：相对于权威事实或参考标准是否正确。
- Faithfulness：答案主张是否被本次给定证据支持。
- 引用质量：引用是否有效、归属正确且覆盖关键主张。
- 拒答质量：证据不足时拒答，证据充分时不应过度拒答。

正确性与 Faithfulness 可以组合成四格：答案可能正确但无证据支持，也可能忠实于错误证据但事实错误。因此不能只保留一个总分。

## 主张级 Faithfulness

把答案拆成 $m$ 个可核验主张，$f_i=1$ 表示证据蕴含主张 $i$：

$$
Faithfulness=\frac{\sum_{i=1}^{m}f_i}{m},\qquad m>0
$$

当 $m=0$ 时 Faithfulness 没有定义，应报告 N/A，并用完整性、任务成功与过度拒答指标评价空答案。不能把“没有主张可犯错”记成高 Faithfulness。如果答案漏掉关键内容，也要单独测完整性或任务成功。

## 拒答指标

把“回答”视为正类：

$$
AnswerPrecision=\frac{\text{可回答且答对}}{\text{所有已回答}}
$$

$$
AnswerCoverage=\frac{\text{已回答}}{\text{全部问题}}
$$

提高拒答阈值通常提升已回答样本可靠性，却降低覆盖率。高风险任务给错误强答更高代价。

## 最小手算

一个答案含 4 个主张，3 个被证据支持，Faithfulness 为 $3/4=75\%$。10 个问题回答 6 个，其中 5 个可回答且正确，Answer Precision 为 $5/6\approx83.3\%$，Coverage 为 $6/10=60\%$。不能只报告其中一个数字。

## 可执行实验

```python
records = [
    {"answerable": True, "answered": True, "correct": True},
    {"answerable": True, "answered": True, "correct": True},
    {"answerable": True, "answered": False, "correct": False},
    {"answerable": False, "answered": True, "correct": False},
    {"answerable": False, "answered": False, "correct": False},
]

def refusal_metrics(rows):
    answered = [row for row in rows if row["answered"]]
    correct_answers = sum(row["answerable"] and row["correct"]
                          for row in answered)
    precision = correct_answers / len(answered) if answered else None
    coverage = len(answered) / len(rows) if rows else None
    correct_abstentions = sum(not row["answerable"] and not row["answered"]
                              for row in rows)
    return precision, coverage, correct_abstentions

precision, coverage, correct_abstentions = refusal_metrics(records)
print("answer precision", round(precision, 3),
      "coverage", coverage, "correct abstentions", correct_abstentions)
assert precision == 2 / 3
assert coverage == 3 / 5
assert correct_abstentions == 1
all_refused = [{"answerable": False, "answered": False, "correct": False}]
assert refusal_metrics(all_refused) == (None, 0.0, 1)
```

实验验证拒答统计口径，并将“全部拒答时的 Answer Precision”标为 N/A，避免除零。它不能评判自然语言语义，真实评测需要人工、规则或经过人工校准的评审模型。

## 自动评审怎样使用

精确字段、数值和引用 ID 优先用确定性程序。开放语义可用模型评审，但要提供清晰评分量表、随机交换答案顺序、隐藏模型身份，并在人工标注子集上测一致性。评审模型升级也属于评测版本变化。

## 端到端错误归因

保留查询、候选、最终上下文、答案和引用。若证据不在候选，是召回问题；候选中有但没进入上下文，是排序或预算问题；上下文有而答案违背，是生成问题；答案支持但事实错，是来源质量问题。

## 质量延迟与成本影响

主张拆分、引用核验和模型评审增加成本。开发集可全量自动评分加人工抽样，上线前对高风险切片做完整人工审查。线上监控使用可观测代理指标，但定期回到真实任务成功和人工质量。

## 数据评测与安全风险

评测集包含可回答、不可回答、矛盾证据、过期证据、越权诱饵和提示注入。参考答案记录来源与有效时间。敏感样本不发送到未经批准的评审服务；模型评审的 Prompt 与输出同样需要审计和防注入。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| Faithfulness 高但没帮助 | 答案过短或漏关键内容 | 完整性、任务成功、拒答 |
| 答案对但无依据 | 模型参数记忆 | 给定证据、主张支持、引用 |
| 自动分高人评低 | 评审量表或模型偏差 | 人工校准、顺序、切片 |
| 强答错误多 | 没有不可回答训练与评测 | 阈值、Answer Precision |
| 更新后分数不可比 | 评审器或数据版本变化 | 版本冻结、重跑基线 |

## 适用与不适用场景

所有生成式 RAG 都需要多维评测。纯检索产品可不测生成，但仍需任务成功。单个文本相似度适合措辞固定的窄任务，不能替代开放问答的事实与证据检查。

## 学习收益

你应能区分正确性、Faithfulness、引用和拒答，设计主张级评测，校准模型评审，并根据 Trace 定位端到端故障。

## 给别人讲清楚

“RAG 答案要过两场考试：它说得对不对，以及它是不是根据这次给的资料说的。还要考没有资料时会不会诚实停下。”

## 自检问题

1. 忠实于错误来源为什么仍可能事实错误？
2. 为什么 Faithfulness 高不代表答案完整？
3. 模型评审上线前怎样用人工标注校准？

## 相关主题

- [RAG 检索评测](37-RAG 检索评测.md)
- [RAG 引用生成](36-RAG 引用生成.md)
- [RAG 纠错检索](22-RAG 纠错检索.md)

## 资料来源

- Shahul Es 等, [RAGAS](https://aclanthology.org/2024.eacl-demo.16/), 2024，访问日期：2026-09-10。
- Akari Asai 等, [Self-RAG](https://arxiv.org/abs/2310.11511), 2023，访问日期：2026-09-10。
- Sewon Min 等, [FActScore](https://aclanthology.org/2023.emnlp-main.741/), 2023，访问日期：2026-09-10。
