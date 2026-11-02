
def collect_destination(state):
    """收集目的地，并更新任务状态。"""

    state["destination"] = "东京"
    state["status"] = "destination_collected"

    print("[Collect] 已收集目的地：", state["destination"])


def plan_itinerary(state):
    """根据当前 State 规划行程。"""

    destination = state.get("destination")

    if not destination:
        raise ValueError("缺少目的地，无法规划行程")

    state["itinerary"] = [
        f"第 1 天：抵达{destination}",
        f"第 2 天：游览{destination}的景点",
    ]
    state["status"] = "itinerary_planned"

    print("[Plan] 已生成行程")


def complete_task(state):
    """完成任务，并更新最终状态。"""

    if not state.get("itinerary"):
        raise ValueError("没有行程，无法完成任务")

    state["status"] = "completed"

    print("[Complete] 任务已完成")


def print_state(state):
    """查看当前任务状态。"""

    print("当前 State：", state)


def run_experiment():
    # 初始化任务状态
    state = {
        "destination": None,
        "itinerary": [],
        "status": "pending",
    }

    print("========== 初始状态 ==========")
    print_state(state)

    print("\n========== 第一步：收集目的地 ==========")
    collect_destination(state)
    print_state(state)

    print("\n========== 第二步：规划行程 ==========")
    plan_itinerary(state)
    print_state(state)

    print("\n========== 第三步：完成任务 ==========")
    complete_task(state)
    print_state(state)


if __name__ == "__main__":
    run_experiment()
