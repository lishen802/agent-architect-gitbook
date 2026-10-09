# 第 2、3 章资料核验记录

本文供作者维护，不纳入读者目录。核验日期为 2026 年 10 月 9 日。正文在相关论断处提供链接；本文记录引用范围和未能由来源证明的结论。

## 关键论断与依据

| 论断或方法 | 一手资料 | 本书使用范围与限制 |
| --- | --- | --- |
| 以预定义路径与模型动态决定过程区分工作流和智能体 | Anthropic：[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)，原文发表于 2024-12-19 | 作为一种工程分类视角，明确不是行业统一标准；不引用其中可能随版本变化的模型名单与能力描述 |
| 架构决策记录包含背景、决策、状态与后果 | Michael Nygard：[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)，2011-11-15 | 本书增加验证计划、重评条件与未决事项，明确为作者对案例的适配 |
| 常见自回归 Transformer 中 KV Cache 用于复用注意力键和值 | Hugging Face：[How caching works](https://huggingface.co/docs/transformers/cache_explanation) | 不推导所有模型都采用同一缓存结构，也不声称缓存必然只能存在于单次请求内；不把计算复用等同于应用记忆 |
| 结果不明时直接重试可能造成重复副作用，幂等需服务端契约 | AWS Builders' Library：[Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | 使用超时、操作标识、参数一致性与保留期限的机制说明；不承诺任意接口都支持相同保证 |
| 测试数据参与方案选择可能导致过于乐观的评价 | scikit-learn：[Common pitfalls：Data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) | 原文讨论机器学习评估，本书明确将隔离评价信息的方法应用到提示与应用方案，不把提示调整称作参数训练 |
| 生成的解释不应直接视为忠实、完整的决策审计 | Turpin 等：[Language Models Don't Always Say What They Think](https://arxiv.org/abs/2305.04388)，2023，页面所示 v2 修订于 2023-12-09 | 只使用论文测试中存在不忠实解释这一发现，不引用具体错误率，不将其外推到所有当前模型 |
| 模型外保留授权、最小权限与工具调用校验 | OWASP：[LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | 引用其分层控制建议；不把提示过滤、模型护栏或人工批准写成绝对安全保证 |

## 属于作者设计的内容

第 2 章的选型比较表、告警职责表、ADR-001 与评测定义是教学设计，并非已有生产项目结果。第 3 章的状态字段、审批绑定与故障诊断表同样属于案例设计。正文说明了这些内容的用途，没有赋予统计有效性或行业标准地位。

工作流不等于 DAG，是两者定义范围的区分：DAG 不含有向环，工作流可以用含循环的状态转移表达。相关表述没有声称所有工作流引擎均支持同样的循环、持久化或恢复特性。

“检查点不能单独保证外部动作恰好一次”用于说明事务边界：若外部动作与状态写入不在同一受协调的边界内，单独存储进度不能填补二者之间的失败窗口。具体保证需要按所用引擎与外部接口核验，正文未声称已经实现通用方案。

## 相邻章节修正

第 1 章同步修正了以下表述，避免与新章冲突：

- 将“编译期完整写出”改为预设业务规则与运行时动作选择，避免混淆编译过程与应用设计。
- 将 Agent 特征说明改为本书工作定义，承认分类路由可以仍属于预定义工作流。
- 将 `Workflow / DAG` 拆清，并注明持久化与恢复依赖实现。
- 移除没有依据的 80/20 经验比例，及自主权与风险的数学反比措辞。
- 将“最小生产级 Runtime”改为职责说明，保留示意代码不可直接运行的说明。
- 明确检查点不足以避免重复副作用，租约设计需要考虑过期执行器。
- 明确步数上限不等于耗时、Token 与工具费用的完整上限。
- 区分普通自然语言历史与具备明确语义的结构化事件记录。

## 验证边界

第 4、5 章与配套 Go 示例在本轮一起提交。示例仍为离线保存响应回放，没有真实在线模型实验。代码测试通过与 Markdown 检查通过，只说明相应检查范围内未发现失败，不证明书稿已完成独立技术审阅，也不等于所有应用效果已得到验证。
