
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. Define State
# ============================================================

class TicketState(TypedDict):
    ticket_id: str
    user_message: str

    is_valid: bool
    validation_error: str

    category: str
    priority: str

    assigned_queue: str
    routing_reason: str

    ticket_status: str
    result: str

    matched_categories: list[str]

    # Record executed nodes so we can inspect the actual route.
    processing_steps: list[str]


# ============================================================
# 2. Define Nodes
# ============================================================

def validate_ticket(state: TicketState) -> dict:
    """Validate required ticket fields."""

    ticket_id = (state.get("ticket_id") or "").strip()
    user_message = (state.get("user_message") or "").strip()

    errors = []

    if not ticket_id:
        errors.append("工单编号不能为空")

    if not user_message:
        errors.append("用户问题不能为空")

    return {
        "is_valid": len(errors) == 0,
        "validation_error": "；".join(errors),
        "processing_steps": state["processing_steps"] + [
            "validate_ticket"
        ],
    }


def invalid_ticket(state: TicketState) -> dict:
    """Handle invalid tickets."""
    

    return {
        "ticket_status": "invalid",
        "processing_steps": state["processing_steps"] + [
            "invalid_ticket"
        ],
    }


def classify_ticket(state: TicketState) -> dict:
    """Classify a ticket using deterministic keyword rules."""

    message = state["user_message"].lower()

    account_keywords = [
        "账号", "账户", "登录", "密码", "验证码"
    ]

    technical_keywords = [
        "崩溃", "故障", "无法使用", "报错",
        "异常", "bug", "闪退"
    ]

    order_keywords = [
        "订单", "付款", "支付", "物流",
        "发货", "快递", "退款"
    ]

    matched_categories = []
    if any(keyword in message for keyword in account_keywords):
        matched_categories.append("Account")

    if any(keyword in message for keyword in technical_keywords):
        matched_categories.append("Technical")

    if any(keyword in message for keyword in order_keywords):
        matched_categories.append("Order")

    if len(matched_categories) == 0:
        category = "Unknown"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        category = "Multiple"
    
    return{
        "category": category,
        "matched_categories": matched_categories,
        "processing_steps": state["processing_steps"] + [
            "classify_ticket"
        ],
    }


def assess_priority(state: TicketState) -> dict:
    """Assess ticket priority independently from its category."""

    message = state["user_message"].lower()

    high_priority_keywords = [
        "紧急",
        "严重",
        "完全无法使用",
        "业务中断",
        "崩溃",
    ]

    if any(keyword in message for keyword in high_priority_keywords):
        priority = "High"
    else:
        priority = "Normal"

    return {
        "priority": priority,
        "processing_steps": state["processing_steps"] + [
            "assess_priority"
        ],
    }


# ============================================================
# 3. Define Routing Nodes
# ============================================================

def assign_account_queue(state: TicketState) -> dict:
    return {
        "assigned_queue": "Account Support",
        "routing_reason": "账号类问题分配给账号支持团队",
        "processing_steps": state["processing_steps"] + [
            "assign_account_queue"
        ],
    }


def assign_technical_queue(state: TicketState) -> dict:
    return {
        "assigned_queue": "Technical Support",
        "routing_reason": "技术类问题分配给技术支持团队",
        "processing_steps": state["processing_steps"] + [
            "assign_technical_queue"
        ],
    }


def assign_order_queue(state: TicketState) -> dict:
    return {
        "assigned_queue": "Order Support",
        "routing_reason": "订单类问题分配给订单支持团队",
        "processing_steps": state["processing_steps"] + [
            "assign_order_queue"
        ],
    }


def manual_triage(state: TicketState) -> dict:
    return {
        "assigned_queue": "Manual Triage",
        "routing_reason": "无法识别工单类别，需要人工分流",
        "ticket_status": "needs_manual_triage",
        "processing_steps": state["processing_steps"] + [
            "manual_triage"
        ],
    }


def finalize_ticket(state: TicketState) -> dict:
    """Build the final ticket result."""
    category = state.get("category", "Not Classified")
    priority = state.get("priority", "Not Assessed")
    assigned_queue = state.get("assigned_queue", "Not Assigned")
    routing_reason = state.get("routing_reason", "")

    if state["ticket_status"] == "needs_manual_triage":
        status = "needs_manual_triage"
    elif state["ticket_status"] == "invalid":
        status = "invalid"
        category = "Not Classified"
        priority = "Not Assessed"
        assigned_queue = "Not Assigned"
        routing_reason = f"工单验证失败：{state['validation_error']}"
        
    else:
        status = "routed"

    matched_categories = state.get("matched_categories", [])
    matched_text = ", ".join(matched_categories) or "无匹配类别"


    result = (
        f"工单编号：{state['ticket_id']}\n"
        f"工单类别：{category}\n"
        f"优先级：{priority}\n"
        f"处理队列：{assigned_queue}\n"
        f"工单状态：{status}\n"
        f"分流说明：{routing_reason}\n"
        f"匹配类别：{matched_text}\n"
    )

    return {
        "ticket_status": status,
        "result": result,
        "processing_steps": state["processing_steps"] + [
            "finalize_ticket"
        ],
    }


# ============================================================
# 4. Define Conditional Routing Functions
# ============================================================

def route_validation(state: TicketState) -> str:
    if state["is_valid"]:
        return "valid"

    return "invalid"


def route_category(state: TicketState) -> str:
    return state["category"]


# ============================================================
# 5. Build LangGraph
# ============================================================

def build_ticket_graph():

    builder = StateGraph(TicketState)

    # Register nodes
    builder.add_node("validate_ticket", validate_ticket)
    builder.add_node("invalid_ticket", invalid_ticket)
    builder.add_node("classify_ticket", classify_ticket)
    builder.add_node("assess_priority", assess_priority)

    builder.add_node("assign_account_queue", assign_account_queue)
    builder.add_node("assign_technical_queue", assign_technical_queue)
    builder.add_node("assign_order_queue", assign_order_queue)
    builder.add_node("manual_triage", manual_triage)

    builder.add_node("finalize_ticket", finalize_ticket)

    # Entry point
    builder.add_edge(START, "validate_ticket")

    # Validation conditional routing
    builder.add_conditional_edges(
        "validate_ticket",
        route_validation,
        {
            "valid": "classify_ticket",
            "invalid": "invalid_ticket",
        },
    )

    # Invalid tickets terminate directly
    builder.add_edge("invalid_ticket", "finalize_ticket")

    # Normal processing sequence
    builder.add_edge("classify_ticket", "assess_priority")

    # Category conditional routing
    builder.add_conditional_edges(
        "assess_priority",
        route_category,
        {
            "Account": "assign_account_queue",
            "Technical": "assign_technical_queue",
            "Order": "assign_order_queue",
            "Unknown": "manual_triage",
            "Multiple": "manual_triage",
        },
    )

    # All routing branches converge on finalization
    builder.add_edge("assign_account_queue", "finalize_ticket")
    builder.add_edge("assign_technical_queue", "finalize_ticket")
    builder.add_edge("assign_order_queue", "finalize_ticket")
    builder.add_edge("manual_triage", "finalize_ticket")

    builder.add_edge("finalize_ticket", END)

    return builder.compile()


# ============================================================
# 6. Run Test Cases
# ============================================================

def run_test(graph, title: str, ticket_id: str, message: str):

    initial_state: TicketState = {
        "ticket_id": ticket_id,
        "user_message": message,

        "is_valid": False,
        "validation_error": "",

        "category": "",
        "priority": "",

        "assigned_queue": "",
        "routing_reason": "",

        "ticket_status": "",
        "result": "",

        "processing_steps": [],
    }

    result = graph.invoke(initial_state)

    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)

    print(result["result"])

    print("\n实际执行节点：")
    print(" -> ".join(result["processing_steps"]))


def main():

    graph = build_ticket_graph()

    run_test(
        graph,
        "TEST 1：账号问题",
        "T001",
        "我登录账号时提示密码错误",
    )

    run_test(
        graph,
        "TEST 2：严重技术故障",
        "T002",
        "系统发生严重崩溃，现在完全无法使用",
    )

    run_test(
        graph,
        "TEST 3：订单问题",
        "T003",
        "我的订单已经付款，但是一直没有发货",
    )

    run_test(
        graph,
        "TEST 4：无效工单",
        "T004",
        "",
    )

    run_test(
        graph,
        "TEST 5：无法识别的工单类别",
        "T005",
        "我想咨询一下企业合作事宜",
    )
    run_test(
    graph,
    "TEST 6：多类别工单",
    "T006",
    "我无法登录账号，而且订单付款后一直没有发货",
     )


if __name__ == "__main__":
    main()
