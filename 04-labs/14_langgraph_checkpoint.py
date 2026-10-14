from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


# ----------------------
# 定义 State
# ----------------------

class AgentState(TypedDict):
    task: str
    progress: str



# ----------------------
# Node
# ----------------------

def planning_node(state: AgentState):

    print("\n[Planning Node]")

    return {
        "progress": "Planning completed"
    }



def continue_node(state: AgentState):

    print("\n[Continue Node]")

    print("Current state:")
    print(state)

    return {
        "progress": "Task finished"
    }



# ----------------------
# 创建 Graph
# ----------------------

graph = StateGraph(AgentState)


graph.add_node(
    "planning",
    planning_node
)


graph.add_node(
    "continue",
    continue_node
)


graph.add_edge(
    START,
    "planning"
)


graph.add_edge(
    "planning",
    "continue"
)


graph.add_edge(
    "continue",
    END
)



# ----------------------
# 添加 Checkpointer
# ----------------------

checkpointer = MemorySaver()


app = graph.compile(
    checkpointer=checkpointer
)



# ----------------------
# 第一次运行
# ----------------------

config = {
    "configurable": {
        "thread_id": "travel_task_001"
    }
}


print("=== First Run ===")


result = app.invoke(
    {
        "task": "Plan Beijing trip",
        "progress": "Start"
    },
    config=config
)


print("\nFinal result:")
print(result)



# ----------------------
# 查看保存状态
# ----------------------

print("\n=== Checkpoint ===")


checkpoint = app.get_state(config)


print(checkpoint.values)