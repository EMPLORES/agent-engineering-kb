from types import SimpleNamespace
from unittest.mock import patch

import os
import json

from typing import TypedDict
from dotenv import load_dotenv
from openai import OpenAI

from langgraph.graph import StateGraph, START, END

load_dotenv()


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

    confidence: str
    classification_reason: str
    classification_error: str

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


def apply_confidence_gate(category: str, confidence: str) -> str:
    """Apply confidence-based routing rules."""

    auto_route_categories = {
        "Account",
        "Technical",
        "Order"
    }

    if category in auto_route_categories and confidence != "High":
        return "Unknown"

    return category

def run_confidence_gate_tests():
    """Test confidence gate without calling the LLM."""

    test_cases = [
        # Account
        ("Account", "High", "Account"),
        ("Account", "Medium", "Unknown"),
        ("Account", "Low", "Unknown"),

        # Technical
        ("Technical", "High", "Technical"),
        ("Technical", "Medium", "Unknown"),
        ("Technical", "Low", "Unknown"),

        # Order
        ("Order", "High", "Order"),
        ("Order", "Medium", "Unknown"),
        ("Order", "Low", "Unknown"),

        # Unknown
        ("Unknown", "High", "Unknown"),
        ("Unknown", "Medium", "Unknown"),
        ("Unknown", "Low", "Unknown"),

        # Multiple
        ("Multiple", "High", "Multiple"),
        ("Multiple", "Medium", "Multiple"),
        ("Multiple", "Low", "Multiple"),
    ]

    print("\n=======================================================")
    print("置信度门控测试")
    print("=======================================================")

    passed = 0
    failures = []

    for index, (category, confidence, expected) in enumerate(
        test_cases, start=1
    ):
        actual = apply_confidence_gate(category, confidence)

        if actual == expected:
            passed += 1
            print(
                f"PASS {index}: "
                f"{category} + {confidence} -> {actual}"
            )
        else:
            failures.append(
                f"TEST {index}: expected {expected}, got {actual}"
            )
            print(
                f"FAIL {index}: "
                f"{category} + {confidence} -> {actual}"
            )

    print("-------------------------------------------------------")
    print(f"测试结果：{passed}/{len(test_cases)} 通过")

    if failures:
        for failure in failures:
            print(failure)
        raise AssertionError("Confidence gate tests failed")

    print("所有置信度门控测试通过！")

def classify_ticket(state: TicketState) -> dict:
    """Classify a ticket using DeepSeek structured output."""

    try:
        api_key = os.getenv("LANGGRAPH_API_KEY")
        base_url = os.getenv("LANGGRAPH_BASE_URL")
        model = os.getenv("LANGGRAPH_MODEL")

        if not api_key or not base_url or not model:
            raise ValueError("Missing API configuration")

        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        system_prompt = """
你是一个客服工单分类助手。

请根据用户提供的工单内容判断业务类别。

允许的类别：
- Account：账号、登录、密码、账户问题
- Technical：系统故障、程序错误、功能异常
- Order：订单、付款、支付、物流、发货、退款
- Unknown：无法明确判断类别
- Multiple：同时涉及多个业务类别

信心等级：
- High：描述清晰，分类依据明确
- Medium：有一定依据，但存在不确定性
- Low：描述模糊，无法可靠判断

规则：
1. matched_categories 只能包含 Account、Technical、Order。
2. 没有匹配类别时，category 必须是 Unknown。
3. 同时涉及多个类别时，category 必须是 Multiple。
4. 只有一个匹配类别时，category 必须与该类别一致。
5. 不要为了给出分类而猜测。
6. 必须包含 category、matched_categories、
   confidence、reason 四个字段。
7. 只输出 JSON，不输出其他文字。

示例：
{
    "category": "Technical",
    "matched_categories": ["Technical"],
    "confidence": "High",
    "reason": "用户描述了系统故障"
}
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": state["user_message"]
                }
            ],
            response_format={
                "type": "json_object"
            },
            max_tokens=300
        )

        message = response.choices[0].message
        content = message.content

        if not content or not content.strip():
            raise ValueError("Empty model response")

        if response.choices[0].finish_reason == "length":
            raise ValueError("Model output was truncated")

        classification = json.loads(content)

        required_fields = {
            "category",
            "matched_categories",
            "confidence",
            "reason"
        }

        if not required_fields.issubset(classification.keys()):
            raise ValueError("Missing required fields")

        category = classification["category"]
        matched_categories = classification["matched_categories"]
        confidence = classification["confidence"]
        reason = classification["reason"]

        allowed_categories = {
            "Account", "Technical", "Order",
            "Unknown", "Multiple"
        }

        allowed_matches = {
            "Account", "Technical", "Order"
        }

        allowed_confidence = {
            "High", "Medium", "Low"
        }

        if category not in allowed_categories:
            raise ValueError("Invalid category")

        if not isinstance(matched_categories, list):
            raise ValueError("Invalid matched_categories")

        if not all(
            item in allowed_matches
            for item in matched_categories
        ):
            raise ValueError("Invalid matched category")

        if len(matched_categories) != len(set(matched_categories)):
            raise ValueError("Duplicate matched categories")

        if confidence not in allowed_confidence:
            raise ValueError("Invalid confidence")

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Invalid reason")

        # Check whether category and matched_categories agree.
        if category == "Unknown" and matched_categories:
            raise ValueError("Inconsistent Unknown classification")

        if category == "Multiple" and len(matched_categories) < 2:
            raise ValueError("Inconsistent Multiple classification")

        if category in allowed_matches:
            if matched_categories != [category]:
                raise ValueError("Inconsistent single classification")

        # Only High-confidence single-category results
        # are allowed to enter automatic routing.
        category = apply_confidence_gate(category, confidence)


        return {
            "category": category,
            "matched_categories": matched_categories,
            "confidence": confidence,
            "classification_reason": reason,
            "classification_error": "",
            "processing_steps": state["processing_steps"] + [
                "classify_ticket"
            ],
        }

    except Exception as error:
        # Fail safely: do not automatically route an
        # unverified model result.
        return {
            "category": "Unknown",
            "matched_categories": [],
            "confidence": "Low",
            "classification_reason": "模型调用或结果校验失败，需要人工处理",
            "classification_error": type(error).__name__,
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
    matched_categories = state.get("matched_categories", [])
    confidence = state.get("confidence") or "不适用（未执行分类）"
    classification_reason = state.get("classification_reason") or "不适用（工单验证未通过，未执行分类）"
    classification_error = state.get("classification_error")

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
        f"置信度：{confidence}\n"
        f"分类理由：{classification_reason}\n"
        f"异常信息：{classification_error or '无'}\n"
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

        "matched_categories": [],
        "confidence": "",
        "classification_reason": "",
        "classification_error": "",
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

    run_confidence_gate_tests()

    run_confidence_routing_integration_tests(graph)

    run_classification_failure_integration_tests(graph)

def make_mock_llm_response(classification: dict):
    # 辅助函数
    """Create a mock DeepSeek response."""

    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=json.dumps(
                        classification,
                        ensure_ascii=False
                    )
                ),
                finish_reason="stop"
            )
        ]
    )

def make_mock_llm_response_content(content: str):
    """Create a mock response with raw content."""

    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=content
                ),
                finish_reason="stop"
            )
        ]
    )

def run_confidence_routing_integration_tests(graph):
    # 集成测试函数
    """Test confidence gate and actual LangGraph routing."""

    test_cases = [
        {
            "title": "Account + High",
            "message": "我登录账号时提示密码错误",
            "classification": {
                "category": "Account",
                "matched_categories": ["Account"],
                "confidence": "High",
                "reason": "账号问题，置信度高"
            },
            "expected_category": "Account",
            "expected_queue": "Account Support",
            "expected_status": "routed",
            "expected_route": "assign_account_queue",
        },
        {
            "title": "Account + Medium",
            "message": "我登录账号时提示密码错误",
            "classification": {
                "category": "Account",
                "matched_categories": ["Account"],
                "confidence": "Medium",
                "reason": "账号问题，置信度中等"
            },
            "expected_category": "Unknown",
            "expected_queue": "Manual Triage",
            "expected_status": "needs_manual_triage",
            "expected_route": "manual_triage",
        },
        {
            "title": "Account + Low",
            "message": "我登录账号时提示密码错误",
            "classification": {
                "category": "Account",
                "matched_categories": ["Account"],
                "confidence": "Low",
                "reason": "账号问题，置信度较低"
            },
            "expected_category": "Unknown",
            "expected_queue": "Manual Triage",
            "expected_status": "needs_manual_triage",
            "expected_route": "manual_triage",
        },
        {
            "title": "Unknown + High",
            "message": "我想咨询企业合作事宜",
            "classification": {
                "category": "Unknown",
                "matched_categories": [],
                "confidence": "High",
                "reason": "不属于现有业务类别"
            },
            "expected_category": "Unknown",
            "expected_queue": "Manual Triage",
            "expected_status": "needs_manual_triage",
            "expected_route": "manual_triage",
        },
        {
            "title": "Multiple + High",
            "message": "我无法登录账号，而且订单付款后未发货",
            "classification": {
                "category": "Multiple",
                "matched_categories": ["Account", "Order"],
                "confidence": "High",
                "reason": "同时涉及账号和订单问题"
            },
            "expected_category": "Multiple",
            "expected_queue": "Manual Triage",
            "expected_status": "needs_manual_triage",
            "expected_route": "manual_triage",
        },
    ]

    mock_env = {
        "LANGGRAPH_API_KEY": "mock-api-key",
        "LANGGRAPH_BASE_URL": "https://mock.example.com/v1",
        "LANGGRAPH_MODEL": "mock-model",
    }

    print("\n" + "=" * 55)
    print("置信度门控与 LangGraph 路由集成测试")
    print("=" * 55)

    passed = 0
    failures = []

    for index, case in enumerate(test_cases, start=1):

        initial_state: TicketState = {
            "ticket_id": f"MOCK-{index}",
            "user_message": case["message"],

            "is_valid": False,
            "validation_error": "",

            "category": "",
            "priority": "",

            "assigned_queue": "",
            "routing_reason": "",

            "ticket_status": "",
            "result": "",

            "processing_steps": [],

            "matched_categories": [],
            "confidence": "",
            "classification_reason": "",
            "classification_error": "",
        }

        mock_response = make_mock_llm_response(
            case["classification"]
        )

        # Mock only the OpenAI client response.
        # The real classify_ticket() and LangGraph still execute.
        with patch.dict(os.environ, mock_env):
            with patch(f"{__name__}.OpenAI") as mock_openai:

                mock_openai.return_value.chat.completions.create.return_value = (
                    mock_response
                )

                result = graph.invoke(initial_state)

        expected_steps = [
            "validate_ticket",
            "classify_ticket",
            "assess_priority",
            case["expected_route"],
            "finalize_ticket",
        ]

        checks = {
            "category": (
                result["category"] == case["expected_category"]
            ),
            "queue": (
                result["assigned_queue"] == case["expected_queue"]
            ),
            "status": (
                result["ticket_status"] == case["expected_status"]
            ),
            "execution_path": (
                result["processing_steps"] == expected_steps
            ),
        }

        if all(checks.values()):
            passed += 1
            print(f"PASS {index}: {case['title']}")
        else:
            failed_checks = [
                name for name, passed_check in checks.items()
                if not passed_check
            ]

            failures.append(case["title"])

            print(f"FAIL {index}: {case['title']}")
            print(f"失败检查项：{failed_checks}")

        print(
            f"  分类：{result['category']} | "
            f"队列：{result['assigned_queue']} | "
            f"状态：{result['ticket_status']}"
        )

        print(
            "  执行节点："
            + " -> ".join(result["processing_steps"])
        )

    print("-" * 55)
    print(f"集成测试结果：{passed}/{len(test_cases)} 通过")

    if failures:
        print("失败测试：", failures)
        raise AssertionError("Confidence routing integration tests failed")

    print("所有置信度门控与路由集成测试通过！")

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

def run_classification_failure_integration_tests(graph):
    """Test classification failures and safe recovery."""

    test_cases = [
        {
            "title": "API 调用异常",
            "failure_type": "api_error",
            "expected_error": "ConnectionError",
        },
        {
            "title": "非法 JSON 响应",
            "failure_type": "invalid_json",
            "expected_error": "JSONDecodeError",
        },
        {
            "title": "业务校验失败",
            "failure_type": "invalid_category",
            "expected_error": "ValueError",
        },
    ]

    mock_env = {
        "LANGGRAPH_API_KEY": "mock-api-key",
        "LANGGRAPH_BASE_URL": "https://mock.example.com/v1",
        "LANGGRAPH_MODEL": "mock-model",
    }

    print("\n" + "=" * 55)
    print("LLM 分类异常与安全恢复集成测试")
    print("=" * 55)

    passed = 0
    failures = []

    for index, case in enumerate(test_cases, start=1):

        initial_state: TicketState = {
            "ticket_id": f"ERROR-{index}",
            "user_message": "我登录账号时提示密码错误",

            "is_valid": False,
            "validation_error": "",

            "category": "",
            "priority": "",

            "assigned_queue": "",
            "routing_reason": "",

            "ticket_status": "",
            "result": "",

            "processing_steps": [],

            "matched_categories": [],
            "confidence": "",
            "classification_reason": "",
            "classification_error": "",
        }

        with patch.dict(os.environ, mock_env):
            with patch(f"{__name__}.OpenAI") as mock_openai:

                create = (
                    mock_openai.return_value
                    .chat.completions.create
                )

                if case["failure_type"] == "api_error":
                    create.side_effect = ConnectionError(
                        "Simulated API connection failure"
                    )

                elif case["failure_type"] == "invalid_json":
                    create.return_value = (
                        make_mock_llm_response_content(
                            "{invalid json"
                        )
                    )

                elif case["failure_type"] == "invalid_category":
                    create.return_value = make_mock_llm_response({
                        "category": "Billing",
                        "matched_categories": [],
                        "confidence": "High",
                        "reason": "Simulated invalid category"
                    })

                result = graph.invoke(initial_state)

        expected_steps = [
            "validate_ticket",
            "classify_ticket",
            "assess_priority",
            "manual_triage",
            "finalize_ticket",
        ]

        checks = {
            "category": (
                result["category"] == "Unknown"
            ),
            "confidence": (
                result["confidence"] == "Low"
            ),
            "error_type": (
                result["classification_error"]
                == case["expected_error"]
            ),
            "queue": (
                result["assigned_queue"] == "Manual Triage"
            ),
            "status": (
                result["ticket_status"]
                == "needs_manual_triage"
            ),
            "execution_path": (
                result["processing_steps"] == expected_steps
            ),
        }

        if all(checks.values()):
            passed += 1
            print(f"PASS {index}: {case['title']}")
        else:
            failed_checks = [
                name
                for name, passed_check in checks.items()
                if not passed_check
            ]

            failures.append(case["title"])

            print(f"FAIL {index}: {case['title']}")
            print(f"失败检查项：{failed_checks}")

        print(
            f"  分类：{result['category']} | "
            f"置信度：{result['confidence']} | "
            f"异常：{result['classification_error']}"
        )

        print(
            f"  处理队列：{result['assigned_queue']} | "
            f"状态：{result['ticket_status']}"
        )

        print(
            "  执行节点："
            + " -> ".join(result["processing_steps"])
        )

    print("-" * 55)
    print(f"异常恢复测试结果：{passed}/{len(test_cases)} 通过")

    if failures:
        print("失败测试：", failures)
        raise AssertionError(
            "Classification failure recovery tests failed"
        )

    print("所有异常恢复测试通过！")

if __name__ == "__main__":
    main()
