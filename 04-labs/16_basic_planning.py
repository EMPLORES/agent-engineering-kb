
def create_plan(task):
    """根据任务生成一个简单的执行计划。"""
    if task == "规划北京旅行":
        return [
            "确定旅行日期和预算",
            "选择旅行景点",
            "安排每日行程",
            "汇总旅行计划",
        ]

    return [
        "分析任务",
        "执行任务",
        "汇总结果",
    ]


def execute_plan(task, plan):
    """按照计划顺序执行步骤。"""
    print(f"任务：{task}")
    print("\n生成的计划：")

    for index, step in enumerate(plan, start=1):
        print(f"{index}. {step}")

    print("\n开始执行：")

    for index, step in enumerate(plan, start=1):
        print(f"[Step {index}] 正在执行：{step}")

    return "计划中的步骤已执行完毕"


if __name__ == "__main__":
    task = "规划北京旅行"

    plan = create_plan(task)
    plan.reverse()
    result = execute_plan(task, plan)

    print("\n最终结果：", result)
