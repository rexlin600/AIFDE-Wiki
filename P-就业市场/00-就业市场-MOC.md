---
type: moc
domain:
  - Job Market
  - FDE
depth: L3
importance: common
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 招聘市场观察
tags:
  - jobs
  - evidence
---

# 招聘市场 MOC

## 岗位名称集合

采样不能只检索 `FDE`，应覆盖 Forward Deployed Engineer、Forward Deployed AI Engineer、Applied AI Engineer、AI Application Engineer、Agent Engineer、AI Solution Engineer，以及以 AI 实际交付为主要工作的 Customer Engineer 和 Solutions Architect。名称相同不代表职责相同，统计以前述工作内容为准。

## 单个样本字段

每份样本记录公司、岗位原始名称、地点、工作方式、级别或年限（仅在页面明确时）、职责摘要、必要/加分能力、行业与合规约束、来源 URL、来源类型、访问日期、页面状态和归一化能力标签。可补充薪酬范围，但必须保留币种、周期、适用地点和原文口径。

只保存自己的结构化摘要和少量必要术语，不复制岗位全文，不从缺失信息推断级别、薪酬、签证或招聘状态。

## 季度采样方法

1. 每季度首月使用固定岗位名称集合检索企业官方招聘页，必要时补充招聘平台。
2. 去重规则使用“公司 + 原始岗位名称 + 地点”；同一 URL 内容显著变化时新建带访问日期的快照笔记。
3. 优先收录官方页面可直接核验、职责与 AI 交付高度相关的样本；记录被排除原因。
4. 每个公司和岗位族设置样本上限，避免单一雇主或批量相似职位支配统计。
5. 汇总标签出现次数与样本占比，并同时报告样本量、来源构成和缺失情况；不同季度不把页面消失直接解释为需求下降。

## 技能归一化词表

| 归一化标签 | 可归入的页面表述 |
| --- | --- |
| `software-engineering` | Python、API、数据库、测试、分布式或生产系统 |
| `ai-application` | LLM 应用、RAG、Agent、Prompt 或模型集成 |
| `evaluation` | Evals、验证、基准、错误分析或验收门槛 |
| `enterprise-integration` | 企业 API、数据平台、EHR、身份或遗留系统 |
| `reliability` | Observability、性能、可用性、部署或运维 |
| `security-governance` | 隐私、授权、审计、合规、PHI/HIPAA |
| `discovery-delivery` | Discovery、范围、架构、实现、上线与交接 |
| `customer-collaboration` | 客户工程、运营、领域专家或利益相关者协作 |
| `product-feedback` | 参考架构、可复用模式、产品改进或前线反馈 |

同一句可映射多个标签，但必须保留样本链接以便审计；同义词归一化不扩大原文含义。

## 自动访问失败

若自动访问遇到登录、验证码、地区限制、动态渲染、拒绝访问或页面消失，应记录时间、URL、失败类型和采用的只读重试方式。搜索摘要、缓存或第三方转载只能帮助定位官方页面，不能替代岗位原文证据；无法核验时将样本标为 `unverified`，排除出职责与技能统计，并安排人工复核。不得绕过访问控制。

## 当前样本

- [OpenAI：Forward Deployed Engineer, Healthcare](01-%E6%8B%9B%E8%81%98-OpenAI%20FDE%20%E5%8C%BB%E7%96%97%E5%81%A5%E5%BA%B7-20260909.md)，官方页面访问于 2026-09-09。

## 与路线的连接

季度汇总用于调整[路线总览](../B-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF/00-%E5%AD%A6%E4%B9%A0%E8%B7%AF%E7%BA%BF-MOC.md)的证据优先级，并以 [FDE 能力模型](../A-%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97/02-FDE%20%E8%83%BD%E5%8A%9B%E6%A8%A1%E5%9E%8B.md)聚类；单个岗位不能决定完整学习路线，也不用于推断公司的内部职级标准。
