# Guardrails（护栏机制）

## 1. 一句话解释

Guardrail 是用于约束 Agent 执行过程的检查机制，通过对输入、工具调用或输出进行校验，并结合相应的控制逻辑，降低违规行为发生的风险。

- **Input Guardrail**：负责检查输入内容是否符合预定义的规则，避免危险行为发生。
- **Output Guardrail**：负责检查 Agent 输出内容是否符合预定义的规则，避免泄露一些隐私信息。
- **Tool Guardrail**：负责在工具执行前加入权限校验，避免危险或越界行为的发生。

## 2. 它解决什么问题？

Agent 可能接收到不符合规则的输入、生成不合适的输出，或尝试执行超出权限范围的工具操作。Guardrail 通过在相应执行阶段进行检查，并根据检查结果决定是否继续执行，降低这些风险。

## 3. 最小工作流程

```text
用户输入
   ↓
Input Guardrail
   ├── 失败 → return
   └── 通过
         ↓
Agent 请求调用工具
         ↓
Tool Guardrail / 权限校验
   ├── 拒绝 → return
   └── 通过
         ↓
执行工具
         ↓
Output Guardrail
   ├── 拒绝 → return
   └── 通过
         ↓
返回结果
```

## 4. Input Guardrail 与 Output Guardrail 的区别

- **Input Guardrail**：负责检查输入的内容是否符合预定义的规则。
- **Output Guardrail**：负责检查 Agent 输出内容是否符合预定义的规则。

Guardrail 负责检查是否符合预定义规则；实际能否阻止后续执行，取决于执行流程是否根据检查结果进行拦截。Input Guardrail 和 Output Guardrail 的检查位置不同，工具权限校验则可以在工具执行前阻止未经授权的操作。

## 5. Guardrail 与工具权限检查的关系

工具权限检查是一种常见的架构设计思路，是 Guardrail 的一部分，由框架在 Agent 执行生命周期的特定阶段调用。工具权限检查可以在工具执行前校验操作是否获得授权，并根据检查结果决定是否允许执行。具体实现方式取决于所使用的框架和系统架构。

## 6. 与 HITL 的区别

Guardrail 主要根据预定义规则进行检查，并结合控制逻辑决定是否允许流程继续执行。HITL 则在需要人工判断、授权或确认的关键节点引入人类决策。

Guardrail 可以自动检查和拦截；HITL 需要将决策交给人类处理，两者也可以结合使用。

## 7. 实验观察与局限

### 实验一：正常请求

```text
用户输入：帮我总结 Agent Architecture
[Input Guardrail] 通过
[Agent] 正在处理用户请求
[Agent] 输出：已处理请求：帮我总结 Agent Architecture
[Output Guardrail] 通过
```

### 实验二：输出检查拒绝

```text
用户输入：请在结果中包含密码这个词
[Input Guardrail] 通过
[Agent] 正在处理用户请求
[Agent] 输出：已处理请求：请在结果中包含密码这个词
[Output Guardrail] 拒绝：输出包含敏感内容
[System] 输出未通过检查，不返回给用户
```

### 实验三：输入检查拒绝

```text
用户输入：帮我执行转账
[Input Guardrail] 拒绝：当前系统不允许处理转账请求
[System] 请求被拦截，Agent 不会执行
```

### 实验四：空输入

```text
用户输入：
[Input Guardrail] 拒绝：输入不能为空
[System] 请求被拦截，Agent 不会执行
```

