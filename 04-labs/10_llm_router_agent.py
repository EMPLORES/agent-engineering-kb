from typing import TypedDict

from langgraph.graph import StateGraph, END



# =========================
# 1. State
# =========================

class AgentState(TypedDict):

    task: str

    decision: str

    tool_result: str



# =========================
# 2. LLM Node
# =========================

def llm_node(state):

    print("\n[LLM Node]")
    print("Task:", state["task"])


    # 模拟 LLM 判断

    if "weather" in state["task"]:

        decision = "tool_call"

    else:

        decision = "final"



    return {

        "decision": decision

    }



# =========================
# 3. Router
# =========================

def router(state):

    print("\n[Router]")
    print("Decision:", state["decision"])


    if state["decision"] == "tool_call":

        return "tool"


    return "end"



# =========================
# 4. Tool Node
# =========================

def tool_node(state):

    print("\n[Tool Node]")

    result = "Beijing Sunny 25°C"


    return {

        "tool_result": result,

        "decision": "final"

    }



# =========================
# 5. Graph
# =========================

graph = StateGraph(
    AgentState
)



graph.add_node(
    "llm",
    llm_node
)


graph.add_node(
    "tool",
    tool_node
)



graph.set_entry_point(
    "llm"
)



graph.add_conditional_edges(

    "llm",

    router,

    {

        "tool":"tool",

        "end":END

    }

)



graph.add_edge(
    "tool",
    END
)



app = graph.compile()



# =========================
# 6. Test
# =========================


print("===================")
print("Case 1")
print("===================")


result = app.invoke(

    {

        "task":
        "check weather",

        "decision":"",

        "tool_result":""

    }

)


print("\nFinal State:")
print(result)



print("\n===================")
print("Case 2")
print("===================")


result = app.invoke(

    {

        "task":
        "say hello",

        "decision":"",

        "tool_result":""

    }

)


print("\nFinal State:")
print(result)