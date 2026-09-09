---
type: moc
domain:
  - LLM
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 大语言模型
tags:
  - core
  - llm
---

# LLM MOC

## 领域边界

本领域覆盖大语言模型（Large Language Model，LLM）的文本表示、预训练、对齐与适配、生成推理、应用接口和模型服务选择。重点是从机制到可测工程链路；RAG 检索流程、Agent 编排和通用生产平台分别由相邻领域负责。

## 前置知识

- [深度学习](../04-%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0-MOC.md)中的 Attention、Transformer、优化与 PyTorch 工程。
- [机器学习](../03-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0-MOC.md)中的数据拆分、泛化、指标和错误分析。
- 能调用 HTTP API、处理 JSON Schema，并记录延迟与成本。

## 推荐顺序

1. 从 Tokenizer、Embedding、预训练目标与 Transformer 理解输入到下一个 Token 的路径。
2. 学习采样、上下文、KV Cache、量化和服务，建立质量、延迟与成本意识。
3. 再学习 Prompt、结构化输出和 Function Calling，构建受控应用接口。
4. 最后比较 SFT、PEFT/LoRA、RLHF/DPO 与蒸馏，明确何时训练、何时检索或换模型。

## 核心主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| Tokenizer | BPE/Unigram 直觉、词表、特殊 Token、序列长度和中英文成本 | L3 | core |
| Embedding | Token Embedding、位置表示、句向量用途，以及与生成输出的区别 | L3 | core |
| 预训练目标 | Causal LM、Masked LM、数据混合、规模规律和训练数据边界 | L2 | core |
| Transformer | 自回归解码、Attention、残差、归一化、位置编码和因果 Mask | L3 | core |
| Prompt | 系统/用户消息、指令、Few-shot、版本化和可证伪评测 | L3 | core |
| Context | Context Engineering、窗口预算、信息排序、截断和上下文污染 | L3 | core |
| 结构化输出 | JSON Schema、约束解码、解析校验、修复、重试和降级 | L3 | core |
| Function Calling | 工具描述、参数 Schema、调用结果回填、错误边界和权限隔离 | L3 | core |
| 幻觉 | 事实错误、无依据生成、拒答、Grounding 和错误分类 | L3 | core |
| 模型选型 | 质量、模态、上下文、隐私、许可、延迟、吞吐、成本和锁定风险 | L3 | core |

## 常用主题

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| SFT | 监督微调（Supervised Fine-Tuning）的数据格式、目标、切分、过拟合和评测 | L2 | common |
| PEFT/LoRA | 参数高效微调、低秩适配、秩与目标模块、保存和合并 | L3 | common |
| 采样 | Greedy、Temperature、top-k、top-p、停止条件、随机种子和复现边界 | L3 | common |
| KV Cache | Prefill/Decode、缓存形状、显存占用、上下文长度与吞吐权衡 | L3 | common |
| 量化 | 权重/激活精度、PTQ/QAT、校准数据，以及质量、显存和速度权衡 | L2 | common |
| 模型服务 | 批处理、流式输出、首 Token 延迟、吞吐、并发、超时和供应商抽象 | L3 | common |

## 拓展视野

| 主题 | 范围 | 建议深度 | 重要程度 |
| --- | --- | --- | --- |
| RLHF/DPO | 偏好数据、奖励模型、策略优化和直接偏好优化的目标与风险 | L3 | extension |
| 蒸馏 | 教师/学生、软标签、响应蒸馏、能力迁移和评测污染 | L3 | extension |
| 从头预训练 | 数据治理、分词器、分布式训练、检查点和规模预算 | L4 | extension |
| 稀疏与长上下文 | MoE、稀疏 Attention、位置外推和长上下文评测 | L4 | extension |

## 最小实验

- 比较两种 Tokenizer 对中英文、代码和 JSON 输入的 Token 数量与截断行为。
- 在固定评测集上比较自由文本、JSON 提示和 Schema 约束输出，记录合规率与失败样例。
- 用 PyTorch 实现单头因果 Attention 和逐 Token 贪心生成，验证 Mask、形状和停止条件。
- 比较基础模型与小型 LoRA 适配，记录训练/验证曲线、质量、延迟和显存。

## 项目

- 在 `llm-engineering-lab` 中实现统一模型适配器、Prompt 版本、结构化输出校验、评测集和成本/延迟报告。
- 以[阶段 2：LLM 工程](../01-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/%E9%98%B6%E6%AE%B5%202-%E5%A4%A7%E6%A8%A1%E5%9E%8B%20LLM%20%E5%B7%A5%E7%A8%8B.md)的退出证据约束复现、适配和模型选择。

## 开源研究

- 跟踪 Transformers 从 Tokenizer、`generate` 到采样的一条公开调用链。
- 跟踪 PEFT 的 LoRA 模块注入、训练参数、保存与加载路径。
- 跟踪 vLLM 的模型加载、请求调度、批处理与 OpenAI 兼容服务入口。

## 面试入口

- 从输入到下一个 Token 解释 Transformer 推理与 KV Cache，并量化主要成本。
- 比较 Prompt、长上下文、RAG、LoRA、全量微调和更换模型的适用条件。
- 设计可靠的结构化输出与 Function Calling 链路，覆盖校验、超时、重试和降级。
- 用固定评测集答辩模型选型，并解释幻觉、延迟、成本和隐私取舍。

## 相邻领域

- [深度学习](../04-%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0-MOC.md)：提供 Transformer、训练与推理机制。
- [机器学习](../03-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0-MOC.md)：提供评测、泛化和错误分析方法。
- [AI 全局知识地图](../00-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/AI%20%E7%9F%A5%E8%AF%86%E5%9C%B0%E5%9B%BE.md)：查看 LLM 与 RAG、Agent、生产和安全的依赖关系。
- [AI/FDE 七阶段路线](../01-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF-MOC.md)：把领域知识落实为阶段实验与项目证据。
