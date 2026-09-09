---
type: concept
domain:
  - Machine Learning
depth: L3
importance: core
maturity: draft
created: 2026-09-09
updated: 2026-09-09
last_verified: 2026-09-09
aliases:
  - 树模型
  - 梯度提升树
tags:
  - supervised-learning
  - tree-models
---

# 树与 Boosting

<!-- markdownlint-disable MD012 MD013 -->

## 它解决什么机器学习问题

树模型擅长表格数据中的阈值、非线性和特征交互，例如“距离超过 8 公里且处于晚高峰时，超时风险突然增加”。它常是结构化数据必须比较的强基线。

## 不理解会造成什么错误

- 让单棵树无限生长，训练集完美、线上却不稳定。
- 认为更多树必然更好，忽略延迟、内存和过拟合。
- 把特征重要性误当因果贡献。
- 在编码全量数据后再验证，引入泄漏。

## 它在建模工作流中的位置

先有可信拆分、简单线性基线和稳定特征，再比较树模型。选择后仍需用[指标](06-指标.md)、[校准](10-校准.md)和切片误差验证上线价值。

## 从表格基线案例开始

在支付时预测订单是否超时。单棵树给出可读规则；随机森林降低单树对样本扰动的敏感；Boosting 逐轮修正当前错误。漏报会错失调度，误报会浪费运力。

## 决策树怎样分裂

分类树寻找“特征 $j$ 是否小于阈值 $s$”的切分，使子节点更纯。二分类 Gini 不纯度为：

$$
G=1-p^2-(1-p)^2=2p(1-p)
$$

节点全是一类时 $G=0$；两类各半时 $G=0.5$。算法选择加权子节点不纯度下降最大的切分。

## 最小手算

父节点有 2 正 2 负，$G=0.5$。一个切分得到左侧 2 正、右侧 2 负，两个子节点 Gini 都为 0，加权不纯度降为 0。如果切分只是各放 1 正 1 负，不纯度没有下降。

## 随机森林与 Boosting

- **随机森林：** 对不同自助样本训练许多树，分裂时随机选择部分特征，最后平均，借此降低方差。
- **梯度提升：** 后一棵树拟合当前损失的负梯度，不断加小步修正：$F_m=F_{m-1}+\eta h_m$。
- **学习率：** $\eta$ 决定每棵树贡献多大；更小的学习率通常需要更多树。
- **树深度：** 控制单树可表达的交互，也是最重要的复杂度旋钮之一。

## 可执行实验

```python
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = make_classification(
    n_samples=1200, n_features=12, n_informative=6,
    class_sep=0.8, flip_y=0.04, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)
models = {
    "deep_tree": DecisionTreeClassifier(random_state=42),
    "small_tree": DecisionTreeClassifier(
        max_depth=4, min_samples_leaf=15, random_state=42
    ),
    "forest": RandomForestClassifier(
        n_estimators=150, min_samples_leaf=5, random_state=42
    ),
    "boosting": GradientBoostingClassifier(
        n_estimators=100, max_depth=2, learning_rate=0.05, random_state=42
    ),
}
for name, model in models.items():
    model.fit(X_train, y_train)
    train_auc = roc_auc_score(y_train, model.predict_proba(X_train)[:, 1])
    test_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(name, "train", round(train_auc, 3), "test", round(test_auc, 3))
```

深树往往训练 AUC 接近 1，却不一定有最佳测试 AUC。其他模型展示了偏差、方差与计算成本的不同取舍。

## 评测与结果解释

在同一拆分、特征和指标上与线性基线比较。除总分外还要记录训练时长、单条预测延迟、模型体积和切片表现。特征重要性只说明模型如何降低损失；相关特征会分摊或替代重要性，不能推出因果关系。

## 数据与泄漏风险

树能轻易记住高基数 ID、时间戳和未来状态。类别编码、目标编码和缺失值填补必须在训练折内拟合。若同一客户重复出现，应按客户或时间拆分。

## 工程排错

| 现象 | 可能原因 | 优先检查 |
| --- | --- | --- |
| 训练满分测试差 | 树太深或叶子太小 | 深度、叶子样本数、学习曲线 |
| Boosting 后期变差 | 轮数过多或学习率过大 | 验证曲线、早停、学习率 |
| 结果每次波动 | 样本少或种子未固定 | 多折方差、种子、分组边界 |
| 某 ID 极其重要 | 模型在记忆实体 | 唯一值比例、移除后复验 |
| 线上延迟超标 | 树数或深度过大 | 单条延迟、模型大小、线程 |

## 适用与不适用场景

适合中等规模表格数据、非线性和交互明显的任务。超高维稀疏文本常先试线性模型；树不擅长平滑外推；若要求因果或严格可审计规则，需要额外约束。

## 学习收益

你应能手算 Gini，解释单树、森林和 Boosting 的差异，通过训练测试差距调复杂度，并谨慎解释特征重要性。

## 给别人讲清楚

“树通过连续提问给数据分组；森林让许多有差异的树投票；Boosting 让后面的树专门修正前面的错误。”

## 自检问题

1. 为什么单棵深树容易过拟合？
2. 学习率变小后为什么常增加树数？
3. 特征重要性为什么不能证明因果关系？

## 相关主题

- [分类](02-分类.md)
- [特征工程](04-特征工程.md)
- [验证设计](11-验证设计.md)

## 资料来源

- scikit-learn, [Decision Trees](https://scikit-learn.org/stable/modules/tree.html)，访问日期：2026-09-09。
- scikit-learn, [Ensembles](https://scikit-learn.org/stable/modules/ensemble.html)，访问日期：2026-09-09。
- Jerome H. Friedman, [Greedy Function Approximation](https://doi.org/10.1214/aos/1013203451), 2001。
