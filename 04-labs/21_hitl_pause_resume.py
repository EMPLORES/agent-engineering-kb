
def prepare_transfer(amount):
    """创建转账任务，并记录执行状态。"""
    return {
        "amount": amount,
        "status": "pending",
        "step": "waiting_for_approval",
    }


def run_workflow(state, approval=None):
    """根据保存的状态继续执行工作流。"""

    if state["step"] == "waiting_for_approval":
        print("[Agent] 转账请求已准备")
        print(f"[Agent] 转账金额：{state['amount']} 元")
        print("[Agent] 等待人工审批")

        if approval is None:
            state["status"] = "waiting"
            return state

        if approval is False:
            state["status"] = "rejected"
            state["step"] = "finished"
            print("[Human] 审批拒绝")
            return state

        state["status"] = "approved"
        state["step"] = "execute_transfer"

    if state["step"] == "execute_transfer":
        print("[System] 审批通过，执行转账")
        state["status"] = "completed"
        state["step"] = "finished"

    return state


if __name__ == "__main__":
    # 第一阶段：准备任务，但不提供审批结果
    state = prepare_transfer(500)
    state = run_workflow(state)

    print("\n=== 暂停后的状态 ===")
    print(state)

    # 第二阶段：模拟稍后收到人工审批结果
    print("\n=== 收到人工审批后恢复 ===")
    state = run_workflow(state, approval=True)

    print("\n=== 最终状态 ===")
    print(state)
