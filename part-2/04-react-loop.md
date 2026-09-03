# 第 04 章：手写最小 ReAct Loop——从零构建控制反转执行引擎

## 4.1 ReAct 协议本质
Think -> Act -> Observe 循环驱动。

## 4.2 Go 最小实现
```go
for step := 0; step < MaxSteps; step++ {
    resp := llm.Chat(ctx, state)
    switch resp.Type {
    case ToolCall:
        res := registry.Execute(ctx, resp.Tool, resp.Args)
        state.AppendObservation(res)
    case FinalAnswer:
        return resp.Answer
    }
}
```
