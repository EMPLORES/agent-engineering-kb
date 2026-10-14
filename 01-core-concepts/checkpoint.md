\# Checkpoint





\## 1. 一句话定义



Checkpoint是Agent运行过程中某个时间点State的快照，用于保存执行状态，使Agent能够在中断后恢复运行。



\## 2. 解决的问题

Checkpoint解决Agent长时间运行过程中的状态保存问题。

当Agent因为系统中断、人工审批等待或者任务暂停时，可以通过Checkpoint恢复之前的执行状态。



\## 3. Agent架构中的位置

Checkpoint位于Agent Runtime执行流程中，负责保存State，使Agent具备暂停、恢复和长期运行能力。



\## 4. State vs Checkpoint

state是当前任务运行过程中的全部状态。，checkpoint是某一时间点下state的快照



\## 5. Checkpoint vs Memory

checkpoint是某一时刻下state的快照，memory是跨任务或跨会话长期保存的内容或具有长期价值的内容



Checkpoint关注：

“这一次任务运行到哪里了。”



Memory关注：

“未来任务还能使用什么信息。”



\## 6. Human-in-the-loop中的作用

Human-in-the-loop需要Agent暂停等待人工决策。



Checkpoint保存暂停时的State，使人工批准后Agent能够从之前的位置继续执行，而不是重新开始。



\## 7. thread\_id的作用

thread\_id用于区分不同Agent运行实例。



同一个Graph可以通过不同thread\_id保存不同任务的State。



\## 8. LangGraph中的Checkpoint

LangGraph通过Checkpointer机制实现Checkpoint。



Graph执行过程中，Checkpoint会在特定执行阶段保存State快照。



通过thread\_id区分不同运行实例。



恢复运行时，LangGraph根据thread\_id读取对应Checkpoint，并继续之前的执行流程。



\## 9. 最小实现

D:\\Projects\\agent-engineering-kb>python 04-labs/14\_langgraph\_checkpoint.py

=== First Run ===



\[Planning Node]



\[Continue Node]

Current state:

{'task': 'Plan Beijing trip', 'progress': 'Planning completed'}



Final result:

{'task': 'Plan Beijing trip', 'progress': 'Task finished'}



=== Checkpoint ===

{'task': 'Plan Beijing trip', 'progress': 'Task finished'}


实验验证：



MemorySaver保存Graph运行结束后的State，并可以通过get\_state读取Checkpoint。

\## 10. 我的理解

checkpoint不是新的状态，而是某一时间点下state的快照。state负责录Agent当前运行情况，而Checkpoint负责保证这些状态可以被保存和恢复，使Agent能够支持长时间任务和人工介入。



\## 11. 当前疑问

\- LangGraph Checkpointer如何实现数据库持久化？

\- 多节点执行过程中Checkpoint保存在哪个时间点？

\- Resume时如何恢复执行位置？

