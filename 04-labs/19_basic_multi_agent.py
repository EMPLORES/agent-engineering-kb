def researcher_agent(task, feedback=None):
    """提出方案，并根据审核意见修改方案。"""
    print("[Researcher Agent] 正在分析任务")

    if feedback is None:
        proposal = "安排半天的郊外徒步活动"
        reason = "适合喜欢户外活动的人"
    else:
        print(f"[Researcher Agent] 收到修改意见：{feedback}")
        print("[Researcher Agent] 正在修改方案")

        proposal = (
            "安排半天的郊外徒步活动；"
            "出发前确认天气和路线安全，"
            "选择难度适中的路线，并准备必要装备"
        )
        reason = "在保留原方案的基础上补充了安全准备"

    return {
        "proposal": proposal,
        "reason": reason,
        "risk": "需要确认天气和路线安全",
    }


def reviewer_agent(task, research_result):
    """检查方案，并返回审核状态。"""
    print("[Reviewer Agent] 正在检查研究结果")
    print(
        f"[Reviewer Agent] 收到的方案："
        f"{research_result['proposal']}"
    )

    proposal = research_result["proposal"]

    approved = (
        "确认天气和路线安全" in proposal
        and "必要装备" in proposal
    )

    if approved:
        review = "方案通过审核"
        suggestion = ""
    else:
        review = "方案需要进一步完善"
        suggestion = "请确认天气和路线安全，并补充必要装备准备"

    return {
        "approved": approved,
        "review": review,
        "suggestion": suggestion,
    }


def supervisor_agent(task):
    """协调多个 Agent，直到方案通过审核或达到尝试上限。"""
    print("[Supervisor Agent] 接收到任务")
    print(f"[Supervisor Agent] 任务内容：{task}")

    max_attempts = 3
    feedback = None

    for attempt in range(1, max_attempts + 1):
        print(f"\n[Supervisor Agent] 第 {attempt} 轮协作")

        research_result = researcher_agent(task, feedback)
        review_result = reviewer_agent(task, research_result)

        if review_result["approved"]:
            print("[Supervisor Agent] 方案通过审核，结束协作")

            return {
                "最终方案": research_result["proposal"],
                "方案依据": research_result["reason"],
                "审核状态": review_result["review"],
            }

        print("[Supervisor Agent] 方案未通过审核")
        feedback = review_result["suggestion"]

    print("[Supervisor Agent] 已达到最大尝试次数，结束协作")

    return {
        "最终方案": research_result["proposal"],
        "审核状态": "未通过审核，已达到最大尝试次数",
        "最后审核意见": review_result["suggestion"],
    }

if __name__ == "__main__":
    task = "为喜欢户外活动的人规划一个周末活动"

    result = supervisor_agent(task)

    print("\n========== 最终结果 ==========")

    for key, value in result.items():
        print(f"{key}：{value}")