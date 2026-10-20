# 第 7 章写作与核验记录

写作与资料核验日期：2026 年 10 月 20 日。状态：正文初稿与作者自查，未完成独立技术审阅。

## 本章范围

从告警助手的固定取证需求出发，说明工具粒度、契约、身份与权限、结果范围、失败语义和写操作身份；不要求读者先采用动态智能体。新增工具契约模板，保留会议室预约迁移题并补充并发与结果不明的区别。

JSON 结果为人为构造的内部契约示意，不属于供应商 API；流程、状态分类与验收表为设计建议，不是已经实现或测得的系统行为。未修改 Go 配套实现，未接入实际监控服务或在线模型。

## 关键依据与适用范围

| 资料 | 支持的论断 | 不能据此推断 |
| --- | --- | --- |
| [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) 的工具附录 | 工具定义、参数和使用说明需要认真设计 | 清楚的说明可以替代授权，或某个框架是当前默认推荐 |
| [OWASP：Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | 最小权限、默认拒绝、逐请求授权 | 仅筛选模型可见工具就完成资源授权 |
| [OWASP：LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | 外部结果是不可信输入，工具参数与权限在模型外约束 | 标注来源或检测器能够保证阻断全部注入 |
| [AWS：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | 请求标识表达重试意图，实际保障依赖服务端契约 | 本地 UUID、相同参数或先查后写自动提供外部幂等性 |

原始资料中的产品 API、框架和性能信息未作为本章实现保证。正文重点保持协议无关，具体实现需要按实际版本另行核验。

## 作者自查重点

- 区分模型提议、执行侧身份、业务授权与人工审批。
- 区分查询范围完整、证据充分与事实正确。
- 区分失败、处理中、部分返回和结果不明。
- 区分调用关联标识、持久化业务操作号和下游幂等机制。
- 区分同一意图的重试与不同意图之间的资源竞争。
- 不把模拟测试计划、离线示例或正常返回写成真实集成成果。

独立审阅仍应关注：工具粒度是否便于读者迁移，异常分类是否足以支撑具体实现，以及哪些段落需要配合实际接口实验再扩写。

## 仓库校验

本轮已检查 23 章目录、标题与章节结构，105 个本地链接目标存在；第 7 章示例 JSON 可解析、时间顺序与单位一致；`git diff --check` 通过。代码未改动，因此本轮未重复运行 Go 测试；这些文档检查不代表工具集成或模型效果验证。
