from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# ============================================================
# 1. Define State
# ============================================================

class TaskState(TypedDict):
    task_id: str
    description: str
    status: str
    result: str
    processing_steps: list[str]


# ============================================================
# 2. Define Nodes
# ============================================================

def validate_task(state: TaskState) -> dict:
    """Validate the incoming task."""

    print(f"[Validate] 正在验证任务：{state['task_id']}")

    return {
        "status": "validated",
        "processing_steps": state["processing_steps"] + [
            "validate_task"
        ],
    }


def process_task(state: TaskState) -> dict:
    """Process the task."""

    print(f"[Process] 正在处理任务：{state['task_id']}")

    return {
        "status": "processed",
        "result": f"已处理任务：{state['description']}",
        "processing_steps": state["processing_steps"] + [
            "process_task"
        ],
    }


def finalize_task(state: TaskState) -> dict:
    """Finalize the task."""

    print(f"[Finalize] 任务完成：{state['task_id']}")

    return {
        "status": "completed",
        "processing_steps": state["processing_steps"] + [
            "finalize_task"
        ],
    }


# ============================================================
# 3. Build Graph with Checkpointer
# ============================================================

def build_task_graph(checkpointer):

    builder = StateGraph(TaskState)

    builder.add_node("validate_task", validate_task)
    builder.add_node("process_task", process_task)
    builder.add_node("finalize_task", finalize_task)

    builder.add_edge(START, "validate_task")
    builder.add_edge("validate_task", "process_task")
    builder.add_edge("process_task", "finalize_task")
    builder.add_edge("finalize_task", END)

    return builder.compile(
        checkpointer=checkpointer
    )


# ============================================================
# 4. Run Task with Thread ID
# ============================================================

def run_task(graph, thread_id: str, task_id: str, description: str):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state: TaskState = {
        "task_id": task_id,
        "description": description,
        "status": "pending",
        "result": "",
        "processing_steps": [],
    }

    result = graph.invoke(
        initial_state,
        config=config
    )

    print("\n最终执行结果：")
    print(result)

    return config


# ============================================================
# 5. Inspect Current State
# ============================================================

def inspect_thread(graph, config, title: str):

    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)

    snapshot = graph.get_state(config)

    print("\n当前 StateSnapshot：")
    print("Values：", snapshot.values)
    print("Next：", snapshot.next)
    print("Metadata：", snapshot.metadata)
    print("Created At：", snapshot.created_at)

    checkpoint_id = snapshot.config["configurable"].get(
        "checkpoint_id"
    )

    print("Checkpoint ID：", checkpoint_id)

    # Inspect checkpoint history
    history = list(
        graph.get_state_history(config)
    )

    print(f"\n历史检查点数量：{len(history)}")

    for index, item in enumerate(history, start=1):

        checkpoint_id = (
            item.config["configurable"].get("checkpoint_id")
        )

        print(f"\nCheckpoint {index}")
        print("ID：", checkpoint_id)
        print("Values：", item.values)
        print("Next：", item.next)
        print("Metadata：", item.metadata)


# ============================================================
# 6. Main
# ============================================================

def main():

    # Create an in-memory checkpointer
    checkpointer = InMemorySaver()

    # Compile the graph with the checkpointer
    graph = build_task_graph(checkpointer)

    # Run two independent tasks
    config_1 = run_task(
        graph,
        "ticket-T001",
        "T001",
        "处理账号登录问题"
    )

    config_2 = run_task(
        graph,
        "ticket-T002",
        "T002",
        "处理系统技术故障"
    )

    # Inspect current state of each thread
    inspect_thread(
        graph,
        config_1,
        "THREAD T001"
    )

    inspect_thread(
        graph,
        config_2,
        "THREAD T002"
    )

    # Verify thread isolation
    state_1 = graph.get_state(config_1).values
    state_2 = graph.get_state(config_2).values

    print("\n" + "=" * 55)
    print("Thread 隔离验证")
    print("=" * 55)

    print("Thread T001 的任务：", state_1["task_id"])
    print("Thread T002 的任务：", state_2["task_id"])

    assert state_1["task_id"] == "T001"
    assert state_2["task_id"] == "T002"

    assert state_1["description"] != state_2["description"]

    print("两个 Thread 的任务状态相互独立！")


if __name__ == "__main__":
    main()