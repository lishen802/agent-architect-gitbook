# Summary

* [前言：写给传统程序员的范式转移指南](README.md)
  * [传统软件的确定性世界与大模型的概率黑盒](intro/determinism-vs-probabilistic.md)
  * [你的工程资产并没有失效：能力迁移映射图谱](intro/skill-mapping.md)

* [第一篇：范式转移与认知重构 (Mental Models)](part-1/README.md)
  * [第 01 章：告别确定性妄想——AI Agent 时代的软件工程法则](part-1/01-software-laws.md)
  * [第 02 章：架构师的需求审判——Agent 决策矩阵与十问心法](part-1/02-architecture-matrix.md)
  * [第 03 章：撕掉伪概念标签——五大必须纠正的架构认知偏差](part-1/03-five-misconceptions.md)

* [第二篇：智能体内核与运行时设计 (Runtime & State)](part-2/README.md)
  * [第 04 章：手写最小 ReAct Loop——从零构建控制反转执行引擎](part-2/04-react-loop.md)
  * [第 05 章：状态驱动设计——结构化 TaskState 与并发 Actor 运行时](part-2/05-taskstate-runtime.md)
  * [第 06 章：持久化执行与人机协同——Durable Workflow 与 Checkpoint](part-2/06-durable-execution.md)

* [第三篇：交互边界、上下文与知识工程 (Boundary & Context)](part-2/README.md)
  * [第 07 章：工具工程与执行沙箱——Schema 约束与安全隔离](part-3/07-tool-engineering.md)
  * [第 08 章：上下文工程——Token 预算控制与工作记忆分层](part-3/08-context-engineering.md)
  * [第 09 章：走出向量库迷思——企业级 Hybrid RAG 架构](part-3/09-hybrid-rag.md)

* [第四篇：可靠性工程、平台底座与规模化 (Reliability & Platform)](part-3/README.md)
  * [第 10 章：评测驱动开发 (EDD)——Tracing 链路与 Golden Benchmark](part-4/10-eval-observability.md)
  * [第 11 章：确定性安全围栏——Guardrails 与动作空间控制](part-4/11-guardrails-security.md)
  * [第 12 章：智能体网关与平台化治理——路由、缓存与成本控制](part-4/12-gateway-cost.md)
  * [第 13 章：多智能体系统的工程审判——权衡、协议与实战](part-4/13-multi-agent.md)

* [第五篇：贯穿实战全纪实 (Capstone Project)](part-5/README.md)
  * [第 14 章：企业级 SRE 故障自愈 Agent V1 到 V10 演进史](part-5/14-sre-agent-evolution.md)

* [附录：开源框架底层设计哲学深度导读](appendix/README.md)
  * [附录 A：LangGraph 源码解密：图状态机与 Checkpoint 机制](appendix/langgraph.md)
  * [附录 B：OpenAI Agents SDK 极简抽象解析](appendix/openai-agents-sdk.md)
  * [附录 C：Google ADK 的 Go 语言实践参考](appendix/google-adk.md)
