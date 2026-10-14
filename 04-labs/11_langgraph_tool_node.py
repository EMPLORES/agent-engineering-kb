"""
Day5 Experiment:
Simulate LangGraph ToolNode workflow

Flow:

State
 ↓
LLM Node
 ↓
ToolNode
 ↓
ToolMessage
 ↓
State Update
 ↓
LLM Node
 ↓
Final
"""


class AgentState:
    def __init__(self):
        self.messages = []


# -------------------------
# Tool
# -------------------------

def get_weather(city):
    return {
        "city": city,
        "weather": "Sunny",
        "temperature": "25°C"
    }


TOOLS = {
    "get_weather": get_weather
}


# -------------------------
# LLM Node
# -------------------------

def llm_node(state):

    # 第一次：
    # 根据任务决定调用工具

    if not state.messages:

        return {
            "type": "tool_call",
            "name": "get_weather",
            "arguments": {
                "city": "Beijing"
            }
        }

    # 第二次：
    # 看到ToolMessage后生成最终答案

    tool_message = state.messages[-1]

    return {
        "type": "final",
        "content": (
            f"The weather in {tool_message['city']} "
            f"is {tool_message['weather']} "
            f"with temperature {tool_message['temperature']}."
        )
    }


# -------------------------
# ToolNode
# -------------------------

def tool_node(tool_call):

    tool_name = tool_call["name"]

    arguments = tool_call["arguments"]

    print(f"[ToolNode] Calling tool: {tool_name}")

    tool = TOOLS[tool_name]

    result = tool(**arguments)


    # ToolNode产生ToolMessage

    tool_message = {
        "role": "tool",
        **result
    }

    return tool_message



# -------------------------
# Runtime
# -------------------------

def run_agent():

    state = AgentState()


    for step in range(5):

        print(
            f"\n[Runtime] Step {step + 1}"
        )


        response = llm_node(state)


        print(
            "[LLM Node]",
            response
        )


        if response["type"] == "tool_call":

            tool_message = tool_node(response)


            print(
                "[ToolNode] Result:",
                tool_message
            )


            # Runtime更新State

            state.messages.append(
                tool_message
            )


        elif response["type"] == "final":

            print(
                "\n[Final Answer]",
                response["content"]
            )

            break



if __name__ == "__main__":

    run_agent()