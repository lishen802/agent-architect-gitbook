# 附录 C 配套代码仓库说明

本书的配套实现与书稿位于同一仓库的 `examples/` 目录。仓库地址为[agent-architect-gitbook](https://github.com/lishen802/agent-architect-gitbook)。章节中的代码须标明可运行示例、节选或职责示意，不能把伪代码当作生产实现复制。

| 项目 | 对应章节 | 能支持的结论 |
| --- | --- | --- |
| [告警助手](https://github.com/lishen802/agent-architect-gitbook/blob/main/examples/alert-assistant/README.md) | 第 4、5 章；第 6 章沿用任务背景 | 本地保存响应的输入、输出与失败处理；未接入在线模型 |
| [评测记录与汇总](https://github.com/lishen802/agent-architect-gitbook/blob/main/examples/evaluation-basics/README.md) | 第 6 章 | 教学记录的契约检查与汇总；语义标签预先构造，未调用真实模型 |
| [插图构建脚本](https://github.com/lishen802/agent-architect-gitbook/tree/main/assets) | 全书插图 | 重建书中 SVG 插图，不承担自动架构选型 |
| 具体模型与框架适配 | 后续补充 | 不提供在线成功率、费用或性能结论 |

各项目的环境与核验记录：

- 告警助手：Go 模块声明 1.22；2026-10-09 在 Go 1.27.1、macOS arm64 验证。
- 评测记录与汇总：Python 标准库；2026-10-20 在 Python 3.12.3 核验。
- 插图构建脚本：Python 标准库，共用 `figlib.py`；生成后需按原尺寸与栏宽渲染复核。
- 具体模型与框架适配：尚未选择和核验实现版本。

从仓库根目录运行现有示例：

```sh
cd examples/alert-assistant
go test ./...
go run .
```

重建全部插图：

```sh
cd assets
python3 build-all.py
```

示例无需 API 密钥，不发送生产数据。`SavedResponse` 读取已保存响应，不根据输入生成内容。真实适配需要重新核对接口、处理结束原因、传递取消，并建立任务级评测。

对新增项目，记录输入样例、运行环境、依赖锁定方式、核验日期、执行命令与限制；若报告性能或费用，还要保留任务集、配置、计量口径与失败调用。没有完成的验证应明确留空，不填写猜测值。
