\# Workflow



\## 1. 一句话定义

Workflow 定义的是图的拓扑结构（节点集合 + 边 + 路由规则），不定义节点内部的具体逻辑



\## 2. Workflow 解决什么问题？

每一个节点后对于下一个节点的流转以及每一步之间的如何连接，还有对于不同工具产生结果后执行不同分支包括步骤怎么连、分支怎么走、工具结果出来后按哪条预定义规则路由。

\## 3. Workflow 与 Planning、Agent Loop 的区别

Workflow：静态拓扑 + 预定义路由规则（谁连谁）



Planning：动态决策下一步做什么（路径由模型/策略生成）



Agent Loop：执行引擎，驱动“判断→行动→观察”反复发生



\## 4. 固定流程与条件路由



固定流程是：路径完全写死，A→B→C，没有 if。



条件路由：在固定流程基础上增加预定义分支。分支集合和判断规则由工程师预定义，运行时根据 State 选一条。它仍然是确定性的，只是多了 if/else。

\## 5. 执行结果驱动的条件路由

Agent Loop（外层执行引擎）

&#x20; └─ 任务输入

&#x20; └─ Planning（生成/更新计划）

&#x20; └─ Workflow（节点执行 + 条件路由）

&#x20; └─ Tool Result

&#x20; └─ 回到 Workflow 路由决定下一节点

&#x20; └─ ... 直到结束

\## 6. Workflow 的最小工作流程



任务内容 → Planning → Workflow → Tool Result → Workflow → 循环直到结束



注意：Agent Loop 不是最后一步，它是包裹整个过程的执行引擎。

\## 7. 与 LangGraph 的关系

workflow属于LangGraph中的控制策略，是loop中的控制逻辑，决定了每一轮判断的依据以及整个循环的路径形态，是确定性的，可审计的策略，用灵活性换取可靠性和可预测性

\## 8. 当前阶段的学习结论

Agent Loop 是机制层，负责驱动“判断→行动→观察”反复发生；它本身不决定路径。



Workflow 是确定性控制策略，定义节点拓扑、分支集合和路由规则；条件路由是 Workflow 的内部能力，不是 Planning。



Planning 是动态控制策略，负责在运行时决定下一步做什么、是否调整计划；它可以把计划固化为中间产物，但决策本身不一定确定。



三者关系：Loop 是容器，Workflow 是骨架，Planning 是大脑；生产级系统用 Workflow 约束 Planning，而不是二选一。



LangGraph 中：StateGraph 的节点和边承载 Workflow；条件边里的路由函数可以写死规则（Workflow），也可以调用 LLM 做动态决策（Planning）；Checkpointer 按 thread\_id 保存 Loop 每个 super-step 后的 State。

\## 9. 后续实践方向

先跑纯线性 Workflow：START → A → B → END，理解节点返回值如何合并进 State。



加条件路由：用 add\_conditional\_edges 实现“工具结果不同走不同分支”，路由函数只读 State，不调 LLM。



加循环：让条件边指回前面的节点，实现“不满足条件就重试”，理解一个 Loop 里会产生多个 Checkpoint。



加 Checkpointer + thread\_id：跑两次 invoke，验证同一 thread\_id 能续上历史，不同 thread\_id 互不串状态。



加中断：用 interrupt\_before 在某个节点前暂停，再用同一 thread\_id 恢复，理解“人工介入”的落点。



最后再引入 Planning：在条件边路由函数里调用 LLM 做动态决策，对比第2步的写死规则，体会“确定性 vs 动态性”的差异。



混合架构：外层用固定阶段（Workflow），内层用条件边 + LLM 路由（Planning），体会生产级“骨架固定、局部动态”的设计

