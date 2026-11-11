\# LangGraph Basic Graph Execution



\## 1. 研究目标

本次从 LangGraph 的基础 Graph Execution 开始的具体缘由，是将之前的LangGraph的state，node，edge以及conditional\_edge等内容串联在一起，构架成一个整体的框架，能够将所有内容串联起来




本次实验希望验证的内容如下：
工程概念： LangGraph 不只是让我们画出执行流程，而是让我们把执行流程构建成可以实际运行、重复调用和组合的程序对象。
工程边界:    Python 中存在一个函数，不等于这个函数已经成为 LangGraph 执行图的一部分。





本次实验聚焦基础 Graph 的构建、编译和执行，暂不涉及 LLM、Tool、Checkpoint、Persistence 等更复杂的机制。







\## 2. 核心 API 与职责



\### 2.1 StateGraph



\- StateGraph 是LangGraph提供的图构建器



\- 在本次实验中，StateGraph 用于创建图构建器，通过 builder 注册节点、配置边和执行关系，最后调用 compile() 生成可执行图对象 app。



\### 2.2 State

\- State 是当前任务执行过程中共享的状态数据集合，用于保存任务输入、中间处理结果以及最终结果。

Node 通过接收 State 获取当前任务数据，并通过返回部分 State 更新来修改需要更新的状态字段。





\### 2.3 Node



\- Node 是实现具体任务，执行具体任务代码
本次实验中有classify\_request，pricing\_node，general\_node
classify\_request：读取用户请求，判断请求类型，并更新 State 中的 request\_type。







pricing\_node：处理价格类请求，更新 response。







general\_node：处理普通请求，更新 response。	



\### 2.4 Edge

\- Edge 决定下一个去哪个node，负责协调流转节点
普通 Edge： 预先定义固定的节点流转关系，它不需要根据 State 动态判断下一步。
Conditional Edge： 根据路由函数的返回结果，动态选择后续执行节点。





\### 2.5 START 和 END

START 表示 Graph 的执行入口，END 表示 Graph 的执行终点。初始 State 由调用方准备，并通过 invoke() 传入图中。



\### 2.6 add\_conditional\_edges()

add\_conditional\_edges() 用于向 Graph 添加条件边，配置路由函数以及路由结果与目标节点之间的映射关系。



\- Router 函数负责根据当前 State 判断后续执行方向，并返回路由结果。







\### 2.7 compile() 和 invoke()



\- compile()：构建可执行图对象。


\- invoke()：传入初始 State，启动一次图执行，并返回最终 State。





\## 3. Graph 的实际执行流程



结合 Experiment33 的代码，说明：

1.StateGraph(AgentState)

&#x20;       ↓

&#x20;     builder

&#x20;       ↓

注册 Node、配置 Edge 和路由

&#x20;       ↓

&#x20;  builder.compile()

&#x20;       ↓

&#x20;      app



2.调用方先准备初始 State，然后通过 invoke(initial\_state) 将其传入可执行图，启动任务执行。





3\. classify\_request 更新 State 中的 request\_type，随后 route\_request 读取该字段，决定下一节点的执行方向。


4\. Graph 执行到条件路由位置时，调用 route\_request。Router 读取当前 State 中的 request\_type，返回 "pricing" 或 "general"，再根据预先配置的映射关系选择对应的业务节点。



5\. 后续业务节点都是在每一个定义的node中完成对应职责后直接进行相应的state的更新，当前实验中router\_request不修改 State，而两个业务处理节点会更新 response



6\. 根据先前定义的图的执行关系，根据执行逻辑最终到达END返回结果，执行到 END 后，invoke() 返回最终 State，调用方可以从中读取 response。







\## 4. 关键工程理解



\### 4.1 Node 与 Router 的区别

Node 负责执行具体任务，并可以返回 State 更新


Router 负责读取当前 State，判断后续执行方向并返回路由结果。它配合 Conditional Edge 实现动态路由；普通 Edge 则直接按照预先定义的连接关系执行。



\### 4.2 Python 函数定义与 Graph 节点注册的区别

Python 函数定义后就可以被 Python 代码直接调用，但这不代表它已经成为 LangGraph 执行图的一部分。若希望 LangGraph 将其作为 Graph 节点执行，需要通过 add\_node() 注册，并配置相应的图连接关系。





\### 4.3 修改 Graph 结构后，为什么需要重新 compile()？



不是每次修改业务数据都需要重新编译，而是当 Graph 的结构发生变化，例如新增节点、修改边和路由关系时，需要重新编译，生成反映新结构的可执行图对象





\### 4.4 为什么正常重复执行任务时可以复用编译后的 app？

正常重复执行任务时，当前可执行图对象的架构并没有发生改变，节点还是原来的并不需要添加或减少，对应的逻辑以及触发条件也没有发生改变，所以可以直接复用编译后的app来重复执行任务



\## 5. 实验验证



\- 实验文件：`04-labs/33\_langgraph\_basic\_graph.py`

\- 运行命令：python 04-labs/33\_langgraph\_basic\_graph.py

\- 测试输入一及执行结果：这个产品多少钱？------	pricing（路由结果）------这是一个价格类请求，需要查询产品价格。（最终回答）

\- 测试输入二及执行结果：介绍一下这个产品。-------	general（路由结果）-----这是一个普通请求，可以介绍产品信息。（最终回答）

\- 验证了 State 在节点之间的传递和更新。







验证了 Conditional Edge 根据 Router 返回值选择目标节点。







验证了编译后的 Graph 可以接收不同输入并返回不同结果。

\- 本次实验还没有验证：

LLM 调用。







Tool 调用。







Checkpoint 和持久化。







中断与恢复。







多 Agent 协作



这些不是本次实验的目标



\## 6. 本次研究总结

1\. LangGraph 使用 StateGraph 构建基于共享 State 的执行图，通过builder注册节点、配置边和路由关系定义执行流程，再通过 compile() 生成可执行图对象。



2\. 从构建 Graph 到执行 Graph，完整过程是：
创建 StateGraph

&#x20;   ↓

构建 builder

&#x20;   ↓

注册节点、配置边和路由

&#x20;   ↓

compile()

&#x20;   ↓

生成 app

&#x20;   ↓

准备 initial\_state

&#x20;   ↓

invoke(initial\_state)

&#x20;   ↓

执行 Graph

&#x20;   ↓

返回最终 State



3\. 这套机制能够将原本分散的 Python 函数组织成具有明确执行关系的工作流，通过 State 在不同节点之间共享任务信息，并通过条件路由让不同任务进入不同的处理路径。这为后续构建具有多个执行节点的真实 Agent 系统提供了基础。

