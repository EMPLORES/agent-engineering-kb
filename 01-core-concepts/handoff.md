\# Handoff



\## 1. 一句话定义



Handoff 是一种多 Agent 编排模式，用于表达当前 Agent 将任务处理权交给目标 Agent 的意图，并由框架或调度器执行相应的控制权转移



\## 2. Handoff 解决什么问题？



多个 Agent 可以运行在相同的框架、模型和 Runtime 中，但由于职责、指令、工具或权限不同，它们可能分别擅长不同的任务。当当前 Agent 不应继续独自处理任务，而需要由专门的 Agent 接管后续工作时，就需要一种明确的任务交接机制。



Handoff 用于表达交接意图和目标 Agent。随后，框架或调度器执行控制权转移，并向接收方提供继续完成任务所必需的输入和上下文。具体传递哪些信息，取决于框架的实现和应用设计。



\## 3. Handoff 的最小工作流程



```text

用户请求

&#x20;  ↓

当前 Agent 分析任务

&#x20;  ↓

确定交接目标和需要交接的任务

&#x20;  ↓

Handoff 表达交接意图

&#x20;  ↓

Runtime / 调度器识别请求并执行转交

&#x20;  ↓

接收方 Agent 接管并处理任务

&#x20;  ↓

接收方给出结果

```



\## 4. Handoff 与 Agent-as-Tool 的区别



\*\*Handoff：\*\* 当当前 Agent 判断后续任务应该由另一个 Agent 接管时，可以采用 Handoff，将任务处理权交给目标 Agent，由其继续后续处理。



\*\*Agent-as-Tool：\*\* 当主 Agent 需要借助另一个 Agent 的专业能力，但仍希望保留控制权、接收对方的结果并继续进行推理或整合时，可以采用这种方式



两种模式的选择主要取决于后续控制权由谁持有，而不是单纯取决于任务的复杂程度。如果主 Agent 需要保留控制权，并继续分析或整合专业 Agent 的返回结果，可以使用 Agent-as-Tool；如果需要由专业 Agent 接管后续任务，则可以使用 Handoff。两种模式也可以组合使用。



\## 5. Handoff 与 Workflow 的关系



Workflow / 路由机制负责组织执行流程，并决定下一步执行哪个节点或分支，因此可以将执行路径导向目标 Agent 所在的节点。



Handoff 表达当前 Agent 将任务处理权交给目标 Agent 的意图；Runtime 或调度器则根据交接请求执行实际的控制流转，并提供接收方所需的输入和上下文。



三者可以协同工作，但职责并不相同：Workflow 关注执行路径，Handoff 关注任务处理权的交接，Runtime 负责落实相应的执行行为。在某些框架中，路由到另一个 Agent 可以通过独立的 Handoff API 实现；在其他架构中，也可以直接通过图节点和条件边完成相应的控制流转。



\## 6. 我在 Python 实验中学到了什么



在本次 Python 实验中，Handoff 类保存了目标 Agent 的名称 `target\_agent` 和需要交接的任务 `task`，用于表达交接意图。



创建 Handoff 对象本身不会自动发生控制权转移。调度逻辑需要识别这个对象，读取目标 Agent 和任务内容，再调用对应的 Agent 函数，才能在当前实验中完成交接。



本次实验只实现了交接目标和任务内容的传递，没有实现通用的上下文管理、元数据管理或完整的 Agent Runtime。生产级框架可以在此基础上提供更完善的交接配置、上下文传递和执行控制机制



实现交接的代码：



```python

if isinstance(result, Handoff):

&#x20;   if result.target\_agent == "refund\_agent":

&#x20;       result = refund\_agent(result.task)

```



\## 7. 与 OpenAI Agents SDK 的关系



Handoff 是 OpenAI Agents SDK 提供的核心编排能力之一，用于将任务处理权从当前 Agent 转交给目标 Agent。开发者可以通过 Agent 的 `handoffs` 配置声明可交接的目标，也可以使用 `handoff()` 辅助函数配置交接行为。



SDK 默认向接收方提供此前的对话历史，也允许使用 `input\_filter` 调整传递内容。交接参数、回调和上下文的处理方式取决于具体 API 配置，不能简单理解为所有元数据都会自动传递。



\## 8. 当前阶段的学习结论



当当前 Agent 不适合或不应继续独自处理任务，而系统又需要由另一个 Agent 接管后续工作时，可以考虑使用 Handoff。



Handoff 是一种多 Agent 编排模式，其核心是将任务处理权从当前 Agent 转交给目标 Agent。它与 Agent-as-Tool 的区别不在于是否执行了另一个 Agent，而在于两种机制预期的控制流程不同：Agent-as-Tool 通常让调用方保留控制权并处理调用结果，而 Handoff 让接收方接管后续处理。



在 LangGraph 中，可以使用 StateGraph 的节点、边、条件路由和状态管理来实现 Agent 之间的任务交接。Workflow 或路由机制负责决定下一步执行哪个节点；Handoff 描述任务处理权的交接意图；图的执行机制负责实际运行对应节点。这些职责可以协同工作，但不意味着 LangGraph 中存在一个固定、独立的 Handoff 中间层。



不同 Agent 框架可以采用不同的 API 和内部实现来完成 Handoff。理解其控制流语义，比记住某个特定框架的接口更重要

