"""
Day 2 Task 3
Reasoning Agent Loop

Goal:
Understand:
Tool result is not final answer.
LLM needs another reasoning step.
"""


# -----------------------------
# Tool
# -----------------------------

def get_weather(city):

    data = {
        "Beijing": {
            "weather": "Sunny",
            "temperature": 25
        }
    }

    return data.get(
        city,
        {
            "weather": "Unknown",
            "temperature": None
        }
    )


TOOL_REGISTRY = {
    "get_weather": get_weather
}



# -----------------------------
# Mock LLM
# -----------------------------

def mock_llm(messages):

    last = messages[-1]


    # First reasoning:
    # Need external information
    if last["role"] == "user":

        return {
            "type": "tool_call",
            "name": "get_weather",
            "arguments": {
                "city": "Beijing"
            }
        }


    # Second reasoning:
    # Analyze tool result
    if last["role"] == "tool":

        weather = last["result"]


        if (
            weather["weather"] == "Sunny"
            and weather["temperature"] <= 30
        ):

            return {
                "type": "final",
                "content":
                    "天气晴朗，温度适中，适合出去活动。"
            }


        return {
            "type": "final",
            "content":
                "天气条件一般，不建议外出。"
        }



# -----------------------------
# Agent Runtime
# -----------------------------

def run_agent(task, max_steps=5):


    messages = [
        {
            "role": "user",
            "content": task
        }
    ]


    for step in range(1, max_steps + 1):

        print(
            f"\n[Runtime] Step {step}: asking model"
        )


        response = mock_llm(messages)


        print(
            "[Runtime] Model response:",
            response
        )


        # Final answer
        if response["type"] == "final":

            print(
                "\n[Final Answer]",
                response["content"]
            )

            return



        # Tool request

        if response["type"] == "tool_call":


            tool_name = response["name"]

            arguments = response["arguments"]


            print(
                "[Runtime] Calling tool:",
                tool_name
            )


            tool = TOOL_REGISTRY[tool_name]


            result = tool(**arguments)


            tool_result = {

                "role": "tool",

                "name": tool_name,

                "result": result
            }


            print(
                "[Runtime] Observation:",
                tool_result
            )


            messages.append(tool_result)



    print(
        "[Runtime] Max steps reached"
    )



# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":

    run_agent(
        "北京天气怎么样？适合出去玩吗？"
    )