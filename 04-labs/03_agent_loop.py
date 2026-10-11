"""
Day 2: Minimal Agent Loop

Goal:
Understand how Agent repeatedly:
1. Ask model
2. Decide action
3. Execute tool
4. Observe result
5. Continue or finish
"""


# -----------------------------
# Tools
# -----------------------------

def get_weather(city):
    """
    Simulated weather tool
    """
    weather_data = {
        "Beijing": "Sunny, 25°C",
        "Tokyo": "Cloudy, 20°C",
    }

    return weather_data.get(city, "Unknown city")


TOOL_REGISTRY = {
    "get_weather": get_weather,
}


# -----------------------------
# Mock LLM
# -----------------------------

def mock_llm(messages):
    """
    Simulate model decision.

    The model decides:
    - call a tool
    - or return final answer
    """

    last_message = messages[-1]

    # First step:
    # Model decides it needs weather information
    if last_message["role"] == "user":

        return {
            "type": "tool_call",
            "name": "get_weather",
            "arguments": {
                "city": "Beijing"
            }
        }


    # Second step:
    # Model sees tool result and finishes
    if last_message["role"] == "tool":

        return {
            "type": "final",
            "content": (
                f"The weather information is: "
                f"{last_message['result']}"
            )
        }


# -----------------------------
# Agent Runtime Loop
# -----------------------------

def run_agent(task, max_steps=5):

    messages = [
        {
            "role": "user",
            "content": task
        }
    ]


    for step in range(1, max_steps + 1):

        print(f"\n[Runtime] Step {step}: asking model")


        response = mock_llm(messages)


        print(
            "[Runtime] Model response:",
            response
        )


        # Model decides final answer
        if response["type"] == "final":

            print(
                "\n[Final Answer]",
                response["content"]
            )

            return


        # Model requests tool
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


            # Important:
            # Return observation to model
            messages.append(tool_result)



    print(
        "[Runtime] Maximum steps reached"
    )



# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":

    run_agent(
        "What is the weather in Beijing?"
    )