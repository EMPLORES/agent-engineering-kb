# Context（上下文）

## 1. 一句话解释

Context 是当前执行阶段可用的信息，负责告诉 Agent 当前的背景内容。

## 2. 它解决什么问题？

Agent 在执行任务时，需要明确当前的任务内容、状态，甚至一些元数据等，才能判断下一步如何推进。Context 就是为此提供所需信息的部分。

## 3. Context、Prompt、State、Memory 的区别

- **Context**：当前执行阶段可用的信息集合。
- **Prompt**：由工程师或调用者提供给 Agent 的指令或输入文本。
- **State**：当前的任务状态数据和内容。
- **Memory**：保存具有可调用性和未来参考价值的信息。

Context、Prompt、State 和 Memory 并不是互斥的概念，它们承担不同的职责。

在一种常见设计中，系统可以根据当前 State、用户输入以及从 Memory 中检索的信息，组装当前执行阶段所需的 Context，再将相关信息组织成 Prompt 提供给 LLM。具体的数据组织和传递方式取决于框架设计。

## 4. 最小工作流程

```text
用户输入 + State + 按需检索的 Memory
                ↓
       组装当前执行所需的 Context
                ↓
     结合 Prompt 调用 Agent / LLM
                ↓
          决策与执行
```

## 5. 最小代码示例

Context 为 Agent 当前执行阶段提供所需的信息；State 用于表示和维护任务执行过程中的状态与相关数据。两者可能包含相关信息，但关注的职责不同。

### 实验输出

```text
D:\Projects\agent-engineering-kb>python 04-labs\26_basic_context.py
情况一：
准备开始规划前往 北京 的行程

情况二：
前往 北京 的行程已经完成

情况三：
缺少目的地信息，无法制定具体行程
```

### 局限

本实验通过普通 Python 字典模拟 Context 和 State，使用条件判断观察不同输入对输出的影响。实验**没有**实现真实 LLM 调用、Memory 检索或完整的 Agent 状态管理。

## 6. 与 LangGraph / OpenAI Agents SDK 的关系

Context 在 LangGraph 和 OpenAI Agents SDK 中的具体实现方式、传递机制和生命周期，需要结合各自的官方文档与源码进一步学习。

目前可以确定的是，Context 用于向当前执行过程提供所需的信息，但不能直接将它等同于全局变量。不同框架可能采用不同的数据结构和传递机制，具体实现留待后续源码学习验证。

## 7. 我的理解

本节梳理 Context 的具体含义、它在整体框架中的作用和位置，以及 Context 与 State / Memory 的区别和 Prompt 的作用。

- **Context**：当前执行状态下的信息集合。
- **State**：当前任务的状态数据和内容。
- **Memory**：负责保存并在需要时检索可复用的信息。

这是一种实用的架构划分，不代表三者在所有框架中的边界完全相同。

Context、State 和 Memory 并不是完全互斥的数据概念。根据框架设计，State 和 Memory 中的信息可以被选取或检索，再用于构建当前执行所需的 Context。但它们并不一定始终相互关联，具体关系取决于系统的架构设计。
