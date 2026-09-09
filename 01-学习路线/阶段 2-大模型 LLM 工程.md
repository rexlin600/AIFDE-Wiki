---
type: moc
domain:
  - Roadmap
  - LLM
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 阶段 2 LLM 工程
tags:
  - core
  - roadmap
---

# 阶段 2：LLM 工程

## 建议周期与进入条件

**建议周期：6～8 周，每周 5～10 小时。** 时间是建议，达到退出证据比完成阅读清单重要。

进入条件是理解训练/验证/测试、过拟合、损失、梯度、Embedding 和基本神经网络；能用 PyTorch 运行训练与推理，并能以固定数据集比较实验。

## 推荐深度与核心知识

Tokenizer、Prompt、结构化输出和模型评测达到 L3；Transformer、微调和推理机制至少达到 L2：

领域入口：[LLM](../05-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM/%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM-MOC.md)，必要时回到[深度学习](../04-%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0-MOC.md)补齐 Transformer、优化与 PyTorch 工程基础。

- Tokenizer、词表、特殊 Token、序列长度与中英文 Token 成本。
- Embedding、位置表示、Attention、Transformer Block 和自回归生成。
- 系统/用户消息、Prompt、Context Engineering、Few-shot 与失败边界。
- JSON Schema、Function Calling、校验、修复与受控重试。
- Temperature、top-p、停止条件、上下文窗口、KV Cache 和批处理。
- 模型 API、本地推理、量化、吞吐、首 Token 延迟与总成本。
- SFT、PEFT/LoRA 的目标与数据要求，以及 RAG、微调、长上下文之间的选择。

## 必做实验

围绕一个公开的信息抽取或分类任务，建立不少于 50 条的固定评测集，比较：

1. 两种 Tokenizer 对中英文与结构化输入的长度影响。
2. Zero-shot、Few-shot 与经过 Context Engineering 的 Prompt。
3. 自由文本、JSON 提示和受 Schema 约束的结构化输出。
4. 至少两个模型或一个模型的两个推理配置。
5. 基础模型与一个小型 LoRA 适配实验；资源不足时使用小模型，但必须记录数据切分和过拟合风险。

结果必须同时报告任务质量、Schema 合规率、拒答/幻觉样例、首 Token 延迟、总延迟、吞吐和估算成本。

## 外部 GitHub 项目

- [Transformers](https://github.com/huggingface/transformers)：研究 Tokenizer 到 `generate` 的公开调用链。
- [PEFT](https://github.com/huggingface/peft)：运行并理解 LoRA 适配器注入、保存和加载。
- [vLLM](https://github.com/vllm-project/vllm)：观察模型加载、调度、批处理与 OpenAI 兼容服务。

## 开源实践：使用、源码跟踪、最小复刻、可选贡献

- **开源使用：** 固定模型、Tokenizer、Transformers/PEFT/vLLM 版本，跑通生成、LoRA 或推理服务中的至少两项。
- **源码跟踪：** 从 `generate` 或兼容 API 入口跟踪到 Tokenization、采样或调度中的一条核心调用链。
- **最小复刻：** 用 PyTorch 实现单头 Causal Self-Attention 和逐 Token 贪心生成，以形状断言和小输入测试机制。
- **可选贡献：** 对可复现的模型兼容、错误消息或文档样例问题提供测试或文档修正。

## 项目增量

创建独立仓库 `llm-engineering-lab`，包含统一模型适配器、结构化输出校验、评测集、Prompt 版本、成本/延迟记录、本地推理脚本和 LoRA 实验。模型权重和受限数据不进入 Git；README 说明下载、许可和硬件要求。

## 评测与复盘

对每项实验保存模型与 Prompt 版本、采样参数和失败样例。复盘质量、稳定性、延迟、成本、隐私和运维之间的取舍，并写出选择 Prompt、RAG、微调或更换模型的决策表。

## 面试训练

- 从输入到下一个 Token 解释 Transformer 推理路径和 KV Cache 的价值。
- 解释 Embedding 与生成模型输出的区别，以及 Tokenizer 为什么影响成本和质量。
- 设计可靠的结构化输出链路，处理 Schema 失败、超时和模型降级。
- 比较 Prompt、RAG、LoRA 与全量微调的适用条件。
- 使用实验数据答辩一次模型选型，而不是用排行榜或供应商品牌作结论。

## 退出证据

- `llm-engineering-lab` 的固定版本、公开评测集、自动测试与复现命令。
- 五组必做对比及质量、合规、延迟、吞吐和成本报告。
- 一个可测试的 Attention/生成最小复刻和一份关键源码调用链记录。
- 一个 LoRA 适配器及训练/验证曲线，或有数据支持的“不应微调”决策记录。
- 能在面试中解释机制、工程边界、模型选择与失败处理。

证据齐全后进入 [阶段 3：RAG 工程](%E9%98%B6%E6%AE%B5%203-RAG%20%E5%B7%A5%E7%A8%8B.md)。
