from crewai.tools import BaseTool
import pdfplumber
from pydantic import BaseModel, Field
from typing import Type
from src.core.llm_factory import llm_factory

class FinancialTableToolInput(BaseModel):
    file_path: str = Field(..., description="PDF 文件的绝对路径")
    page_number: int = Field(..., description="包含表格的页码 (从 1 开始)")
    table_description: str = Field(..., description="要提取的表格描述 (例如 '利润表', '资产负债表')")

class FinancialTableTool(BaseTool):
    name: str = "Financial Table Extractor"
    description: str = (
        "Extracts financial tables from a specific PDF page using an LLM. "
        "Useful for getting structured data tables like Income Statement, Balance Sheet, etc."
    )
    args_schema: Type[BaseModel] = FinancialTableToolInput

    def _run(self, file_path: str, page_number: int, table_description: str) -> str:
        # 1. Extract text from the page
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    return f"错误: 页码 {page_number} 超出范围。"
                page = pdf.pages[page_number - 1]
                # Extract text preserving layout as much as possible
                text_content = page.extract_text(layout=True)
        except Exception as e:
            return f"读取 PDF 错误: {str(e)}"

        # 2. Use LLM to parse the table
        prompt = f"""
        你是一位专业的财务分析师。你的任务是从下面的文本中提取 '{table_description}'。
        
        规则:
        1. 仅以有效的 JSON 格式返回数据。
        2. JSON 应该是表示行的列表或对象列表。
        3. 不要包含任何 markdown 格式（如 ```json），只返回原始 JSON 字符串。
        4. 如果表格被截断，请提取可见部分。
        
        源文本:
        {text_content}
        """

        # Get LLM instance
        llm = llm_factory.get_llm()
        
        # Invoke LLM
        response = llm.invoke(prompt)
        
        return response.content
