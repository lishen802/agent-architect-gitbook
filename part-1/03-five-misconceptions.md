# 第 03 章：撕掉伪概念标签——五大必须纠正的架构认知偏差

1. Eval 绝不能后置，从第 1 周就开始构建自动化评估。
2. 严格区分 Agent Memory 与推理引擎的 KV Cache。
3. 核心持久化的是 TaskState，而非思维链 Scratchpad。
4. 强确定性来源于代码、Schema 与数据库，而非模型本身。
5. 能单 Agent 绝不多 Agent，能 Workflow 绝不让模型自主决策。
