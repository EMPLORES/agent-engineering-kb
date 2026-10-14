"""
Day5 Experiment 2

Understand State Update and Reducer
"""


class AgentState:

    def __init__(self):
        self.messages = []
        self.tool_result = None



# -------------------------
# 模拟Runtime更新State
# -------------------------

def update_state(state, update):

    for key, value in update.items():

        if key == "messages":

            # 模拟Reducer:
            # 新messages追加，而不是覆盖

            state.messages.extend(value)


        else:

            # 普通字段直接更新

            setattr(
                state,
                key,
                value
            )



# -------------------------
# Node
# -------------------------

def user_node():

    return {
        "messages":[
            "User: What is weather?"
        ]
    }



def llm_node():

    return {
        "messages":[
            "AI: call weather tool"
        ]
    }



def tool_node():

    return {
        "messages":[
            "Tool: Sunny"
        ],
        "tool_result":"Sunny"
    }



# -------------------------
# Runtime
# -------------------------

def run():

    state = AgentState()


    nodes = [
        user_node,
        llm_node,
        tool_node
    ]


    for node in nodes:

        update = node()

        print(
            "\nNode:",
            node.__name__
        )

        print(
            "Update:",
            update
        )


        update_state(
            state,
            update
        )


        print(
            "Current State:",
            state.__dict__
        )



if __name__ == "__main__":

    run()