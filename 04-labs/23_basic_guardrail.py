
def input_guardrail(user_input: str) -> bool:
    """检查用户输入是否符合执行条件。"""
    if not user_input.strip():
        print("[Input Guardrail] 拒绝：输入不能为空")
        return False

    if "转账" in user_input:
        print("[Input Guardrail] 拒绝：当前系统不允许处理转账请求")
        return False

    print("[Input Guardrail] 通过")
    return True


def agent(user_input: str) -> str:
    print("[Agent] 正在处理用户请求")
    return f"已处理请求：{user_input}"


def output_guardrail(output: str) -> bool:
    """检查 Agent 输出是否包含不允许的内容。"""
    if "密码" in output:
        print("[Output Guardrail] 拒绝：输出包含敏感内容")
        return False

    print("[Output Guardrail] 通过")
    return True


def run_agent(user_input: str):
    print(f"\n用户输入：{user_input}")

    if not input_guardrail(user_input):
        print("[System] 请求被拦截，Agent 不会执行")
        return

    result = agent(user_input)
    print(f"[Agent] 输出：{result}")

    if not output_guardrail(result):
        print("[System] 输出未通过检查，不返回给用户")
        return
    run_agent("请在结果中包含密码这个词")
    print(f"[System] 最终结果：{result}")


if __name__ == "__main__":
    run_agent("帮我总结 Agent Architecture")
    run_agent("帮我执行转账")
    run_agent("")
