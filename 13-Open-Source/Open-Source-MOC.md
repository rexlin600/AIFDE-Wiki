---
type: moc
domain:
  - Open Source
depth: L4
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 开源研究
tags:
  - open-source
  - source-code
---

# 开源研究 MOC

## 研究闭环

开源学习以可验证问题为起点，依次经过四层：

1. **使用与评测：** 固定版本、输入和验收条件，记录成功与失败样例。
2. **调用链跟踪：** 从一个公开 API 进入，定位关键状态、分支、持久化或错误路径。
3. **最小复刻：** 只复刻理解机制所需的最小子集，并注明灵感来源与许可边界。
4. **改造或贡献：** 用公开最小样例验证改动；是否提交上游由维护成本与通用价值决定。

只读 README 或完成 Quickstart 属于第一层的开始，不等同于掌握实现或完成贡献。

## 按阶段选择代表仓库

| 阶段 | 代表仓库 | 研究问题 |
| --- | --- | --- |
| AI/ML | [scikit-learn](https://github.com/scikit-learn/scikit-learn)、[PyTorch](https://github.com/pytorch/pytorch) | 估计器契约、训练循环与自动微分 |
| LLM | [Transformers](https://github.com/huggingface/transformers)、[nanoGPT](https://github.com/karpathy/nanoGPT)、[OpenAI Cookbook](https://github.com/openai/openai-cookbook) | Tokenizer、Attention、生成与 API 样例 |
| RAG | [LlamaIndex](https://github.com/run-llama/llama_index)、[RAGFlow](https://github.com/infiniflow/ragflow)、[GraphRAG](https://github.com/microsoft/graphrag)、[pgvector](https://github.com/pgvector/pgvector)、[Qdrant](https://github.com/qdrant/qdrant) | 摄取、索引、检索、重排、引用与评测 |
| Agent | [LangGraph](https://github.com/langchain-ai/langgraph)、[OpenAI Agents SDK](https://github.com/openai/openai-agents-python)、[MCP Servers](https://github.com/modelcontextprotocol/servers) | Agent Loop、状态、工具、审批、恢复与协议边界 |
| 生产工程 | [LiteLLM](https://github.com/BerriAI/litellm)、[vLLM](https://github.com/vllm-project/vllm)、[DeepEval](https://github.com/confident-ai/deepeval)、[promptfoo](https://github.com/promptfoo/promptfoo) | 网关、推理、评测、Tracing 与安全测试 |
| 端到端产品 | [Dify](https://github.com/langgenius/dify)、[RAGFlow](https://github.com/infiniflow/ragflow) | 完整架构、扩展点、部署和运维边界 |

## 许可证检查

每次研究都以目标版本仓库根目录的 `LICENSE`、`COPYING` 或官方许可说明为准，记录项目、目标版本、许可证标识、访问日期和所用文件。还要检查依赖、模型权重、数据集与示例素材是否另有条款；“源码可见”不等于允许复制、修改或再分发。许可证缺失、冲突或用途不明确时，只做链接与事实性描述，不复制实现，并在采用前寻求法律意见。

## Source 档案要求

- 项目定位、维护主体、官方仓库、许可证与访问日期。
- 一条足够具体且可复查的公开调用链。
- 可靠性与失败语义，而非只记正常路径。
- 可独立实现的最小子集、预期学习结果和停止条件。
- 局限、替代方案，以及与 Wiki 主题和项目的关系。

## 当前样例

- [LangGraph 源码研究](Repo-LangGraph.md)：从 `StateGraph` 构建到 `CompiledStateGraph.invoke` 的调用链。

## 相邻入口

- [Agent](../07-Agent/Agent-MOC.md)
- [生产 AI](../09-Production-AI/Production-AI-MOC.md)
- [实战项目](../12-Projects/Projects-MOC.md)
