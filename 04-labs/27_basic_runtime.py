
def fake_model(messages):
    """模拟模型：根据当前消息决定下一步。"""

    # 检查是否已经执行过天气工具
    has_tool_result = any(
        message["role"] == "tool"
        for message in messages
    )

    if not has_tool_result:
        return {
            "type": "tool_call",
            "tool": "get_weather",
            "arguments": {"city": "Tokyo"},
        }

    return {
        "type": "final",
        "content": "东京有降雨可能，建议带伞。",
    }


def get_weather(city):
    """模拟天气工具，不访问真实天气服务。"""
    print(f"[Tool] 正在查询 {city} 的天气")
    return f"{city}：有降雨可能"


def run_agent(user_input, max_steps=5):
    """最小 Agent Runtime：循环决策、执行工具、处理结果。"""

    messages = [
        {"role": "user", "content": user_input}
    ]

    print("[Runtime] 开始执行任务")

    for step in range(1, max_steps + 1):
        print(f"\n[Runtime] 第 {step} 轮执行")

        decision = fake_model(messages)

        if decision["type"] == "final":
            print("[Runtime] 任务完成")
            print("[Agent]", decision["content"])
            return decision["content"]

        if decision["type"] == "tool_call":
            if decision["tool"] == "get_weather":
                result = get_weather(
                    decision["arguments"]["city"]
                )
            else:
                raise ValueError(
                    f"未知工具：{decision['tool']}"
                )

            messages.append({
                "role": "tool",
                "content": result,
            })

    raise RuntimeError("超过最大执行步数，任务未完成")


if __name__ == "__main__":
    run_agent("查询东京天气，并建议我是否需要带伞")

