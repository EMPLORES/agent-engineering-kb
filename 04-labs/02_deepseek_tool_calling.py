import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# 1. 读取项目根目录中的 .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError(
        "未找到 DEEPSEEK_API_KEY，请检查项目根目录中的 .env"
    )


# 2. 连接 DeepSeek API
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=30.0,
    max_retries=1,
)


# 3. 定义本地工具
def divide(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        raise ValueError("参数必须是数字，不能是布尔值")

    if not isinstance(a, (int, float)):
        raise ValueError("参数 a 必须是数字")

    if not isinstance(b, (int, float)):
        raise ValueError("参数 b 必须是数字")

    if b == 0:
        raise ValueError("除数不能为零")

    return a / b


# 工具注册表：工具名称 -> 本地 Python 函数
TOOL_REGISTRY = {
    "divide": divide,
}


# 4. 向模型描述可用工具及参数
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "计算 a 除以 b，返回商。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "被除数",
                    },
                    "b": {
                        "type": "number",
                        "description": "除数",
                    },
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
    }
]


def run_agent(user_request, max_steps=5):
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个计算助手。"
                "用户要求进行除法计算时，必须调用 divide 工具。"
                "根据工具实际返回的结果回答，不要编造计算结果。"
            ),
        },
        {
            "role": "user",
            "content": user_request,
        },
    ]

    for step in range(1, max_steps + 1):
        print(f"\n[Runtime] 第 {step} 轮：请求 DeepSeek")

        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=False,
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            },
        )

        message = response.choices[0].message

        # 保存模型消息，包含可能存在的 tool_calls
        messages.append(
            message.model_dump(exclude_none=True)
        )

        # 模型没有请求工具，说明它直接返回了文本回答
        if not message.tool_calls:
            print("[Runtime] 模型返回最终回答")
            return message.content or "(没有文本回答)"

        # 5. Runtime 验证并执行工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name

            print(f"[Runtime] 收到工具调用：{tool_name}")

            try:
                if tool_name not in TOOL_REGISTRY:
                    raise ValueError(
                        f"不允许调用工具：{tool_name}"
                    )

                arguments = json.loads(
                    tool_call.function.arguments
                )

                if not isinstance(arguments, dict):
                    raise ValueError("参数必须是 JSON 对象")

                if set(arguments.keys()) != {"a", "b"}:
                    raise ValueError(
                        "divide 必须且只能接收 a、b 两个参数"
                    )

                result = TOOL_REGISTRY[tool_name](**arguments)

                tool_result = {
                    "ok": True,
                    "result": result,
                }

                print(f"[Tool] 执行成功：{result}")

            except Exception as exc:
                tool_result = {
                    "ok": False,
                    "error": str(exc),
                }

                print(
                    f"[Tool] 执行失败：{type(exc).__name__}"
                )

            # 6. 按照 tool_call_id 将工具结果交还给模型
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                    ),
                }
            )

    return "已达到最大执行轮数，Runtime 停止继续调用模型。"


if __name__ == "__main__":
    print("DeepSeek Tool Calling 实验")
    print("输入 exit 退出程序")

    while True:
        try:
            user_request = input("\n你：").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n程序退出")
            break

        if user_request.lower() == "exit":
            break

        if not user_request:
            continue

        try:
            answer = run_agent(user_request)
            print(f"\nAgent：{answer}")

        except Exception as exc:
            # 不输出完整异常信息，避免意外泄露请求中的敏感内容
            print(
                f"\n[请求失败] {type(exc).__name__}。"
                "请检查 API Key、网络、账户额度及接口配置。"
            )