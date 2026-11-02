\# Runtime Loop



\## 1. Runtime Loop 是什么？



Runtime Loop 是 Agent 运行时的执行循环机制，负责协调模型调用、工具执行、结果反馈以及后续执行，直到任务完成或达到停止条件。



Agent 整个系统的执行过程需要 Runtime Loop 来负责整体的协调和流转，它将模型决策与外部工具执行连接起来，使 Agent 能够持续推进任务。



\## 2. Runtime Loop 的执行流程



结合实验 27，执行流程如下：



`用户输入 → Runtime 调用模型 → 模型进行决策 → 返回工具调用请求 → Runtime 执行 Tool → 将工具结果追加到 Messages → 再次调用模型 → 最终回答`



具体来说：



1\. 用户输入任务。

2\. Runtime 将用户输入交给模型。

3\. 模型根据当前 Messages 决定提出工具调用请求，或者直接返回最终答案。

4\. 如果模型提出工具调用，Runtime 负责找到对应的 Tool 并执行。

5\. Tool 返回执行结果。

6\. Runtime 将 Tool Result 追加到 Messages。

7\. Runtime 再次调用模型，让模型根据新的 Messages 继续决策。

8\. 当模型返回最终答案时，Runtime 结束循环。



\## 3. Model、Runtime 和 Tool 的职责区别



\- \*\*Model：\*\* 根据输入的上下文进行推理和决策，决定直接返回答案还是提出工具调用请求，充当 Agent 的大脑。

\- \*\*Runtime：\*\* 负责模型调用、工具执行、结果反馈以及整个执行循环的协调和控制。

\- \*\*Tool：\*\* 提供具体功能，用于解决问题和执行实际操作，例如实验中的天气查询函数。



\## 4. 实验 27：Basic Runtime Loop



对应代码：`04-labs/27\_basic\_runtime.py`



在此实验中，用户输入后，`fake\_model()` 接收到 Messages 并模拟模型思考和决策，提出 Tool Calling 请求。



Runtime 接收到请求后，找到对应的 Tool 并执行调用。工具执行后返回结果，Runtime 将其追加到 Messages 中，再次提供给 `fake\_model()`，从而进入下一轮 Runtime Loop。



\- `fake\_model()`：模拟模型的行为，根据当前 Messages 决定提出工具调用请求还是返回最终答案。

\- `get\_weather()`：模拟实际工具，负责查询指定城市的天气并返回结果。

\- `run\_agent()`：负责调用模型、处理工具调用、保存工具结果并控制整个执行循环。

\- `messages.append()`：将工具执行结果追加到 Messages，使模型能够在下一轮调用中获取工具执行结果。

\- `max\_steps`：设置 Runtime Loop 的最大执行轮数，避免模型重复提出工具调用请求，导致程序持续执行。



\## 5. Runtime Loop 的退出机制



模型根据当前 Messages 和用户提出的问题进行决策。当模型认为可以返回最终答案时，会输出最终回答，而不是继续提出工具调用请求。



Runtime 负责识别模型的返回结果：



\- 如果模型提出 Tool Calling，Runtime 执行对应工具，并将结果反馈给模型，进入下一轮循环。

\- 如果模型返回最终答案，Runtime 结束循环并返回结果。

\- 如果达到最大执行步数，Runtime 停止执行，避免程序持续循环。



在这个过程中，模型负责根据上下文进行推理和决策，Runtime 负责执行循环和控制停止条件。



\## 6. 实验中的异常情况



如果删除将 Tool Result 追加到 Messages 的代码，模型就无法获得工具执行结果。



在本实验的模拟逻辑下，模型会重复提出相同的工具调用请求，Runtime 因此重复执行工具，直到达到 `max\_steps` 后停止。



触发最大执行步数限制，是为了在异常情况出现时避免程序持续循环，减少不必要的执行成本。



\## 7. 我的理解



一次完整的 Runtime Loop 是由 Runtime 负责接收用户输入、调用模型并处理模型返回结果。模型思考后提出 Tool Calling 决策，Runtime 负责执行工具调用，并将工具返回的结果追加到 Messages 中，再次提供给模型，从而进入下一轮循环，直到模型返回最终答案或达到最大执行步数。



模型没有直接执行工具的权限，只能提出 Tool Calling 请求。Runtime 负责实际执行工具，并控制整个系统的执行过程，将模型决策、工具执行和结果反馈连接起来。



\---



\*\*实验文件：\*\* `04-labs/27\_basic\_runtime.py`

