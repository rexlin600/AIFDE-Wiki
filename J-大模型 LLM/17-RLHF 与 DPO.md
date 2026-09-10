---
type: concept
domain:
  - LLM
depth: L3
importance: extension
maturity: draft
created: 2026-09-10
updated: 2026-09-10
last_verified: 2026-09-10
aliases:
  - 大模型偏好对齐
tags:
  - rlhf
  - dpo
---

# RLHF 与 DPO

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么 LLM 问题

同一个问题可能有多个事实正确的回答，但人更偏好其中一个：更有帮助、更简洁、语气更合适或更安全。RLHF 与 DPO 用成对偏好数据塑造这种行为。它们优化“更喜欢哪个回答”，不负责把变化频繁的事实写进模型。

## 不理解会造成什么错误

- 把标注者偏好当成客观真理。
- 只提高奖励分，不检查事实性和任务能力是否下降。
- 忘记参考模型约束，策略偏离到不自然区域。
- 偏好对只差长度，模型最终学会“越长越好”。
- 用偏好训练解决知识过期，本应使用 RAG 或工具。

## 它在 LLM 链路中的位置

通常先预训练，再用 SFT 学会指令格式，之后收集同一提示下的胜者回答 $y_w$ 和败者回答 $y_l$。经典 RLHF 训练奖励模型并用强化学习优化策略；DPO 直接用偏好对更新策略。最终仍需独立事实、安全和业务评测。

## RLHF 流程

1. SFT 模型对提示生成多个候选。
2. 标注者比较候选，形成偏好对。
3. 奖励模型学习 $r(x,y_w)>r(x,y_l)$。
4. 策略在提高奖励的同时，通过 KL 惩罚靠近参考模型。

一个概念目标是：

$$
\max_\pi\ \mathbb{E}_{y\sim\pi(\cdot|x)}[r(x,y)]
-\beta D_{KL}(\pi(\cdot|x)\Vert\pi_{ref}(\cdot|x))
$$

$\beta$ 越大，越不允许策略远离参考模型。奖励模型只是人类偏好的近似，策略可能寻找其漏洞，这就是奖励投机。

## DPO 从偏好概率开始

DPO 不显式训练奖励模型。对同一提示，定义策略相对参考模型对胜者和败者的优势差：

$$
z=\beta\left[
(\log\pi_\theta(y_w|x)-\log\pi_{ref}(y_w|x))
-(\log\pi_\theta(y_l|x)-\log\pi_{ref}(y_l|x))
\right]
$$

损失为：

$$
L_{DPO}=-\log\sigma(z)
$$

当策略相对参考模型更提升胜者概率时，$z$ 变大，$\sigma(z)$ 接近 1，损失变小。序列对数概率通常是各回答 Token 对数概率之和，并 Mask 掉提示 Token 和 Padding。

## 最小手算

设 $\beta=0.5$。当前策略的胜者和败者对数概率为 `-2`、`-3`，参考模型分别为 `-2.4`、`-2.6`。胜者相对优势是 0.4，败者是 -0.4，所以 $z=0.5\times(0.4-(-0.4))=0.4$。损失 $-\log\sigma(0.4)\approx0.513$，小于没有偏好优势时的 $-\log0.5\approx0.693$。

## 可执行实验

```python
import math

def dpo_loss(policy_w, policy_l, reference_w, reference_l, beta=0.5):
    advantage = (policy_w - reference_w) - (policy_l - reference_l)
    z = beta * advantage
    # 数值稳定的 -log(sigmoid(z))
    return math.log1p(math.exp(-z)), z

neutral, z0 = dpo_loss(-2.4, -2.6, -2.4, -2.6)
preferred, z1 = dpo_loss(-2.0, -3.0, -2.4, -2.6)
reversed_loss, z2 = dpo_loss(-3.0, -2.0, -2.4, -2.6)
print("neutral", round(neutral, 3), "preferred", round(preferred, 3),
      "reversed", round(reversed_loss, 3))
assert math.isclose(neutral, math.log(2), rel_tol=1e-9)
assert z1 > z0 > z2
assert preferred < neutral < reversed_loss
```

实验验证损失方向，不代表训练已经安全。真实训练还受回答长度归一化、标签噪声、批次组成和优化超参数影响。

## 数据怎样设计

每一对回答应针对同一提示，并标明偏好理由和无法判断的情况。控制长度、风格与事实性的混杂；让标注者看到相同证据；用重复样本估计一致性。记录标注群体和指南版本，因为“更好”可能因用户、地区和场景不同。

## DPO 与 RLHF 怎样选择

DPO 流程较短、训练稳定性通常更易管理，适合已有高质量离线偏好对。RLHF 能让策略在线探索并利用单独奖励模型，但系统复杂、计算和调参成本更高。二者都不能消除奖励偏差；选择依据应是数据、探索需求、团队能力和固定评测，而非算法名称。

## 实验结果怎样解释

同时报告胜率、事实性、拒答、帮助性、长度、风格和原有能力。评审应盲化模型身份和回答顺序，并报告平局与评审一致性。若胜率提升只来自更长或更讨好，说明指标被钻了空子。

## 质量延迟与成本影响

偏好训练不一定改变推理架构，但可能让答案变长，从而增加延迟和费用。RLHF 需要生成、奖励模型和策略训练；DPO 需要策略与参考模型的对数概率。可预计算参考概率节省训练计算，但必须绑定 Tokenizer、模板和模型版本。

## 数据评测与安全风险

偏好数据可能包含敏感提示、有害回答和标注者偏见。最小化收集、脱敏、限制访问，并保护标注者。安全偏好会产生过度拒答风险，必须按语言、群体和任务切片。模型自评不能完全替代人类与确定性检查。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| DPO 损失方向反了 | winner 和 loser 颠倒 | 一对样本手算、字段映射 |
| 回答越来越长 | 长度成为偏好捷径 | 长度切片、配对控制、长度正则 |
| 通用能力下降 | 偏好过强或数据过窄 | beta、参考模型、能力回归集 |
| 训练好但人评无提升 | 奖励或偏好标签错配 | 指南、一致性、盲评 |
| 拒答显著增多 | 安全偏好失衡 | 可回答样本、过度拒答指标 |
| 结果无法复现 | 模板或参考概率不一致 | Tokenizer、chat template、版本 |

## 适用与不适用场景

适用于正确答案不唯一、但可稳定比较帮助性、风格和安全性的任务。不适用于更新事实知识、纠正确定性业务规则或缺乏可靠偏好数据的场景。少量明确示范通常先做 SFT。

## 学习收益

你应能解释 RLHF 四阶段、KL 约束、DPO 的相对对数概率，手算偏好损失，并识别长度偏差与奖励投机。

## 给别人讲清楚

“SFT 教模型照示范回答，偏好对齐让模型在两个都像答案的输出中更偏向人喜欢的那个。参考模型像安全绳，防止为了追分走得太远。”

## 自检问题

1. DPO 为什么要比较策略相对参考模型的变化？
2. 偏好胜率提高为什么不一定意味着事实性提高？
3. 怎样检查模型是否只学会生成更长回答？

## 相关主题

- [大模型监督微调 SFT](<11-大模型监督微调 SFT.md>)
- [LoRA 参数高效微调](<12-LoRA 参数高效微调.md>)
- [大模型幻觉](09-大模型幻觉.md)

## 资料来源

- Paul F. Christiano 等, [Deep Reinforcement Learning from Human Preferences](https://arxiv.org/abs/1706.03741), 2017，访问日期：2026-09-10。
- Long Ouyang 等, [Training Language Models to Follow Instructions with Human Feedback](https://arxiv.org/abs/2203.02155), 2022，访问日期：2026-09-10。
- Rafael Rafailov 等, [Direct Preference Optimization](https://arxiv.org/abs/2305.18290), 2023，访问日期：2026-09-10。

