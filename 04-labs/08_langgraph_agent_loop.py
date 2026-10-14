from typing import TypedDict, List

from langgraph.graph import StateGraph, END


# =========================
# 1. 定义 State
# =========================

class AgentState(TypedDict):
    messages: List[str]


# =========================
# 2. LLM Node
# =========================

def llm_node(state: AgentState):

    messages = state["messages"]

    last_message = messages[-1]


    print("\n[LLM Node]")
    print("观察:", last_message)


    # 模拟模型决策

    if "weather" in last_message:

        return {
            "messages":
            messages +
            [
                "tool_call:get_weather"
            ]
        }


    else:

        return {
            "messages":
            messages +
            [
                "final:我无法处理该任务"
            ]
        }



# =========================
# 3. Tool Node
# =========================

def tool_node(state: AgentState):

    messages = state["messages"]


    print("\n[Tool Node]")
    print("执行天气查询")


    tool_result = "Beijing Sunny 25°C"


    return {
        "messages":
        messages +
        [
            f"tool_result:{tool_result}"
        ]
    }



# =========================
# 4. 判断下一步
# =========================

def should_continue(state:AgentState):

    last = state["messages"][-1]


    if last.startswith("tool_call"):

        return "tool"


    return "end"



# =========================
# 5. 创建 Graph
# =========================

graph = StateGraph(
    AgentState
)



# 添加节点

graph.add_node(
    "llm",
    llm_node
)


graph.add_node(
    "tool",
    tool_node
)



# 设置入口

graph.set_entry_point(
    "llm"
)



# 条件边

graph.add_conditional_edges(
    "llm",
    should_continue,
    {
        "tool":"tool",
        "end":END
    }
)



# tool执行后回到LLM

graph.add_edge(
    "tool",
    "llm"
)



# 编译

app = graph.compile()



# 执行

result = app.invoke(
    {
        "messages":
        [
            "please check weather"
        ]
    }
)


print("\nFinal State:")
print(result)