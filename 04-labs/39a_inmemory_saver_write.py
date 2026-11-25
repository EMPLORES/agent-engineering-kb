from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt


class TaskState(TypedDict):
    task_id: str
    description: str
    approval_status: str


def request_approval(state: TaskState):
    print(f"[Approval] 工单 {state['task_id']} 正在等待人工审核")

    decision = interrupt({
        "task_id": state["task_id"],
        "description": state["description"],
        "question": "是否批准执行？"
    })

    return {
        "approval_status": "approved" if decision["approved"] else "rejected"
    }


def build_graph(checkpointer):
    builder = StateGraph(TaskState)

    builder.add_node("request_approval", request_approval)
    builder.add_edge(START, "request_approval")
    builder.add_edge("request_approval", END)

    return builder.compile(checkpointer=checkpointer)


def main():
    checkpointer = InMemorySaver()
    graph = build_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": "experiment39-T001"
        }
    }

    initial_state = {
        "task_id": "T001",
        "description": "执行客户账户权限变更",
        "approval_status": "pending"
    }

    print("=" * 50)
    print("进程 A：创建工作流并暂停")
    print("=" * 50)

    result = graph.invoke(initial_state, config=config)

    print("\n暂停返回结果：")
    print(result)

    snapshot = graph.get_state(config)

    print("\n暂停时的 Checkpoint：")
    print("Values：", snapshot.values)
    print("Next：", snapshot.next)
    print("Checkpoint ID：",
          snapshot.config["configurable"]["checkpoint_id"])

    print("\n进程 A 即将结束。")
    print("InMemorySaver 中的数据将随进程退出而丢失。")


if __name__ == "__main__":
    main()