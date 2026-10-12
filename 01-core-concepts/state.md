\# State





\## 1. 一句话定义



State 是 Agent 在一次任务执行过程中维护的当前状态信息集合，包括任务信息、执行结果、中间数据以及控制流程所需的信息。



\## 2. 解决的问题



State解决了Agent在多步骤任务中无法保存执行过程和中间结果的问题。



通过持续更新State，Agent可以根据最新状态重新判断下一步行动，而不是每次都从零开始。



\## 3. Agent架构中的位置

state充当agent当前任务状态的角色，能够告诉agent当前的任务状况，提供一个参考内容以便后续不断进行动态思考，State位于Runtime管理的执行过程中，是连接LLM决策、Tool执行和下一轮循环的重要数据结构。



\## 4. State vs Messages

messages通常只是State中的一个字段，用于保存对话历史。

State还可能包含工具结果、任务状态、中间变量等信息。



\## 5. State vs Context

state：当前的任务状态的所有内容
context：是由runtime通过context builder建立起的，内容主要是基于当前user task挑选出可以作为LLM进行观察然后做出decision的参考，Context是State经过筛选、压缩和组织后提供给LLM的一次观察视图。



\## 6. State vs Memory

state：当前的任务状态的所有内容
memory：跨任务，跨对话长期存储和是否值得未来使用的内容
主题性质不同：state是基于当前任务的状态内容，memory更多的是基于跨任务或跨对话需要长期存储和值得未来使用的内容



\## 7. State如何影响Agent Loop

State会随着不同Node执行不断变化。每次State更新后，Agent都会基于新的状态重新判断下一步行动，从而形成Agent Loop。



\## 8. StateGraph中的作用

在抽象或复杂的生产级agent的情况下，StateGraph描述State如何经过不同Node处理产生变化，以及不同状态之间如何根据条件进行流转。



\## 9. 最小实现



State与Memory区别实验：class AgentState:



&#x20;   def \_\_init\_\_(self):

&#x20;       # 当前任务的信息

&#x20;       self.current\_task = None

&#x20;       

&#x20;       # 当前任务执行产生的信息

&#x20;       self.tool\_result = None







class Memory:



&#x20;   def \_\_init\_\_(self):

&#x20;       # 长期保存的信息

&#x20;       self.user\_preferences = {}







\# 当前一次 Agent 运行



state = AgentState()



memory = Memory()







\# 用户当前任务



state.current\_task = "Find weather in Beijing"







\# 当前任务执行结果



state.tool\_result = "Sunny"







\# 长期用户信息



memory.user\_preferences\[

&#x20;   "activity"

] = "User likes outdoor activities"







print("State:")

print(vars(state))





print("\\nMemory:")

print(memory.user\_preferences)



\## 10. 我的理解



之前我认为Agent主要是LLM调用工具解决问题。



学习State之后，我理解Agent真正区别于普通API调用的地方，是它能够保存任务执行过程中的状态，并根据状态变化不断调整下一步决策。



State不是简单的数据存储，而是连接Runtime、LLM和Tool的重要信息载体。





\## 11. 当前疑问



\- LangGraph中的State具体如何定义和管理？

\- StateGraph如何实现Node之间的状态传递？

\- Checkpoint如何保存和恢复State？

\- Context Builder在真实Agent中如何设计？

\- 大规模Agent中如何避免State无限增长？

