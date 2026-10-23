
def prepare_transfer(amount):
    """准备转账请求。"""
    print(f"[Agent] 已准备转账请求：{amount} 元")
    return {
        "amount": amount,
        "status": "pending",
    }


def human_review(request, approved):
    """模拟人工审批。"""
    print("[Human] 正在审核转账请求")

    if approved:
        request["status"] = "approved"
        print("[Human] 审批通过")
    else:
        request["status"] = "rejected"
        print("[Human] 审批拒绝")

    return request


def execute_transfer(request):
    """根据审批状态决定是否执行转账。"""
    if request["status"] != "approved":
        print("[System] 未获得批准，不执行转账")
        return

    print(f"[System] 正在执行转账：{request['amount']} 元")
    request["status"] = "completed"


def run_workflow(amount, approved):
    print("\n========== 新任务 ==========")

    request = prepare_transfer(amount)
    request = human_review(request, approved)
    execute_transfer(request)

    print("[System] 最终状态：", request["status"])


if __name__ == "__main__":
    run_workflow(500, True)
    run_workflow(2000, False)
