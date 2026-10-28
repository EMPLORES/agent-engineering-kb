
def mock_agent(context, state):
    """模拟 Agent 根据当前上下文和任务状态决定输出。"""

    destination = context.get("destination")

    if not destination:
        return "缺少目的地信息，无法制定具体行程"

    if state["status"] == "completed":
        return f"前往 {destination} 的行程已经完成"

    if state["status"] == "pending":
        return f"准备开始规划前往 {destination} 的行程"

    return f"正在规划前往 {destination} 的行程"


# Context：当前可以使用的信息
context = {
    "destination": "北京"
}

# State：当前任务的执行状态
state = {
    "status": "pending"
}

print("情况一：")
print(mock_agent(context, state))

print("\n情况二：")
state["status"] = "completed"
print(mock_agent(context, state))

print("\n情况三：")
context.pop("destination")
state["status"] = "pending"
print(mock_agent(context, state))

