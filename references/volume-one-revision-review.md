# 第一卷结构调整：核验范围与边界

记录日期：2026 年 10 月 16 日。本记录是作者工作记录，不代替独立审阅。

## 资料依据

下列官方或原始资料于本轮写作中查阅（2026 年 10 月 15 日）；各正文与附录在相关结论旁给出链接。

| 主题 | 原始资料 | 使用边界 |
| --- | --- | --- |
| 评测对象、判定器与任务隔离 | [Anthropic 评测工程文章](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 借鉴方法，不声称给定阈值普遍适用 |
| 浏览器操作检查 | [Playwright actionability](https://playwright.dev/docs/actionability) | 元素可操作不等于业务提交成功 |
| 提示注入 | [OWASP 防护指南](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | 分层约束，不承诺完全消除攻击 |
| 幂等重试 | [AWS Builders’ Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | 外部服务契约决定保障范围，客户端重试不是自动安全 |
| 中国境内合规 | [附录 D 的官方来源](../appendix/compliance-cn.md) | 按服务对象、数据流与功能判断；不泛化备案义务 |

## 内容状态

第 2 章清单、选型图与预算例子是本书的设计工具，不是统计验证的评分器；成本和耗时示例为教学假设。第 6 章给评测方法，没有宣称已测得模型效果。第 14、15 章为教学样章，没有虚构生产部署。所有章末答案是基于题设的参考选择，可以被新证据改变。

未完成：真实模型效果实验、独立技术审阅、朋友试读、框架版本与能力逐项核验、其余章节扩写。原有第 1 章待补图仍需补齐。现有离线示例只能支持本地应用契约与失败处理结论。

目录、章号、相对链接、图源一致性和离线示例属于本轮仓库校验范围；这些检查不代表整本书技术正确性已获得独立认证。

## 本轮实际校验

2026 年 10 月 16 日完成：23 章标题、目录顺序、节号、经验对照和迁移练习结构检查；六个场景各有六项正文结构；100 个本地链接目标存在；book.json 与 SVG 可解析，SVG 由源脚本重建一致；`git diff --check` 通过。作者 drafts 工作稿不纳入出版导航检查，也未修改。

在 `examples/alert-assistant` 执行 `go test ./...` 与 `go run .` 通过，运行返回需人工审阅的草稿。此次验证仍为离线回放，不支持任何真实模型准确率、成本或延迟结论。
