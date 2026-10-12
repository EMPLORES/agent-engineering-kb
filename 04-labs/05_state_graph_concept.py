class AgentState:
    def __init__(self, task):
        self.task = task
        self.decision = None
        self.tool_result = None
        self.status = "running"


# Node 1:
# 负责思考下一步行动
def agent_node(state):

    print("\n[Agent Node]")
    print("Current state:")
    print(vars(state))

    if state.tool_result is None:
        state.decision = {
            "type": "tool_call",
            "tool": "divide",
            "args": {
                "a": 10,
                "b": 2
            }
        }

    else:
        state.decision = {
            "type": "final",
            "content": f"Result is {state.tool_result}"
        }

    return state


# Node 2:
# 负责执行工具
def tool_node(state):

    print("\n[Tool Node]")

    args = state.decision["args"]

    result = args["a"] / args["b"]

    state.tool_result = result

    print("Tool result:", result)

    return state



# Edge:
# 决定下一步去哪

def router(state):

    if state.decision["type"] == "tool_call":
        return "tool"

    elif state.decision["type"] == "final":
        return "end"



def run():

    state = AgentState(
        "Calculate 10 divided by 2."
    )


    while True:

        # Agent Node
        state = agent_node(state)


        next_step = router(state)


        if next_step == "tool":

            state = tool_node(state)


        elif next_step == "end":

            print("\n[Final]")
            print(
                state.decision["content"]
            )
            break



if __name__ == "__main__":
    run()