
"""
Minimal Tool Calling Runtime Lab

This is an educational simulation.
The model responses are predefined rules, not real LLM outputs.
"""

MAX_STEPS = 5


# 1. Tool: provides the actual capability.
def divide(a, b):
    if type(a) not in (int, float) or type(b) not in (int, float):
        raise TypeError("Both arguments must be numbers.")

    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")

    return a / b


TOOL_REGISTRY = {
    "divide": divide,
}


# 2. Simulated LLM: decides what to do.
# Later, we will replace this function with a real model API call.
def mock_llm(messages, scenario):
    tool_messages = [
        message for message in messages
        if message["role"] == "tool"
    ]

    # First decision: request a tool call.
    if not tool_messages:
        denominator = 0 if scenario == "tool_error" else 2

        tool_name = (
            "unknown_tool"
            if scenario == "unknown_tool"
            else "divide"
        )

        return {
            "type": "tool_call",
            "name": tool_name,
            "arguments": {
                "a": 10,
                "b": denominator,
            },
        }

    # Next decision: inspect the tool result.
    result = tool_messages[-1]

    if result["ok"]:
        return {
            "type": "final",
            "content": (
                f"Calculation succeeded. "
                f"Result: {result['result']}"
            ),
        }

    return {
        "type": "final",
        "content": (
            "The requested operation could not be completed. "
            f"Reason: {result['error']}"
        ),
    }

# 3. Runtime: coordinates model decisions and tool execution.
def run_agent(task, scenario="success"):
    print("\n" + "=" * 50)
    print(f"Task: {task}")
    print("=" * 50)

    messages = [
        {"role": "user", "content": task}
    ]

    for step in range(1, MAX_STEPS + 1):
        print(f"\n[Runtime] Step {step}: asking model")

        response = mock_llm(messages, scenario)
        print(f"[Runtime] Model response: {response}")

        if not isinstance(response, dict):
            print("[Runtime] Invalid model response. Stopping.")
            return

        action_type = response.get("type")

        # The model says the task is complete.
        if action_type == "final":
            print(f"\n[Final Answer] {response['content']}")
            return

        # The model requests a tool call.
        if action_type != "tool_call":
            print("[Runtime] Unknown action type. Stopping.")
            return

        tool_name = response.get("name")
        arguments = response.get("arguments")

        print(f"[Runtime] Requested tool: {tool_name}")
        print(f"[Runtime] Arguments: {arguments}")

        if not isinstance(arguments, dict):
            tool_result = {
                "role": "tool",
                "name": str(tool_name),
                "ok": False,
                "error": "Tool arguments must be a dictionary.",
            }

        else:
            tool = TOOL_REGISTRY.get(tool_name)

            if tool is None:
                tool_result = {
                    "role": "tool",
                    "name": str(tool_name),
                    "ok": False,
                    "error": f"Unknown tool: {tool_name}",
                }

            else:
                try:
                    value = tool(**arguments)

                    tool_result = {
                        "role": "tool",
                        "name": tool_name,
                        "ok": True,
                        "result": value,
                    }

                except Exception as exc:
                    tool_result = {
                        "role": "tool",
                        "name": tool_name,
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }

        print(f"[Runtime] Tool result: {tool_result}")

        # Return the observation to the model's conversation.
        messages.append(tool_result)

    print("[Runtime] Maximum steps reached. Stopping safely.")


if __name__ == "__main__":
    run_agent(
        "Calculate 10 divided by 2.",
        scenario="success",
    )

    run_agent(
        "Calculate 10 divided by 0.",
        scenario="tool_error",
    )

    run_agent(
        "Try to use an unavailable tool.",
        scenario="unknown_tool",
    )