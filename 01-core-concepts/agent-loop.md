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
该实验展示：

第一次模型调用：LLM根据任务决定调用工具。



第二次模型调用：Runtime将工具结果反馈给模型，模型根据新的Observation生成最终答案。



两次模型调用的输入上下文不同，

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

