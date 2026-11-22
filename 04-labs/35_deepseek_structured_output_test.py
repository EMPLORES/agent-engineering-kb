
import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# 1. Load API Configuration
# ============================================================

load_dotenv()

api_key = os.getenv("LANGGRAPH_API_KEY")
base_url = os.getenv("LANGGRAPH_BASE_URL")
model = os.getenv("LANGGRAPH_MODEL")

if not api_key or not base_url or not model:
    raise ValueError("Missing LangGraph API configuration in .env")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


# ============================================================
# 2. Define Classification Prompt
# ============================================================

system_prompt = """
你是一个客服工单分类助手。

请根据用户提供的工单内容，判断工单属于哪个业务类别。

允许的类别：
- Account：账号、登录、密码、账户问题
- Technical：系统故障、程序错误、功能异常
- Order：订单、付款、支付、物流、发货、退款
- Unknown：无法明确判断类别
- Multiple：同时涉及多个业务类别

信心等级：
- High：工单描述清晰，分类依据明确
- Medium：有一定依据，但存在部分不确定性
- Low：描述模糊，无法可靠判断

请输出 JSON 格式，不要输出其他文字。

输出格式示例：

{
    "category": "Technical",
    "matched_categories": ["Technical"],
    "confidence": "High",
    "reason": "用户描述了系统故障"
}

规则：
1. matched_categories 只能包含 Account、Technical、Order。
2. 没有明确匹配类别时，category 应为 Unknown。
3. 同时涉及多个类别时，category 应为 Multiple。
4. 不要为了给出分类而猜测。
5. 必须包含全部四个字段。
"""


# ============================================================
# 3. Call DeepSeek
# ============================================================

ticket_message = "系统发生严重崩溃，现在完全无法使用。"

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": ticket_message
        }
    ],
    response_format={
        "type": "json_object"
    },
    max_tokens=300
)


# ============================================================
# 4. Parse and Validate Result
# ============================================================

content = response.choices[0].message.content

if not content or not content.strip():
    raise ValueError("Model returned empty content.")

if response.choices[0].finish_reason == "length":
    raise ValueError("Model output was truncated.")

classification = json.loads(content)

required_fields = {
    "category",
    "matched_categories",
    "confidence",
    "reason"
}

if not required_fields.issubset(classification.keys()):
    raise ValueError("Missing required classification fields.")

allowed_categories = {
    "Account",
    "Technical",
    "Order",
    "Unknown",
    "Multiple"
}

allowed_matches = {
    "Account",
    "Technical",
    "Order"
}

allowed_confidence = {
    "High",
    "Medium",
    "Low"
}

category = classification["category"]
matched_categories = classification["matched_categories"]
confidence = classification["confidence"]
reason = classification["reason"]

if category not in allowed_categories:
    raise ValueError("Invalid category.")

if not isinstance(matched_categories, list):
    raise ValueError("matched_categories must be a list.")

if not all(item in allowed_matches for item in matched_categories):
    raise ValueError("Invalid matched category.")

if confidence not in allowed_confidence:
    raise ValueError("Invalid confidence level.")

if not isinstance(reason, str) or not reason.strip():
    raise ValueError("Invalid classification reason.")


# ============================================================
# 5. Display Result
# ============================================================

print("\nClassification Result:")
print(json.dumps(classification, ensure_ascii=False, indent=4))

print("\nValidation:")
print("JSON parsing: Passed")
print("Field validation: Passed")
print("Category validation: Passed")
print("Confidence validation: Passed")
