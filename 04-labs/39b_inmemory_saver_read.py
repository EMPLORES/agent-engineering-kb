from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt


class TaskState(TypedDict):
    task_id: str
    description: str
    approval_status: str


def request_approval(state: TaskState):
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
    # 模拟全新 Python 进程中的存储实例
    checkpointer = InMemorySaver()
    graph = build_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": "experiment39-T001"
        }
    }

    print("=" * 50)
    print("进程 B：尝试读取之前的工作流状态")
    print("=" * 50)

    snapshot = graph.get_state(config)

    print("\n查询结果：")
    print("Values：", snapshot.values)
    print("Next：", snapshot.next)
    print("历史 Checkpoint 数量：",
          len(list(graph.get_state_history(config))))

    if not snapshot.values:
        print("\n验证结果：没有找到之前的 Checkpoint。")
        print("相同 thread_id 并不能恢复已经丢失的内存数据。")
    else:
        print("\n发现状态数据，请进一步检查实验环境。")


if __name__ == "__main__":
    main()