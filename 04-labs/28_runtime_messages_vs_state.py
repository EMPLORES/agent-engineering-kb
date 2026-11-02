
def plan_trip(state):
    """根据 State 中的任务信息生成行程。"""

    destination = state.get("destination")
    status = state.get("status")

    if not destination:
        return "无法规划行程：缺少目的地。"

    if status != "pending":
        return f"当前任务状态为 {status}，暂不规划行程。"

    return f"正在规划前往 {destination} 的行程。"


def run_experiment():
    # 消息记录：用户提出了什么请求
    messages = [
        {
            "role": "user",
            "content": "帮我规划去东京的行程。",
        }
    ]

    # State 记录：当前任务的结构化数据
    state = {
        "destination": "东京",
        "status": "pending",
    }

    print("========== 实验一：初始状态 ==========")
    print("Messages：", messages)
    print("State：", state)
    print("执行结果：", plan_trip(state))

    print("\n========== 实验二：更新 State ==========")
    state["status"] = "completed"

    print("Messages：", messages)
    print("State：", state)
    print("执行结果：", plan_trip(state))

    print("\n========== 实验三：修改 Messages ==========")
    messages.append({
        "role": "assistant",
        "content": "用户的行程任务已经完成。",
    })

    print("Messages：", messages)
    print("State：", state)
    print("执行结果：", plan_trip(state))


if __name__ == "__main__":
    run_experiment()
