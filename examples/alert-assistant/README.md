# 告警分析助手：第 4、5 章配套示例

本示例验证输入、生成结果与业务状态之间的边界。它使用本地保存的响应作为模型替身，不访问在线服务，不需要 API 密钥，也不执行运维操作。所有数据均为教学构造。

## 运行

模块使用 Go 1.22 语言版本；实际验证环境为 Go 1.27.1、macOS arm64，无第三方依赖。以下命令从仓库根目录开始：

```sh
cd examples/alert-assistant
go test ./...
go run .
```

默认输入为 [fixtures/alert.json](fixtures/alert.json)，响应为 [fixtures/report.json](fixtures/report.json)。正常返回 `status: draft`、`reason: review_required` 与报告正文。提示版本为 `alert-report-v1`。

自定义文件：

```sh
go run . -input /path/to/alert.json -response /path/to/report.json
```

两个路径需要替换为实际文件。`SavedResponse` 不根据输入生成内容；必须自行选择与输入对应的保存响应。业务结果输出成功时退出码为零，需要读取 JSON 内的 `status`；文件读取与输入解析失败则以非零状态退出。

## 验证范围

测试覆盖无证据短路、无效输入、引用约束、信息不足、非完整生成、调用错误和预先取消的请求。它们验证业务边界，不度量模型的事实准确率、提示有效性、线上延迟或 Token 成本。

`draft` 只表示程序接受了一份待审阅草稿；引用存在不等于引用支持结论。示例不检查所有自然语言事实，也不实现身份认证、持久化日志、自动重试、完整 JSON Schema 校验或供应商适配器。

JSON 解析遵循 Go `encoding/json` 的语义，拒绝未知字段、非对象与多对象响应，但不额外拒绝重复键或大小写不一致的字段名。Context 取消需要模型实现配合，不能强制中止忽略 Context 的实现。

## 接入在线模型

实现 [main.go](main.go) 中的 `Model` 接口，将任务说明、输入和完整报告 Schema 映射到所选服务的官方协议；传递 Context，限制响应大小，映射结束原因并记录实际模型、请求 ID 与用量。保留现有业务校验，再执行真实模型的语义评测。

设计方法与评测要求见[第 4 章](../../part-2/04-model-integration.md)和[第 5 章](../../part-2/05-first-ai-application.md)。
