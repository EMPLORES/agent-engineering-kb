\# State-driven Routing



\## 1. State-driven Routing 是什么？



State-driven Routing（状态驱动路由）是根据当前 State 中保存的任务状态，决定程序下一步应该执行什么操作的机制。





在较为完整的 Agent Architecture 中，State 存储当前任务的数据状态和内容。系统可以根据当前 State 采用不同的决策方式：一方面，系统可以将当前 State 中相关的任务信息提供给 LLM，LLM 根据这些信息和上下文进行推理并决定下一步操作，另一方面，系统也可以根据预定义的条件路由规则，选择不同的执行节点。


State 更新是当前任务数据状态和内容的变化，而 State-driven Routing 是根据当前 State 和预定义规则，判断下一步执行哪个操作或节点的过程。Runtime 负责协调路由判断和后续 Action 的执行。




\## 2. 实验 30：State-driven Routing



对应代码：`04-labs/30\_state\_driven\_routing.py`





route\_next\_step(state) 根据当前 State 中的 status，通过预定义的条件判断返回下一步操作名称，用于模拟条件路由。



actions 字典负责将操作名称映射到具体的 Python 函数。



run\_runtime() 负责协调整个执行过程，包括调用 route\_next\_step() 获取下一步操作名称、通过 actions 查找对应函数、执行 Action，以及控制循环和停止条件。



\## 3. State 如何决定下一步执行什么？

route\_next\_step(state) 直接读取传入的 State。



函数通过 if-elif 等预定义条件判断，根据 State 中的 status 返回下一步操作名称，模拟确定性的条件路由过程。



由于 State 中保存的任务状态不同，Routing 根据当前 State 进行条件判断时，可能返回不同的操作名称。



Routing 返回的是下一步操作的名称，并不负责执行实际操作。实际执行由 Runtime 根据 actions 字典找到对应函数后完成



\## 4. Routing 与 Action 执行

Routing 根据当前 State 中的任务状态，按照预定义规则决定下一步操作。


actions 字典已经将相关操作名称映射为具体的 Python 函数。



找到对应函数后，run\_runtime() 负责执行函数，并控制整个循环和停止条件


Action 函数执行后，根据具体的执行逻辑修改 State 中的任务数据。Runtime 负责协调函数执行，而更新后的 State 会在下一轮被 Routing 读取，进而影响后续的路由判断。





\## 5. State-driven Routing 的执行流程



读取 State → route\_next\_step() → 返回下一步操作名称 → actions 查找对应函数 → Runtime 执行 Action → Action 更新 State → 再次 Routing





State 更新后，Runtime 再次调用 Routing。Routing 根据更新后的 State 判断是否满足预定义规则，并返回下一步操作名称。



max\_steps 用于限制 Runtime Loop 的最大执行轮数，避免程序持续循环。当循环达到最大执行轮数，程序仍未满足正常结束条件时，就会停止执行并抛出异常。


当程序按照预定义路由进入正常结束条件时，Runtime 结束循环并返回相应结果。





\## 6. 实验中的异常情况

如果 State 中的 status 不属于 route\_next\_step() 已支持的状态，函数无法匹配预定义规则，会抛出 ValueError，程序停止执行。



如果 Routing 返回的操作名称在 actions 字典中不存在对应函数，Runtime 无法找到需要执行的 Action，会抛出 ValueError，程序停止执行



max\_steps 用于限制 Runtime Loop 的最大执行轮数。当程序超过最大执行步数时，会停止执行并抛出异常。它主要用于控制循环执行规模，避免程序持续运行。



前两种情况属于状态判断或动作映射异常；max\_steps 则属于执行次数限制。它们都可以防止程序无限制地继续执行，但解决的问题不同





\## 7. State Management 与 State-driven Routing 的区别

State Management 负责状态管理，对任务状态数据和内容进行保存，读取，更新的管理过程


State-driven Routing 负责根据不同的 State，按照预定义规则选择下一步执行操作或节点。在更完整的 Agent Architecture 中，还可以与 LLM 动态规划机制配合。



State 更新是执行过程中对任务数据的修改。Runtime 负责协调执行流程，但 State 更新本身并不意味着程序会自动调度下一个函数或节点。


二者根据系统和框架的具体设计，所负责的执行行为的不同，产生的结果和影响也不同，State Management 负责数据状态，State-driven Routing 负责执行路径。



\## 8. 我的理解

在较为完整的 Agent Architecture 中，LLM 动态规划和条件路由可以相互配合。系统将当前 State 中相关的任务信息提供给 LLM，LLM 根据这些信息和上下文进行推理，决定下一步行动。条件路由根据预定义规则选择相应的执行节点。两者分别提供灵活的推理决策能力和确定性的执行控制能力。



route\_next\_step() 负责根据当前 State 决定下一步操作名称，run\_runtime() 负责在整个循环中调用路由函数、查找对应 Action、执行函数，并控制循环和停止条件。



Routing 根据 State 判断是否满足预定义条件，并返回相应的操作名称。如果没有匹配的条件，程序需要按照架构中预先设计的异常处理或其他分支进行处理。若希望由 LLM 重新规划，需要显式设计 LLM 决策节点，不能假设条件路由会自动将 State 交给 LLM。


当前实验使用 Python 函数和预定义条件模拟条件路由的执行过程，并没有真正实现 LLM 自主规划。真实的 LLM 动态规划还需要处理开放式任务、模糊要求和不完全明确的执行目标，需要结合上下文理解、模型推理和工具调用等能力。


State-driven Routing 与 LangGraph Conditional Edges（条件边）在概念上具有直接联系：都可以根据当前 State 和条件判断，选择下一步执行的节点。但是，Conditional Edges 本身并不会自动触发 LLM 动态规划。如果希望在条件不匹配时由 LLM 重新判断，需要在 LangGraph 中显式设计相应的 LLM 节点和路由分支。

\---



\*\*实验文件：\*\* `04-labs/30\_state\_driven\_routing.py`

