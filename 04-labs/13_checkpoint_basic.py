from typing import TypedDict


# 定义State
class AgentState(TypedDict):
    task: str
    plan: str
    status: str



# 模拟Checkpoint
checkpoint = None



# Node 1
def planning_node(state: AgentState):

    print("\n[Planning Node]")

    state["plan"] = "Day1: Forbidden City, Day2: Great Wall"
    state["status"] = "planning_complete"

    return state



# 保存checkpoint

def save_checkpoint(state):

    global checkpoint

    checkpoint = state.copy()

    print("\n[Checkpoint Saved]")
    print(checkpoint)



# Node 2

def continue_node(state: AgentState):

    print("\n[Continue Node]")

    print("Current plan:")
    print(state["plan"])

    state["status"] = "finished"

    return state



# -----------------
# Agent运行
# -----------------

state = {

    "task":"Plan Beijing trip",

    "plan":"",

    "status":"start"

}


print("[Initial State]")
print(state)



# 第一步

state = planning_node(state)



# 保存状态

save_checkpoint(state)



# 模拟程序中断

print("\n!!! Agent stopped !!!")

state = None



# -----------------
# 恢复执行
# -----------------

print("\n=== Recover Agent ===")

state = checkpoint.copy()


print("[Recovered State]")
print(state)



# 继续执行

state = continue_node(state)



print("\n[Final State]")
print(state)