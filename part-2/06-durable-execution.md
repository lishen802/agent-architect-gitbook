# 第 06 章：持久化执行与人机协同——Durable Workflow 与 Checkpoint

借鉴 Temporal 理念：
- Event Sourcing 记录每一次调用
- 状态变更触发 Checkpoint 落盘
- 审批挂起与中断唤醒 (Signal & Resume)
