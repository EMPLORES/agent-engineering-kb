
import time
import json
import uuid
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def run_step(trace, step_name, func):
    span = {
        "span_id": str(uuid.uuid4())[:8],
        "trace_id": trace["trace_id"],
        "step_name": step_name,
        "start_time": now(),
        "status": "running",
        "error": None,
    }

    started = time.perf_counter()
    print(f"[Span] {step_name} start")

    try:
        result = func()
        span["status"] = "success"
        return result
    except Exception as e:
        span["status"] = "failed"
        span["error"] = str(e)
        print(f"[Span] {step_name} error: {e}")
        raise
    finally:
        span["end_time"] = now()
        span["duration_ms"] = round(
            (time.perf_counter() - started) * 1000, 2
        )
        trace["spans"].append(span)

        print(
            f"[Span] {step_name} "
            f"status={span['status']} "
            f"duration={span['duration_ms']}ms"
        )


def search_tool():
    time.sleep(0.2)
    raise RuntimeError("搜索服务暂时不可用")


def weather_tool():
    time.sleep(0.1)
    return "当前天气晴朗"


def agent_task():
    trace = {
        "trace_id": str(uuid.uuid4())[:8],
        "start_time": now(),
        "spans": [],
        "status": "running",
    }

    started = time.perf_counter()
    print(f"\n[Trace] {trace['trace_id']} started")

    try:
        try:
            run_step(trace, "tool.search", search_tool)
        except Exception:
            print("[Agent] 搜索失败，尝试继续执行")

        weather = run_step(trace, "tool.weather", weather_tool)
        answer = f"天气查询结果：{weather}"
        trace["status"] = "success"
        print(f"[Agent] {answer}")
        return answer

    except Exception as e:
        trace["status"] = "failed"
        print(f"[Agent] task failed: {e}")
        raise

    finally:
        trace["end_time"] = now()
        trace["duration_ms"] = round(
            (time.perf_counter() - started) * 1000, 2
        )

        print(
            f"[Trace] status={trace['status']} "
            f"duration={trace['duration_ms']}ms"
        )
        print("[Trace] 完整追踪记录：")
        print(json.dumps(trace, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    agent_task()
