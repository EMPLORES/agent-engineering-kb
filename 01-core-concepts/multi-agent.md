\# Multi-Agent



\## 1. 一句话定义

Multi-Agent 系统是由多个具有不同职责或能力的 Agent 组成，并通过任务分工、信息传递和协作完成目标的系统。Supervisor 是其中一种常见的协调模式，负责组织其他 Agent 的执行、根据返回结果决定下一步，并在需要时汇总最终结果。







\## 2. Multi-Agent 解决什么问题？

Multi-Agent 通过多个 Agent 的职责分工与结果交互完成协作。在 Supervisor 模式中，协调者统一组织执行流程，并根据各 Agent 的返回结果决定下一步。明确的协调结构也便于后续增加最大重试次数、异常处理、人工审批或其他 Agent。	



当单个 Agent 已经能够以合理的成本和可靠性完成任务，且没有明显的专业分工、独立验证或并行处理需求时，就没有必要仅仅为了使用多 Agent 而增加协作角色。



\## 3. Supervisor 模式

\- Supervisor Agent：负责协调执行顺序，传递反馈，判断是否继续或结束，协调各个Agent之间的信息流转，根据审核结果决定下一步



\- Researcher Agent：负责提出初始方案，根据审核反馈修改方案，并返回方案内容及相关依据



\- Reviewer Agent：负责独立检查方案，反馈审核结果和修改建议



Supervisor Agent 根据 Reviewer Agent 返回的审核状态和修改意见，决定是输出最终结果，还是将修改意见反馈给 Researcher Agent，使其重新生成方案并进入下一轮审核。





\## 4. Multi-Agent 的协作闭环



```text

任务输入

  ↓

Supervisor 分配任务

  ↓

Researcher 提出方案

  ↓

Reviewer 审核方案

  ↓

结果返回 Supervisor

  ↓

根据审核结果决策

  ├─ 审核通过 → 输出最终结果

  └─ 审核未通过 → 将修改意见返回 Researcher

                         ↓

                       重新生成方案并再次审核

                         ↓

                       直到通过或达到最大尝试次数仍未通过

                         ↓

                       结束迭代，返回当前结果和审核状态

```



\## 5. Supervisor 的实现方式



分别解释以下三种实现方式：



\### 5.1 Python 规则驱动的 Supervisor

通过 Python 编排，配合工作流引擎、状态管理、持久化、重试、日志和异常处理来组织执行，进一步增加条件路由、循环、持久化和恢复机制，它仍然可以承担更复杂的协调工作。



优势在于行为可预测，试错成本低，适合实验测试，局限在于需要将关键判断转化为明确的规则；对于难以预先定义的语义判断和开放式决策，固定规则可能不够灵活。



\### 5.2 LLM Supervisor

当任务需要理解自然语言、综合多个 Agent 的意见，或者根据上下文动态判断下一步时，可以考虑使用 LLM Supervisor。LLM 可以根据各 Agent 返回的结果提出决策，但其输出仍可能存在不稳定、判断错误或意见冲突等问题，因此需要相应的验证和执行约束。当不同 Agent 的结果相互矛盾时，Supervisor 还需要判断如何解决冲突，不能默认 LLM 的判断一定正确。





\### 5.3 混合式 Supervisor

使用 LLM 处理难以完全通过固定规则表达的语义理解和动态决策任务，再由 Python 工作流执行权限检查、重试限制、状态更新和最终路由，在保留一定灵活性的同时提高可控性和可预测性。

\## 6. Multi-Agent 与 Handoff、Workflow、Planning 的关系



分别说明它们的职责，以及它们如何组合使用。



\### 6.1 Multi-Agent 与 Handoff

Handoff 是 Multi-Agent 系统中可以采用的一种任务交接机制，用于将任务处理权从当前 Agent 转交给目标 Agent。但 Multi-Agent 也可以通过普通函数调用、Agent-as-Tool 或 Workflow 编排等方式实现协作，并不一定需要 Handoff。



在 Supervisor 模式下，Supervisor 可以通过调用其他 Agent 并接收返回结果来组织协作，也可以根据具体架构采用 Handoff。两种方式的区别在于预期的控制流程，而不是是否存在多个 Agent。





Agent-as-Tool 适用于主 Agent 需要借助专业 Agent 的能力，但希望保留控制权并继续整合其返回结果的场景。Handoff 适用于当前 Agent 判断应当由另一个 Agent 接管后续处理的场景。两种方式也可以组合使用，具体取决于系统需要如何组织控制流程。



\### 6.2 Multi-Agent 与 Workflow

Workflow 通过节点连接和路由规则组织执行流程。条件路由可以根据当前 State 或执行结果选择预先定义的分支，包括成功、失败和异常处理路径。路由规则可以是固定条件，也可以在特定设计下结合 LLM 进行动态判断。







Workflow 可以用于单 Agent，也可以用于 Multi-Agent 系统，负责组织不同节点或 Agent 的执行顺序、连接关系和控制流转。



\### 6.3 Multi-Agent 与 Planning

Planning 负责生成或调整任务计划，包括任务步骤、执行顺序和策略。计划可以根据运行过程中获得的新信息进行修改。



Workflow 负责组织节点之间的连接关系，并通过路由规则决定下一步执行哪个节点或分支。Supervisor 可以根据任务需要使用固定规则或 LLM 生成、调整计划，再由 Workflow 组织执行过程。Multi-Agent 则通过多个 Agent 的专业分工与结果交互完成协作。



三者可以配合工作，但各自职责不同：Planning 关注做什么以及如何安排步骤；Workflow 关注步骤之间如何连接与流转；Multi-Agent 关注多个 Agent 如何分工与协作。



\## 7. 本次 Python 实验的收获

本次实验通过 Python 模拟 Supervisor 协调多个 Agent，验证了职责分工、结果传递、条件决策、反馈循环和最大尝试次数限制。



Supervisor 将 Reviewer 返回的 suggestion 保存为 feedback，再通过函数参数传递给下一轮 Researcher；同时根据 approved 判断是否结束循环，未通过时继续迭代，达到最大尝试次数时停止。



当前实验使用普通 Python 函数模拟 Agent，没有接入真实 LLM，也没有执行真实的外部任务。审核逻辑只是通过预定义字符串条件判断方案是否符合要求，因此尚未验证 LLM 推理质量或真实任务执行能力。当前还未实现并行执行、持久化与中断恢复、复杂异常处理、运行追踪，以及更可靠的审核机制。

\- \*\*Researcher Agent：\*\* 提出初始方案，并根据 Reviewer 的反馈修改方案。

\- \*\*Reviewer Agent：\*\* 检查 Researcher 给出的方案，返回审核状态和修改建议。

\- \*\*Supervisor Agent：\*\* 负责组织执行顺序，将审核意见传递给 Researcher，并根据审核结果决定继续迭代还是结束。



\## 8. 当前阶段的学习结论



Multi-Agent 适用于需要多个专业角色分工、相互验证或迭代协作的任务，但多个 Agent 并不天然优于单 Agent。



Supervisor 是一种常见的协调模式，可以根据其他 Agent 的返回结果决定下一步。



Python 规则、LLM Supervisor 和混合式 Supervisor 各有适用场景，应根据任务的动态性、可靠性和成本进行选择。



Multi-Agent、Handoff、Workflow 和 Planning 解决的是不同层面的问题，可以组合使用，但不能互相替代。



增加 Agent 数量也会增加通信、协调、延迟、成本和错误处理的复杂度，因此应当以实际需求决定是否引入多 Agent。

