from typing import TypedDict

from langgraph.graph import StateGraph, END


# 1. 定义 State

class AgentState(TypedDict):
    message: str



# 2. 定义 Node

def hello_node(state):

    print("Node received:")
    print(state)

    return {
        "message": state["message"] + " -> processed"
    }



# 3. 创建 Graph

graph = StateGraph(AgentState)



# 4. 添加 Node

graph.add_node(
    "hello",
    hello_node
)



# 5. 设置入口

graph.set_entry_point(
    "hello"
)



# 6. 连接结束

graph.add_edge(
    "hello",
    END
)



# 7. 编译

app = graph.compile()



# 8. 运行

result = app.invoke(
    {
        "message":"hello"
    }
)


print(result)