# 第 01 章：告别确定性妄想——AI Agent 时代的软件工程法则

> “半个世纪以来，现代软件工程的核心成就是将物理硬件的不稳定性封装进确定性的数学逻辑中；而智能体系统工程的核心任务，是学会在概率性黑盒之上，用分布式与平台工程手段重新构建高韧性的确定性围栏。”

---

## 1.1 软件工程的确定性契约与大模型的概率断层

在传统的后端系统与分布式架构中，工程师与计算机之间签署的是一份**确定性契约 (Deterministic Contract)**：
* 给定明确的前置条件与输入参数 $X$；
* 经过编译后的确定性指令序列 $f(X)$；
* 必定在有限步骤内转移到确定性的下一状态，并返回符合 Schema 定义的输出 $Y$。

在这个世界里，单元测试的本质是严格等值断言：
```go
// 传统软件的确定性世界
func TestCalculateDiscount(t *testing.T) {
    result := CalculateDiscount(100.0, "VIP")
    assert.Equal(t, 80.0, result) // 任何偏差均被定义为 Bug
}

// ==========================================
// 传统思维：硬编码业务流 (无控制权反转)
// ==========================================
func HandleOrderComplaint(ctx context.Context, orderID string) error {
    order := db.QueryOrder(orderID)
    logs := loki.QueryLogs(orderID)
    
    // 即使在这里调用大模型，它也只是一个无害的纯文本分析器
    analysis := llm.Analyze(logs)
    
    // 下一步永远被 Go 代码死死锁住：先退款，再发短信
    payment.Refund(order.UserID, order.Amount)
    sms.Send(order.UserID, "您的投诉已处理：" + analysis)
    return nil
}

// ==========================================
// Agent 思维：运行时控制权反转 (IoC)
// ==========================================
type AgentRuntime struct {
    MaxSteps int
    Registry *ToolRegistry
    Policy   *PolicyGate
}

func (r *AgentRuntime) Run(ctx context.Context, goal string) (*TaskResult, error) {
    state := NewTaskState(goal)
    
    for step := 0; step < r.MaxSteps; step++ {
        // 核心反转点：模型根据当前观察事实，自主决定下一步是“查日志”、“退款”还是“发短信”
        decision := r.ReasonNextAction(ctx, state)
        
        if decision.Type == ActionFinish {
            return decision.Result, nil
        }
        
        // 架构师的职责不是代替模型做决定，而是在系统层拦截、校验并安全执行
        obs, err := r.Policy.ExecuteSafely(ctx, decision.Tool, decision.Args)
        state.AppendStep(decision, obs, err)
    }
    return nil, ErrMaxStepsExceeded
}
