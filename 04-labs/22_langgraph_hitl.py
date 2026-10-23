
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class TransferState(TypedDict):
    amount: int
    approved: bool
    status: str


def prepare_transfer(state: TransferState):
    print(f"[Agent] 已准备转账请求：{state['amount']} 元")
    return {"status": "waiting_for_approval"}


def human_approval(state: TransferState):
    # interrupt 会暂停图执行，并向外部提供审批请求。
    # 恢复时，interrupt 的返回值就是外部传入的审批结果。
    approved = interrupt({
        "type": "approval_required",
        "amount": state["amount"],
        "message": f"是否批准转账 {state['amount']} 元？",
    })

    print(f"[Agent] 收到审批结果：{approved}")
    return {
        "approved": approved,
        "status": "approved" if approved else "rejected",
    }


def execute_transfer(state: TransferState):
    print(f"[System] 正在执行转账：{state['amount']} 元")
    return {"status": "completed"}


def reject_transfer(state: TransferState):
    print("[System] 审批未通过，不执行转账")
    return {"status": "rejected"}


def route_after_approval(state: TransferState):
    if state["approved"]:
        return "execute"
    return "reject"


builder = StateGraph(TransferState)

builder.add_node("prepare", prepare_transfer)
builder.add_node("human_approval", human_approval)
builder.add_node("execute", execute_transfer)
builder.add_node("reject", reject_transfer)

builder.add_edge(START, "prepare")
builder.add_edge("prepare", "human_approval")

builder.add_conditional_edges(
    "human_approval",
    route_after_approval,
    {
        "execute": "execute",
        "reject": "reject",
    },
)

builder.add_edge("execute", END)
builder.add_edge("reject", END)

# MemorySaver 用于本次运行中的检查点保存。
# 它不是跨进程、跨重启的磁盘持久化存储。
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "transfer-001",
        }
    }

    print("========== 第一阶段：启动任务 ==========")

    result = graph.invoke(
        {
            "amount": 500,
            "approved": False,
            "status": "pending",
        },
        config=config,
    )

    print("\n========== 中断时的状态 ==========")
    print(result)

    print("\n========== 第二阶段：人工批准并恢复 ==========")

    result = graph.invoke(
        Command(resume=True),
        config=config,
    )

    print("\n========== 最终状态 ==========")
    print(result)
