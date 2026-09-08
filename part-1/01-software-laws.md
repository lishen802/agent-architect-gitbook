# 第 01 章：从确定性程序到概率性系统——Agent 工程的第一性原理

传统软件工程把需求翻译成确定的控制流，再用类型、测试、事务和监控保证它按预期运行。Agent 系统没有推翻这些原则。它改变的是一个关键前提：**部分控制流不再由程序员在编译期完整写出，而是由模型根据目标、上下文和环境反馈在运行时生成。**

Agent 工程因此不是“把 LLM 接到业务 API 上”，而是要回答：

> 当系统中存在一个能力很强、但输出不能被绝对预测的决策组件时，怎样仍然向业务提供可验证、可恢复、可治理的服务承诺？

后续章节讨论的 Runtime、TaskState、Tool、RAG、评测和 Guardrails，都可以看作对这个问题的逐层回答。

---

## 1.1 变化的不是接口，而是控制流

先看一个普通的告警处理服务：

```go
func HandleAlert(ctx context.Context, alert Alert) error {
    metrics, err := queryMetrics(ctx, alert.Service)
    if err != nil {
        return err
    }
    if metrics.ErrorRate > 0.05 {
        return createIncident(ctx, alert, metrics)
    }
    return nil
}
```

程序可能超时，依赖可能失败，机器也可能宕机；但只要输入和外部状态相同，它的决策规则就是明确的：错误率超过 5%，创建事故单；否则结束。

LLM 也可以被包装成 RPC：输入 Prompt，返回文本或 JSON。但真正的变化发生在我们让模型决定“下一步做什么”时：

```go
decision := model.Decide(ctx, goal, state, availableTools)
```

`decision` 可能是查询指标、检索变更记录、请求人工确认，也可能是结束任务。下一步路径不再完整存在于源代码中，而是在运行时由模型生成。

![确定性程序与 Agent 系统的控制边界](01-deterministic-vs-agent.svg)

[用 draw.io 编辑此图](01-deterministic-vs-agent.drawio)

判断一个系统是否真正具有 Agent 特征，不应只看它是否调用了模型，而要看模型是否获得了以下一种或多种权力：

- 选择下一步动作；
- 选择或组合工具；
- 根据观察结果修改计划；
- 判断任务是否已经完成。

如果模型只负责分类、抽取、摘要或生成文案，而业务代码仍然决定完整流程，它更准确地属于 **LLM-enhanced application**。这不是能力高低之分，而是两种不同的控制模型和风险模型。

---

## 1.2 两类不确定性：模型与环境

Agent 的不确定性不只来自“同一个问题可能得到不同答案”。生产环境里至少存在两类不确定性。

### 模型不确定性

即使使用结构化输出并降低采样随机性，我们也不应把模型等同于普通函数：

- 模型升级、System Prompt 变化和上下文顺序可能改变决策；
- 合法的 JSON 不代表参数在业务语义上正确；
- 模型可能遗漏约束、误解目标或过早宣布完成；
- 长上下文中的关键信息可能没有被稳定利用。

结构化输出解决的是“能否解析”，不是“是否正确”。

### 环境不确定性

Agent 会读取并改变外部世界，而外部世界在不断变化：

- 查询结束后，资源状态可能已经改变；
- 工具超时，不代表动作一定没有执行；
- 两个并发任务可能同时修改同一对象；
- 检索结果可能过期、不完整或被恶意内容污染。

传统程序的恢复路径通常由工程师预先定义，Agent 则可能根据错误信息临时生成新路径。模型不确定性与环境不确定性叠加后，系统的可达状态会迅速扩大。

因此，Agent Runtime 的职责不是消除不确定性，而是把它约束在可接受的范围内。

---

## 1.3 三种控制模式，而不是“代际替代”

确定性程序、Workflow 和 Agent 并不是前后淘汰的三代技术。它们是三种控制模式，往往同时存在于一个系统中。

![三种控制模式](01-control-modes.svg)

[用 draw.io 编辑此图](01-control-modes.drawio)

| 模式 | 控制流由谁决定 | 适合的问题 | 主要风险 |
| --- | --- | --- | --- |
| 确定性程序 | 业务代码 | 规则稳定、路径可枚举、强一致性操作 | 规则膨胀，难处理开放输入 |
| Workflow / DAG | 预定义图或状态机 | 长流程、并发编排、审批、补偿和断点续传 | 图复杂度、版本迁移、状态一致性 |
| Agent Loop | 模型在运行时选择动作 | 目标明确但路径未知，需要探索和多步归因 | 漂移、循环、越权、成本和不可复现 |

成熟系统通常采用混合结构：

1. 确定性代码负责身份、权限、配额、事务与最终提交；
2. Workflow 负责长任务编排、等待、审批和补偿；
3. Agent 只进入那些无法提前穷举、但可以通过观察和工具逐步求解的局部区域。

最关键的架构问题不是“要不要用 Agent”，而是：**哪一段控制流值得在运行时交给模型？**

---

## 1.4 决策权必须与执行权分离

模型擅长提出候选动作，但不应天然拥有物理执行权。生产级 Agent 最基本的安全边界可以概括为：

> **LLM proposes, system validates, policy decides, tool executes.**  
> 模型提议，系统校验，策略裁决，工具执行。

![Agent 动作执行流水线](01-action-pipeline.svg)

[用 draw.io 编辑此图](01-action-pipeline.drawio)

### 模型提议：输出是不可信候选

模型返回工具名、参数以及动作理由。这个结果只是一份提案，不是命令。

### 系统校验：保证机器层面的合法性

Runtime 检查工具是否存在、参数能否通过 Schema、资源标识是否合法、是否超过大小和时间限制。校验失败应转化为结构化 Observation，而不是把底层堆栈原样塞回上下文。

### 策略裁决：判断当前主体是否被允许这样做

Schema 合法不等于业务允许。同一个 `restart_workload`，在测试环境可以自动执行，在生产环境可能需要值班人员批准，对核心数据库集群则应完全禁止。

### 工具执行：在受控边界内产生副作用

执行器负责超时、幂等键、审计、并发限制和结果规范化。它返回事实，不负责决定下一步。

这层分离带来一个重要结论：**Prompt 不是安全边界。** Prompt 可以降低模型提出危险动作的概率，但只有代码、权限系统和隔离环境才能阻止危险动作真正发生。

---

## 1.5 确定性骨架与概率性岛屿

“80% 确定性代码 + 20% 模型推理”常被当作经验法则。它有启发性，但不是需要计算的固定比例。更准确的原则是：

> 能在设计期稳定枚举的规则，优先留在代码或工作流中；只有路径无法穷举、需要结合非结构化信息动态判断的部分，才交给模型。

可以用四个问题划分边界：

1. 规则是否稳定且可以枚举？如果可以，用代码。
2. 路径是否复杂但拓扑已知？如果已知，用 Workflow。
3. 是否需要在未知环境中多步探索？如果需要，考虑 Agent。
4. 一次错误动作的损失是否不可逆？如果是，收回执行权或增加人工审批。

例如，“查询过去七天订单总额”是确定性查询；“解释华东区域退款率异常的可能原因”需要跨指标、日志和业务事件进行探索，适合放入 Agentic Island；而“根据分析结果直接批量退款”必须重新回到确定性审批和事务系统。

模型获得的自主权应当与风险成反比：风险越高，动作空间越小，确认点越多。

---

## 1.6 最小生产级 Runtime

教学 Demo 的 Agent Loop 可能只有十几行：模型决定动作，工具返回结果，循环直到模型结束。但生产系统至少需要显式管理预算、状态、权限与恢复：

```go
type RuntimeLimits struct {
    MaxSteps       int
    MaxWallTime    time.Duration
    MaxTokenBudget int
    MaxToolCalls   map[string]int
}

type TaskState struct {
    TaskID        string
    Goal          string
    Status        TaskStatus
    Facts         []Fact
    PendingAction *Action
    Step          int
    Version       int64
}

func (r *Runtime) Run(ctx context.Context, task *TaskState) (*Result, error) {
    for !task.Status.Terminal() {
        if err := r.limits.Check(task); err != nil {
            return r.stop(task, err)
        }

        proposal, err := r.model.Propose(ctx, r.buildContext(task))
        if err != nil {
            return r.retryOrStop(task, err)
        }

        action, err := r.validator.Validate(proposal)
        if err != nil {
            r.observeValidationError(task, err)
            continue
        }

        verdict := r.policy.Decide(ctx, task, action)
        if verdict.RequiresApproval {
            return r.suspendForApproval(task, action)
        }
        if !verdict.Allowed {
            r.observePolicyDenied(task, verdict)
            continue
        }

        observation := r.executor.Execute(ctx, action)
        r.checkpoint.Append(task, action, observation)
    }
    return r.result(task), nil
}
```

Runtime 必须拥有模型之外的控制权：

- **预算控制**：步数、时间、Token、工具调用次数均有上限；
- **循环检测**：识别相同动作和相同错误的重复轨迹；
- **状态持久化**：在副作用前后留下可恢复的 Checkpoint；
- **并发控制**：用版本号或租约避免多个执行器同时推进同一任务；
- **人工挂起**：等待审批时释放计算资源，而不是占住进程；
- **终止权**：Runtime 可以否决模型的“继续”，也可以拒绝模型过早的“完成”。

Agent Loop 是算法表面，Runtime 才是工程主体。

---

## 1.7 贯穿全书的 SRE 案例

假设支付服务在发布后错误率升高，系统目标是“定位原因并在安全范围内缓解故障”。

失控的 Agent 可能读取告警后立即重启实例，失败后重复重启，最后根据不完整日志宣布问题已解决。受控系统会这样划分职责：

| 环节 | 实现方式 | 原因 |
| --- | --- | --- |
| 接收告警、创建任务 | 确定性代码 | 需要幂等和去重 |
| 拉取指标、日志、发布记录 | 受控工具 | 输入输出可审计 |
| 选择下一项证据、形成根因假设 | Agent | 路径无法预先穷举 |
| 判断操作风险 | Policy Engine | 不能由模型自我授权 |
| 回滚生产发布 | Workflow + 人工审批 | 高风险，需补偿和留痕 |
| 验证错误率是否恢复 | 确定性规则 | 成功条件应客观可计算 |
| 生成事故摘要 | LLM | 适合压缩和组织信息 |

最有价值的 Agent 系统不一定让模型做最多的事，而是让模型只做那些非它不可、且风险可控的事。

---

## 1.8 四个常见反模式

### 万物皆 Agent

固定查询、字段映射和阈值判断本来可以稳定编码，却被包装成多个 Agent 互相对话，导致延迟、成本和故障面同时上升。

**修正**：先画确定性流程，再标记真正无法枚举的决策点。Agent 应是局部能力，而不是默认容器。

### 把 Prompt 当权限系统

System Prompt 写着“禁止删除生产资源”，但工具凭证仍然拥有删除权限。一旦发生提示注入或上下文污染，安全承诺就会失效。

**修正**：最小权限凭证、工具白名单、参数策略和审批机制必须位于模型之外。

### 只有 `max_steps`，没有收敛判定

限制最多执行 20 步可以控制最坏成本，却不能阻止 Agent 在 20 步内反复执行同一动作。

**修正**：记录动作签名、错误分类和状态增量；若连续步骤没有产生新事实，主动熔断或升级人工处理。

### 把消息历史当任务状态

对话消息适合给模型阅读，却不适合作为唯一事实源。它无法可靠表达并发版本、待审批动作、幂等键和恢复点。

**修正**：用结构化 TaskState 保存业务事实和执行状态，再按需投影成模型上下文。

---

## 本章小结

1. Agent 的本质变化，是模型获得了部分运行时控制流决策权。
2. 模型不确定性和环境不确定性会叠加，Runtime 必须限制可达状态。
3. 确定性程序、Workflow 与 Agent 是可以组合的控制模式。
4. 决策权与执行权必须分离；Prompt 不能代替权限和策略。
5. 可靠系统把模型限制在“概率性岛屿”内，并用确定性骨架承接身份、状态、副作用和恢复。

## 架构思考题

1. 在你维护的系统中，哪一步需要开放式探索，哪一步只是被误包装成了 Agent？
2. 如果工具超时，但无法确认操作是否已经成功，Runtime 应如何避免重复副作用？
3. 对一个可以自动扩容、但不能自动缩容的 SRE Agent，你会如何设计 Tool Schema、Policy 和审批点？

