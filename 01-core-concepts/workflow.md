\# Workflow



\## 1. 一句话定义

Workflow 定义或约束任务的执行流程，包括节点之间的连接和路由规则；节点内部的具体工作由节点逻辑实现。



\## 2. Workflow 解决什么问题？

Workflow 负责定义节点之间的执行顺序、连接关系和条件路由规则，包括工具执行后如何根据结果选择下一步





如果没有 Workflow，复杂任务中的节点调用顺序、异常分支和工具结果处理可能散落在大量条件语句中，导致执行路径难以维护、测试和审计。

\## 3. Workflow 与 Planning、Agent Loop 的区别

Workflow 可以包含由 LLM 决策的条件路由节点。







Planning 可以提前生成计划，也可以在运行过程中重新规划。







Agent Loop 负责持续推进决策、行动和观察；具体实现可以由图循环、程序循环或其他执行机制承担。



\## 4. 固定流程与条件路由



固定流程是：路径完全写死，A→B→C，执行路径不依赖运行时条件来选择不同分支。



条件路由：在固定流程基础上增加预定义分支。分支集合和判断规则由工程师预定义，运行时根据 State 选一条。它仍然是确定性的，只是多了 if/else，但不代表整个系统一定确定





\## 5. 执行结果驱动的条件路由

接收任务

&#x20;  ↓

Workflow 根据条件选择执行分支

&#x20;  ↓

执行对应节点或工具

&#x20;  ↓

工具结果更新当前状态

&#x20;  ↓

Workflow 根据结果选择下一步

&#x20;  ↓

继续执行 / 结束任务



注意：这只是当前实验的简化流程。不是所有 Workflow 都必须包含 Planning，也不是所有工具结果都必须触发重新路由。

\## 6. Workflow 的最小工作流程



任务内容 → Planning → Workflow → Tool Result → Workflow → 循环直到结束



注意：Agent Loop 不是最后一步，它是包裹整个过程的执行引擎。

\## 7. 与 LangGraph 的关系

在 LangGraph 中，StateGraph 的节点、边和条件边可以共同实现 Workflow。Workflow 可以使用固定规则进行路由，也可以将 LLM 决策纳入路由过程。固定规则有利于提高可预测性和可审计性，但整个图的行为是否确定，还取决于节点逻辑及其使用的模型、工具等因素。



\## 8. 当前阶段的学习结论

Agent Loop 是机制层，负责驱动“判断→行动→观察”反复发生；它本身不决定路径。



Workflow 是流程组织与控制策略，定义节点拓扑、分支集合和路由规则；条件路由是 Workflow 的内部能力，不是 Planning。



Planning 负责生成或调整任务计划，包括执行步骤、顺序和策略。它可以在任务开始前生成计划，也可以在执行过程中根据新信息重新规划。Workflow 则负责组织节点执行和路由，两者可以结合使用；它可以把计划固化为中间产物，但决策本身不一定确定。



三者关系：Loop 是容器，Workflow 是骨架，Planning 是大脑；在需要可控性、可审计性和可靠性的任务中，可以用明确的 Workflow 约束动态决策的范围。

LangGraph 中：StateGraph 的节点和边承载 Workflow；条件边里的路由函数可以写死规则（Workflow），也可以调用 LLM 做动态决策（Planning）；Checkpointer 通过 thread\_id 标识执行线程，并保存 LangGraph 执行过程中的 State 快照，支持状态持久化、恢复和中断后继续执行。具体保存时机由图的执行机制决定，通常与 super-step 相关。

\## 9. 后续实践方向

先跑纯线性 Workflow：START → A → B → END，理解节点返回值如何合并进 State。



加条件路由：用 add\_conditional\_edges 实现“工具结果不同走不同分支”，路由函数只读 State，不调 LLM。



加循环：让条件边指回前面的节点，实现“不满足条件就重试”，理解一个 Loop 里会产生多个 Checkpoint。



加 Checkpointer + thread\_id：跑两次 invoke，验证同一 thread\_id 能续上历史，不同 thread\_id 互不串状态。



加中断：用 interrupt\_before 在某个节点前暂停，再用同一 thread\_id 恢复，理解“人工介入”的落点。



最后再引入 Planning：在条件边路由函数里调用 LLM 做动态决策，对比第2步的写死规则，体会“确定性 vs 动态性”的差异。



混合架构：外层用固定阶段（Workflow），内层用条件边 + LLM 路由（Planning），体会生产级“骨架固定、局部动态”的设计

