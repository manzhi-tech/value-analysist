import os
from dotenv import load_dotenv
# Use community version for native DashScope support, avoids OpenAI config conflicts
from langchain_community.chat_models import ChatTongyi

load_dotenv()

def get_qwen_llm():
    """
    Returns a configured ChatTongyi instance (Aliyun Native).
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key or "PLEASE_PASTE" in api_key:
        raise ValueError("Invalid or missing DASHSCOPE_API_KEY. Please check your .env file.")

    # ChatTongyi automatically looks for DASHSCOPE_API_KEY, 
    # but we pass it explicitly to be sure.
    return ChatTongyi(
        model="qwen-flash",
        dashscope_api_key=api_key,
        temperature=0.1
    )
