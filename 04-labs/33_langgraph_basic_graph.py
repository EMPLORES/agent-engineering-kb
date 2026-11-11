
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# 1. 定义图的共享状态
class AgentState(TypedDict):
    request: str
    request_type: str
    response: str


# 2. 定义节点：判断用户请求类型
def classify_request(state: AgentState):
    request = state["request"]

    print("[Node] 正在分析用户请求：", request)

    if "多少钱" in request or "价格" in request:
        request_type = "pricing"
    else:
        request_type = "general"

    print("[Node] 请求类型：", request_type)

    return {
        "request_type": request_type
    }


# 3. 定义条件路由函数
def route_request(state: AgentState):
    request_type = state["request_type"]

    print("[Router] 根据 State 决定下一步：", request_type)

    return request_type


# 4. 定义价格类请求节点
def pricing_node(state: AgentState):
    print("[Node] 进入价格处理节点")

    return {
        "response": "这是一个价格类请求，需要查询产品价格。"
    }


# 5. 定义普通请求节点
def general_node(state: AgentState):
    print("[Node] 进入普通请求处理节点")

    return {
        "response": "这是一个普通请求，可以介绍产品信息。"
    }


# 6. 创建 StateGraph 构建器
builder = StateGraph(AgentState)


# 7. 注册节点
builder.add_node("classify", classify_request)
builder.add_node("pricing", pricing_node)
builder.add_node("general", general_node)


# 8. 定义图的执行关系
builder.add_edge(START, "classify")

builder.add_conditional_edges(
    "classify",
    route_request,
    {
        "pricing": "pricing",
        "general": "general",
    }
)

builder.add_edge("pricing", END)
builder.add_edge("general", END)


# 9. 编译图，生成可执行对象
app = builder.compile()

print("\n========== Graph 编译完成 ==========")


# 10. 执行两次实验
def run_experiment(request: str):
    print("\n========== 开始执行任务 ==========")

    initial_state = {
        "request": request,
        "request_type": "",
        "response": "",
    }

    result = app.invoke(initial_state)

    print("\n[Result] 最终 State：", result)
    print("[Result] 最终回答：", result["response"])


if __name__ == "__main__":
    run_experiment("这个产品多少钱？")

    run_experiment("介绍一下这个产品。")

