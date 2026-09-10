---
type: concept
domain:
  - LLM
depth: L2
importance: common
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - SFT
  - 指令微调
tags:
  - llm
  - supervised-fine-tuning
  - alignment
---

# 大模型监督微调 SFT

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

预训练模型擅长续写，却不一定理解“用户提问、助手回答”的交互协议。监督微调 SFT 用高质量指令与示范回答继续训练，让模型学会遵循角色、输出格式、语气和领域任务。

SFT 可以教行为模式，不能凭空补全可靠知识。事实经常变化时，先比较 Prompt、RAG 或工具；只有行为稳定且示例充足时，微调才值得承担训练和维护成本。

## 不理解会造成什么错误

- 训练模板与推理模板不同，模型看到陌生的角色边界。
- 对系统和用户 Token 也计算回答损失，浪费容量复述问题。
- 把评测答案或近重复样本放入训练集，制造虚假提升。
- 用少量单一任务数据高学习率训练，造成灾难性遗忘。
- 只检查平均损失，不检查安全拒答、格式和原有能力回退。

## 它在 LLM 链路中的位置

```text
预训练模型 → 消息模板 → Token 与 label mask
→ 自回归交叉熵 → 验证与检查点选择
→ 独立能力安全评测 → 同版模板推理
```

SFT 延续[大模型预训练目标](03-大模型预训练目标.md)的下一 Token 损失，但训练样本从普通文本变成了“指令—回答”示范。

## 从客服工单抽取开始

目标是把客服消息转成固定 JSON。输入是系统规则与用户工单，回答是合法 JSON。主要指标是字段准确率、JSON 合法率和拒答正确率，高成本错误是伪造订单状态或泄露隐私。

简单基线是固定 Prompt 加结构化输出约束。如果基线已稳定满足指标，就没有必要用 SFT 固化行为。

## 消息模板是模型协议

```text
<system>只输出 JSON</system>
<user>订单 A 延迟三天</user>
<assistant>{"issue":"delay","days":3}</assistant>
```

真实模板还可能包含 BOS、EOS、工具消息和轮次分隔符。它们不是装饰：Token ID、位置和结束标记都会参与条件概率。训练、验证和推理必须使用同一个已版本化模板。

多轮数据要明确每个 assistant 回答是否计损失。若训练所有助手轮次，也必须屏蔽系统、用户、工具结果和 Padding。

## Label Mask 如何工作

完整序列为 $x_1,\ldots,x_T$，回答位置指示量为 $m_t\in\{0,1\}$：

$$
L_{\mathrm{SFT}}
=-\frac{\sum_{t=1}^{T}m_t\log p_\theta(x_t\mid x_{<t})}
{\sum_{t=1}^{T}m_t}
$$

分母使用有效回答 Token 数，避免 Padding 和回答长度改变损失尺度。实现中常把不计损失的位置标签设为 `-100`，交叉熵据此忽略它们。

某位置 Logits 为 $z$，则 $p_c=e^{z_c}/\sum_j e^{z_j}$，真实类别 $y$ 的损失为 $-\log p_y$。Mask 为 0 时，该位置不进入总损失。

## 最小手算

四个预测位置中只有最后两个属于回答，正确 Token 概率为 0.5 和 0.25：

$$
L=-\frac{\log0.5+\log0.25}{2}\approx1.040
$$

若错误地把两个概率均为 0.99 的 Prompt 位置也计入，平均损失约降至 0.525。漂亮数字主要来自复制已知输入，不表示回答更好。

## 可执行 Label Mask 实验

```python
import numpy as np

np.random.seed(43)
logits = np.array([
    [5.0, 0.0, 0.0],
    [0.0, 5.0, 0.0],
    [0.0, 0.4, 1.2],
    [0.6, 0.0, 0.2],
])
labels = np.array([0, 1, 2, 0])
answer_mask = np.array([False, False, True, True])

stable = logits - logits.max(axis=1, keepdims=True)
probability = np.exp(stable) / np.exp(stable).sum(axis=1, keepdims=True)
token_loss = -np.log(probability[np.arange(4), labels])
masked_loss = token_loss[answer_mask].mean()
all_token_loss = token_loss.mean()
assert answer_mask.sum() == 2
assert np.isclose(masked_loss, token_loss[2:].mean())
assert all_token_loss < masked_loss

changed = probability.copy()
changed[:2] = 1 / 3
changed_loss = -np.log(changed[np.arange(4), labels])[answer_mask].mean()
assert np.isclose(changed_loss, masked_loss)
print("answer-only/all-token:", round(masked_loss, 4), round(all_token_loss, 4))
```

## 实验结果解释

Prompt 位置的高置信预测会人为拉低全序列损失，回答 Mask 能隔离这种影响。实验没有证明模板或数据正确；仍要解码实际输出并做任务、安全和回归评测。

## 数据构造与污染控制

训练样本应记录来源、许可、语言、领域、模板版本和去重版本。先按用户、文档、会话或来源聚组，再做精确与近重复检测，将同组及其改写放入同一集合，冻结测试集后才做模板化和增强。

公开基准答案、内部验收题及其改写不能进入训练。仅按字符串去重会漏掉翻译、摘要和参数替换版本。污染检测也要版本化。

## 灾难性遗忘

数据过窄、学习率过高或训练过久时，领域任务提升可能伴随通用推理、多语言或安全能力下降。可降低学习率、缩短训练、混入治理后的通用示例或使用 LoRA，但最终仍要运行冻结的能力回归集。

训练损失最低的检查点未必最好。应按目标任务、格式、安全和通用能力组成的验证矩阵选择，而不是继续查看测试集。

## 质量成本与延迟影响

全参数 SFT 要保存参数、梯度和优化器状态，显存远高于推理。被 Mask 的长 Prompt 仍需前向计算。SFT 通常不改变推理参数量，但输出更短或更稳定时可能间接降低成本。

## 数据评测与安全风险

- 示范可能包含个人信息、错误事实、偏见和越权操作。
- 安全拒答与正常帮助要同时覆盖，防止“一律拒绝”。
- 格式正确不等于事实正确，应分别评测。
- 训练前后都要做隐私抽取、危险能力和提示注入回归。
- 合成数据需标注来源，避免错误循环放大。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 损失异常低但回答差 | Prompt Token 进入标签 | 打印 Token、label 与 Mask |
| 模型不停生成 | EOS 未进标签或模板错配 | 结束 Token、截断、模板版本 |
| JSON 忽好忽坏 | 示例格式不一致 | 规范化数据、字段级评测 |
| 通用能力下降 | 数据过窄或训练过度 | 回归集、学习率、轮数 |
| 离线指标异常高 | 评测污染或近重复泄漏 | 来源分组、近重复、时间切分 |
| 恢复后曲线跳变 | 只恢复模型参数 | 优化器、步数、调度器、随机状态 |

## 适用与不适用场景

SFT 适合需要稳定角色、格式、语气或领域操作模式，且有高质量示范的场景。知识频繁更新时优先 RAG；需要实时事实或执行动作时优先工具；少量约束先尝试 Prompt；没有可信评测集时不应急于微调。

## 学习收益

你应能把消息变成训练序列，解释为什么只对回答 Token 计损失，识别模板错配与污染，并设计覆盖目标能力和遗忘风险的验证矩阵。

## 给别人讲清楚

“SFT 像给已经会语言的模型看标准答卷。模板告诉它谁在说话，Label Mask 告诉它只为助手回答负责。答卷若泄题或范围太窄，模型会学得很快，却学错方向。”

## 自检问题

1. 为什么被 Mask 的 Prompt 仍会消耗计算？
2. 训练与推理模板差一个结束标记会怎样？
3. 为什么训练损失下降不能排除评测污染？
4. 怎样区分格式能力与事实能力提升？

## 相关主题

- [大模型预训练目标](03-大模型预训练目标.md)
- [LoRA 参数高效微调](<12-LoRA 参数高效微调.md>)
- [RLHF 与 DPO](<17-RLHF 与 DPO.md>)
- [数据泄漏](../H-机器学习/05-数据泄漏.md)

## 资料来源

- Long Ouyang 等, [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155), 2022，访问日期：2026-09-10。
- Hugging Face, [Chat templates](https://huggingface.co/docs/transformers/chat_templating)，访问日期：2026-09-10。
- Hugging Face TRL, [SFT Trainer](https://huggingface.co/docs/trl/sft_trainer)，访问日期：2026-09-10。
