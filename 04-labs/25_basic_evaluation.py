
def agent(question: str) -> str:
    """模拟 Agent 生成答案。"""
    return "列表和元组都可以存储多个元素。"


def evaluate(answer: str) -> dict:
    """使用明确规则评估答案。"""
    checks = {
        "mentions_list": "列表" in answer,
        "mentions_tuple": "元组" in answer,
        "mentions_mutability": (
            "修改" in answer or "可变" in answer
        ),
    }

    passed = all(checks.values())

    return {
        "passed": passed,
        "checks": checks,
    }


if __name__ == "__main__":
    question = "Python 中，列表和元组的主要区别是什么？"

    answer = agent(question)
    result = evaluate(answer)

    print("用户问题：", question)
    print("Agent 答案：", answer)
    print("评估结果：", result)
