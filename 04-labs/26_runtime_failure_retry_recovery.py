
import json
from pathlib import Path
from typing import Callable


# ==========================================
# 1. 定义不同类型的失败
# ==========================================

class TransientFailure(Exception):
    """临时性错误：允许重试。"""
    pass


class PermanentFailure(Exception):
    """永久性错误：不应该重试。"""
    pass


class SimulatedInterruption(Exception):
    """模拟 Runtime 意外中断。"""
    pass


# ==========================================
# 2. Retry Policy：重试策略
# ==========================================

class RetryPolicy:

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts


# ==========================================
# 3. Checkpoint Store：保存和读取执行状态
# ==========================================

class CheckpointStore:

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def save(self, state: dict):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)

        print("[Checkpoint] 执行状态已保存")

    def load(self, initial_state: dict) -> dict:
        if not self.file_path.exists():
            print("[Checkpoint] 没有历史状态，使用初始状态")
            return initial_state

        with open(self.file_path, "r", encoding="utf-8") as file:
            state = json.load(file)

        print("[Checkpoint] 已加载历史执行状态")
        return state


# ==========================================
# 4. Runtime：负责执行、重试和恢复
# ==========================================

class Runtime:

    def __init__(
        self,
        steps: list,
        checkpoint_store: CheckpointStore,
        retry_policy: RetryPolicy
    ):
        self.steps = steps
        self.checkpoint_store = checkpoint_store
        self.retry_policy = retry_policy

        self.initial_state = {
            "completed_steps": [],
            "results": {}
        }

    def execute_with_retry(
        self,
        step_name: str,
        action: Callable,
        state: dict
    ):

        for attempt in range(1, self.retry_policy.max_attempts + 1):

            print(
                f"[Runtime] 执行 {step_name} "
                f"(第 {attempt} 次尝试)"
            )

            try:
                return action(state)

            except SimulatedInterruption:
                # 中断不是普通的可重试错误
                raise

            except TransientFailure as error:

                print(f"[Retry] 临时错误：{error}")

                if attempt == self.retry_policy.max_attempts:
                    print("[Retry] 已达到最大尝试次数")
                    raise

                print("[Retry] 准备重新执行当前步骤")

            except PermanentFailure as error:

                print(f"[Runtime] 永久性错误：{error}")
                print("[Runtime] 不进行重试")
                raise

        raise RuntimeError("执行流程异常结束")

    def run(self):

        state = self.checkpoint_store.load(
            self.initial_state
        )

        print(
            f"\n[Runtime] 已完成步骤："
            f"{state['completed_steps']}"
        )

        for step_name, action in self.steps:

            # 跳过已经完成的步骤
            if step_name in state["completed_steps"]:
                print(f"[Recovery] 跳过已完成步骤：{step_name}")
                continue

            try:
                result = self.execute_with_retry(
                    step_name,
                    action,
                    state
                )

                # 只有成功执行后才更新状态
                state["results"][step_name] = result
                state["completed_steps"].append(step_name)

                # 成功后保存 Checkpoint
                self.checkpoint_store.save(state)

            except SimulatedInterruption:

                print("\n[Runtime] 检测到执行中断")
                print("[Runtime] 当前执行停止，等待恢复")
                return "interrupted"

            except PermanentFailure:

                print("\n[Runtime] 执行失败，终止任务")
                return "failed"

            except TransientFailure:

                print("\n[Runtime] 重试次数耗尽，终止任务")
                return "failed"

        print("\n[Runtime] 所有步骤执行完成")
        return "completed"


# ==========================================
# 5. 模拟三个任务步骤
# ==========================================

# 用于记录模拟调用次数
call_counts = {
    "collect": 0,
    "analyze": 0,
    "publish": 0
}


def collect_data(state):

    call_counts["collect"] += 1

    if call_counts["collect"] == 1:
        raise TransientFailure("模拟网络暂时不可用")

    print("[Tool] 数据收集成功")
    return {"records": 100}


def analyze_data(state):

    call_counts["analyze"] += 1

    if call_counts["analyze"] == 1:
        raise SimulatedInterruption("模拟 Runtime 中断")

    records = state["results"]["collect"]["records"]

    print("[Tool] 数据分析成功")
    return {"summary": f"共处理 {records} 条记录"}


def publish_report(state):

    call_counts["publish"] += 1

    raise PermanentFailure("模拟发布目标配置错误")


# ==========================================
# 6. 组装执行流程
# ==========================================

steps = [
    ("collect", collect_data),
    ("analyze", analyze_data),
    ("publish", publish_report)
]


def main():

    checkpoint_path = Path(__file__).with_name(
        "day22_checkpoint.json"
    )

    # 清理上一次实验留下的状态
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    checkpoint_store = CheckpointStore(checkpoint_path)
    retry_policy = RetryPolicy(max_attempts=3)

    print("=" * 50)
    print("第一阶段：启动 Runtime")
    print("=" * 50)

    runtime1 = Runtime(
        steps,
        checkpoint_store,
        retry_policy
    )

    first_result = runtime1.run()

    print(f"\n第一阶段结果：{first_result}")

    print("\n" + "=" * 50)
    print("第二阶段：创建新的 Runtime 并恢复执行")
    print("=" * 50)

    runtime2 = Runtime(
        steps,
        checkpoint_store,
        retry_policy
    )

    second_result = runtime2.run()

    print(f"\n第二阶段结果：{second_result}")

    print("\n" + "=" * 50)
    print("最终调用次数")
    print("=" * 50)

    for name, count in call_counts.items():
        print(f"{name}: {count} 次")

    print("\n实验结束")


if __name__ == "__main__":
    main()
