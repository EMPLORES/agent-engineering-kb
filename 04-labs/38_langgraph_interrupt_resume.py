
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict):
    task_id: str
    description: str
    approval_status: str
    approved: bool
    reviewer: str
    execution_result: str


def request_approval(state: ApprovalState):
    print(f"\n[Approval] 正在请求人工审核：{state['task_id']}")

    # 暂停工作流，等待人工提供审核结果
    decision = interrupt({
        "task_id": state["task_id"],
        "description": state["description"],
        "question": "是否批准执行这项操作？"
    })

    print("[Approval] 已收到人工审核结果")

    return {
        "approved": decision["approved"],
        "reviewer": decision["reviewer"],
        "approval_status": (
            "approved" if decision["approved"] else "rejected"
        )
    }


def execute_task(state: ApprovalState):
    print(f"\n[Execute] 正在执行任务：{state['task_id']}")

    return {
        "execution_result": f"任务已执行：{state['description']}"
    }


def reject_task(state: ApprovalState):
    print(f"\n[Reject] 任务被拒绝：{state['task_id']}")

    return {
        "execution_result": "人工审核未通过，任务未执行"
    }


def route_after_approval(state: ApprovalState):
    if state["approved"]:
        return "execute_task"

    return "reject_task"


def build_graph(checkpointer):
    builder = StateGraph(ApprovalState)

    builder.add_node("request_approval", request_approval)
    builder.add_node("execute_task", execute_task)
    builder.add_node("reject_task", reject_task)

    builder.add_edge(START, "request_approval")

    builder.add_conditional_edges(
        "request_approval",
        route_after_approval,
        {
            "execute_task": "execute_task",
            "reject_task": "reject_task"
        }
    )

    builder.add_edge("execute_task", END)
    builder.add_edge("reject_task", END)

    return builder.compile(checkpointer=checkpointer)


def main():
    checkpointer = InMemorySaver()
    graph = build_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": "approval-T001"
        }
    }

    initial_state = {
        "task_id": "T001",
        "description": "执行客户账户权限变更",
        "approval_status": "pending",
        "approved": False,
        "reviewer": "",
        "execution_result": ""
    }

    # 第一阶段：启动工作流，直到人工审核处暂停
    print("=" * 50)
    print("第一阶段：启动工作流")
    print("=" * 50)

    result = graph.invoke(initial_state, config=config)

    print("\n工作流暂停，返回结果：")
    print(result)

    # 第二阶段：检查暂停时的状态快照
    print("\n" + "=" * 50)
    print("第二阶段：检查暂停时的 Checkpoint")
    print("=" * 50)

    snapshot = graph.get_state(config)

    print("Values：", snapshot.values)
    print("Next：", snapshot.next)
    print("Tasks：", snapshot.tasks)
    print("Checkpoint ID：", snapshot.config["configurable"]["checkpoint_id"])

    history = list(graph.get_state_history(config))
    print("当前历史 Checkpoint 数量：", len(history))

    # 第三阶段：模拟人工批准，恢复工作流
    print("\n" + "=" * 50)
    print("第三阶段：人工批准并恢复执行")
    print("=" * 50)

    resume_result = graph.invoke(
        Command(
            resume={
                "approved": True,
                "reviewer": "管理员"
            }
        ),
        config=config
    )

    print("\n恢复后的最终结果：")
    print(resume_result)

    # 第四阶段：再次检查最终状态
    print("\n" + "=" * 50)
    print("第四阶段：检查恢复后的状态")
    print("=" * 50)

    final_snapshot = graph.get_state(config)

    print("Values：", final_snapshot.values)
    print("Next：", final_snapshot.next)

    final_history = list(graph.get_state_history(config))
    print("最终历史 Checkpoint 数量：", len(final_history))


if __name__ == "__main__":
    main()
