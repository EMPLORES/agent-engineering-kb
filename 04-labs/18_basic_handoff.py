
from dataclasses import dataclass


@dataclass
class Handoff:
    target_agent: str
    task: str


def refund_agent(task):
    print("[Refund Agent] 正在处理退款任务")
    print(f"[Refund Agent] 收到的任务：{task}")
    return "退款条件核实完成"


# 方式一：把另一个 Agent 当作工具
def customer_service_with_agent_as_tool(message):
    print("[Customer Service] 开始处理用户请求")

    result = refund_agent(message)

    print("[Customer Service] 重新取得控制权")
    print("[Customer Service] 正在整理退款专员的结果")

    return f"客服综合答复：{result}"


# 方式二：将控制权交给另一个 Agent
def customer_service_with_handoff(message):
    print("[Customer Service] 开始处理用户请求")
    print("[Customer Service] 决定交给退款专员")

    return Handoff(
        target_agent="refund_agent",
        task=message,
    )


def run_with_agent_as_tool(message):
    print("========== Agent-as-Tool ==========")

    result = customer_service_with_agent_as_tool(message)

    print(f"[Final Result] {result}")


def run_with_handoff(message):
    print("\n========== Handoff ==========")

    result = customer_service_with_handoff(message)

    if isinstance(result, Handoff):
        print(f"[Router] 控制权交给：{result.target_agent}")

        if result.target_agent == "refund_agent":
            result = refund_agent(result.task)

    print(f"[Final Result] {result}")


if __name__ == "__main__":
    message = "我想申请退款"

    run_with_agent_as_tool(message)
    run_with_handoff(message)
