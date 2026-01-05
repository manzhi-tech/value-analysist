import os
from openai import OpenAI

# 从 .env 读取配置 (模拟)
# LLM_API_KEY=ba6e9c81-c8b6-416f-bd55-a8c13f989894
# LLM_API_BASE=https://ark.cn-beijing.volces.com/api/v3
# EMBEDDING_MODEL=doubao-embedding-vision-250615

api_key = "ba6e9c81-c8b6-416f-bd55-a8c13f989894"
api_base = "https://ark.cn-beijing.volces.com/api/v3"
model = "doubao-embedding-vision-250615" # Suspicious model name

print(f"Testing Embedding API with model: {model}")
print(f"Base URL: {api_base}")

client = OpenAI(
    api_key=api_key,
    base_url=api_base,
)

try:
    resp = client.embeddings.create(
        input="This is a test sentence.",
        model=model
    )
    print("Success!")
    print(resp.data[0].embedding[:5])
except Exception as e:
    print(f"Error: {e}")
