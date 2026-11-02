
def collect_destination(state):
    """收集目的地，并更新 State。"""
    state["destination"] = "东京"
    state["status"] = "destination_collected"
    print("[Collect] 已收集目的地：东京")


def plan_itinerary(state):
    """根据 State 生成行程。"""
    destination = state.get("destination")

    if not destination:
        raise ValueError("缺少目的地，无法规划行程")

    state["itinerary"] = [
        f"第 1 天：抵达{destination}",
        f"第 2 天：游览{destination}的景点",
    ]
    state["status"] = "itinerary_planned"
    print("[Plan] 行程规划完成")


def complete_task(state):
    """完成任务并更新 State。"""
    if not state.get("itinerary"):
        raise ValueError("没有行程，无法完成任务")

    state["status"] = "completed"
    print("[Complete] 任务完成")


def route_next_step(state):
    """Runtime 根据当前 State 决定下一步执行什么。"""
    status = state.get("status")

    if status == "pending":
        return "collect_destination"
    elif status == "destination_collected":
        return "plan_itinerary"
    elif status == "itinerary_planned":
        return "complete_task"
    elif status == "completed":
        return "end"
    else:
        raise ValueError(f"无法识别的任务状态：{status}")


def run_runtime(state, max_steps=5):
    """根据 State 动态选择并执行下一步。"""
    actions = {
        "collect_destination": collect_destination,
        "plan_itinerary": plan_itinerary,
        "complete_task": complete_task,
    }

    for step in range(1, max_steps + 1):
        print(f"\n[Runtime] 第 {step} 步")
        print("[Runtime] 当前状态：", state["status"])

        next_step = route_next_step(state)
        print("[Runtime] 下一步动作：", next_step)

        if next_step == "end":
            print("[Runtime] 检测到任务完成，停止执行")
            return

        action = actions.get(next_step)
        if action is None:
            raise ValueError(f"找不到对应动作：{next_step}")

        action(state)

    raise RuntimeError("超过最大执行步数，Runtime 停止运行")


def run_experiment():
    state = {
        "destination": None,
        "itinerary": [],
        "status": "pending",
    }

    print("========== State-driven Routing 实验 ==========")
    run_runtime(state)

    print("\n========== 最终 State ==========")
    print(state)


if __name__ == "__main__":
    run_experiment()
