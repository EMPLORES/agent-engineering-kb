\# Agent Loop





\## 1. 一句话定义

Agent Loop是指Runtime根据模型的输出的决策，不断协调模型推理，工具执行，状态更新和结果反馈，直达任务完成或达到终止任务条件的循环过程



\## 2. 解决的问题

传统API是需要设计者提前规划好所有流程

而Agent Loop是根据不断更新的动态信息，动态调成思考和判断最终给出decision，得到final的过程，从而处理更复杂和开放性的任务



\## 3. 在Agent架构中的位置

Agent Loop是Agent运行时的核心控制机制，它连接LLM,Tool，state，memory，runtime，使这些组件形成持续进行的过程



\## 4. 执行流程

User Task



↓



Runtime



↓



State



↓



Context Builder



↓



LLM



↓



Decision



↓



Tool Calling



↓



Runtime



↓



Tool Execution



↓



Observation



↓



State Update



↓



再次进入Loop



\## 5. 最小实现

Step 1: asking model

\[Runtime] Model response: {'type': 'tool\_call', 'name': 'get\_weather', 'arguments': {'city': 'Beijing'}}

\[Runtime] Calling tool: get\_weather

\[Runtime] Observation: {'role': 'tool', 'name': 'get\_weather', 'result': {'weather': 'Sunny', 'temperature': 25}}



\[Runtime] Step 2: asking model

\[Runtime] Model response: {'type': 'final', 'content': '天气晴朗，温度适中，适合出去活动。'}



\## 实验观察



第一次模型调用：



LLM根据用户任务判断需要调用工具，并生成tool\_call。



第二次模型调用：



Runtime执行工具后，将Observation反馈给LLM。



LLM基于新的上下文重新推理，生成最终回答。



两次模型调用接收到的上下文不同，

因此产生不同决策。



\[Final Answer] 天气晴朗，温度适中，适合出去活动。



\## 6. Runtime / LLM / Tool关系

Runtime负责解析决策，调用工具，反馈结果，管理执行进程，更新状态以及控制循环，LLM负责根据当前上下文理解任务，并提出下一步行动建议。，tool负责提供具体能力，例如搜索、数据库查询、计算、API调用



\## 7. 我的理解

Agent Loop不是LLM自己循环，而是Runtime控制LLM、Tool、State之间不断交互。LLM负责理解任务并判断下一步行动。Runtime负责执行行动、维护运行流程，并根据结果决定是否继续循环。从本质上看，Agent Loop让LLM从一次性的回答模型，变成可以根据环境反馈不断调整行动的执行系统。



\## 当前疑问



1\. Runtime如何判断LLM返回的是tool\_call还是final？



2\. State更新是在Runtime内部完成还是由具体框架完成？



3\. LangGraph中的Graph Loop和普通while循环有什么区别？



4\. 多Agent情况下Loop如何管理？

\## 8. 实验



\### Experiment 1

Minimal Agent Loop



目标：

为了验证：

LLM

↓

Tool Calling

↓

Runtime

↓

Tool

↓

Observation

↓

Final





代码：04-labs/03\_reasoning\_agent\_loop.py

观察：模型第一次产生tool\_call，第二次根据tool结果生成final。



\## 9. 后续研究问题

\## 后续研究问题



\- Agent Loop和ReAct有什么关系？

\- 为什么LLM需要Runtime才能形成Agent？

\- State如何保存循环过程中的信息？

\- Context Builder如何决定哪些信息提供给模型？

\- LangGraph如何实现Loop控制？

\- OpenAI Agents SDK Runner如何管理Loop？

\- 如何避免无限循环？

\- 如何评估Agent Loop质量？


\## 10. Agent Loop 与 LangGraph Graph架构的关系

Agent Loop描述的是Agent不断观察、决策、执行、获得反馈并继续循环的过程。



LangGraph Graph架构是在Agent Loop基础上，将原本隐藏在代码中的执行流程，通过State、Node、Edge等结构显式表达出来。



\## 10.1 Agent Loop 与 LangGraph 的关系

Agent Loop是LangGraph设计的基础。



Agent Loop描述Agent运行过程中不断观察、决策、执行和反馈的循环机制。



LangGraph则进一步将这种循环机制抽象为Graph结构，通过State保存状态，通过Node执行动作，通过Edge控制节点之间的流转。



因此LangGraph不是替代Agent Loop，而是一种管理和实现Agent Loop的方法。



\## 10.2 Day2 Runtime Loop 与 LangGraph 的区别

Day2 Runtime Loop中，Agent的控制逻辑通过while循环、if判断等代码结构实现，状态主要通过messages等简单结构维护。



LangGraph则将状态管理和执行流程进一步抽象，通过Graph结构明确表示状态变化、节点执行以及条件分支。



\## 10.3 Node、Edge、Conditional Edge

Node：



Node是Graph中的执行单元，负责读取当前State，并根据自身逻辑产生新的State。





Edge：



Edge负责连接不同Node，决定一个Node执行完成后流向哪个Node。





Conditional Edge：



Conditional Edge根据当前State中的信息或者执行结果进行判断，动态选择下一步执行路径。



\## 10.4 Router在Agent中的作用

Router负责根据当前状态判断下一步执行方向，它通常读取State，然后返回目标节点名称。Router负责决定路径，但是不负责执行节点中的具体任务。



\## 10.5 为什么生产级Agent需要Graph结构

简单Agent可以通过while循环实现。



但是生产级Agent通常包含：



\- 多步骤任务

\- 多工具调用

\- 条件分支

\- 人工审批

\- 错误恢复

\- 长时间运行任务



如果所有逻辑都写在Runtime代码中，随着复杂度增加会越来越难维护。



Graph结构将Agent执行流程显式化，使状态变化和执行路径更加清晰。



\## 10.6 Agent Loop在LangGraph中的执行流程

State



↓



LLM Node



↓



Decision



↓



Conditional Edge



↓



Tool Node / END



↓



State Update



↓



继续Loop



\## 10.7 我的理解



Agent Loop和LangGraph不是两个不同的Agent实现方式，而是不同层次的抽象。



Agent Loop描述Agent如何不断根据反馈调整行动。



LangGraph则将这种循环过程通过Graph结构进行管理。



Day2让我理解Agent如何运行，而Day4让我理解生产级框架为什么需要使用Graph组织这种运行过程。



\## 10.8 当前疑问



\- LangGraph中的State如何真正管理复杂任务信息？

\- Tool Node如何连接真实工具调用？

\- Graph如何实现任务暂停和恢复？

\- 多Agent情况下Graph如何组织？



