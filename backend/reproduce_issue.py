from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pathlib import Path
import os
import sys

# 设置模拟的环境变量，使用 OpenAI 兼容模式
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["OPENAI_API_BASE"] = "http://test-url"
os.environ["OPENAI_MODEL_NAME"] = "gpt-4"

file_path = "/Users/zhaozewei/Project/value-analysist/backend/uploads/茅台2024年年报.pdf"

print(f"Checking file: {file_path}")
if not os.path.exists(file_path):
    print("Error: File does not exist!")
    sys.exit(1)
print("File exists.")

try:
    print("Initializing PDFKnowledgeSource...")
    ks = PDFKnowledgeSource(file_paths=[file_path])
    print("PDFKnowledgeSource initialized successfully.")
    # 验证是否能够真正读取（这一步可能需要真实的 LLM 调用来生成 embedding，但这里只测试初始化路径检查）
    # validate_content() is called in post_init.
except Exception as e:
    print(f"Error initializing PDFKnowledgeSource: {e}")
    import traceback
    traceback.print_exc()
