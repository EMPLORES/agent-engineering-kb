from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read LangGraph experiment configuration
api_key = os.getenv("LANGGRAPH_API_KEY")
base_url = os.getenv("LANGGRAPH_BASE_URL")
model = os.getenv("LANGGRAPH_MODEL")

print("API Key loaded:", bool(api_key))
print("Base URL:", base_url)
print("Model:", model)

# Initialize the API client
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

print("OpenAI client initialized successfully.")

# Send the first request to DeepSeek
response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "你好，请用一句话介绍你自己。"
        }
    ]
)

# Print the model response
print("\nDeepSeek response:")
print(response.choices[0].message.content)