# 前言：写给传统程序员的范式转移指南

欢迎阅读《从程序员到智能体架构师：Agent Runtime 与系统工程实战》。

本书是专门为拥有后端架构（Go/Java）、微服务、分布式系统、或机器学习训推平台工程背景的开发者量身打造的 Agent 系统架构专著。

## 为什么写这本书？
当前市面上 90% 的 Agent 教程停留在：
1. 介绍 LangChain / LlamaIndex 的 API 怎么调；
2. 演示如何写几个 Prompt 拼装一个玩具 Demo；
3. 盲目堆砌 Multi-Agent 概念，忽视系统的稳定性、成本与延迟。

当业务线提出：“我们想做一个 AI Agent，自动处理 XXX” 时，工程师往往发现这些玩具架构在生产环境瞬间崩溃——死循环、幻觉调用危险 API、Token 爆表、超时无恢复、无法评估优化。

本书的核心宗旨：**跳过玩具阶段，用工业级分布式架构与平台工程思维，从零构建高可靠的 Agent Runtime 与基础设施。**

## 核心法则
> **LLM Proposes, System Validates, Policy Decides, Tool Executes.**
> （大模型提议，系统校验，策略决策，工具执行）
