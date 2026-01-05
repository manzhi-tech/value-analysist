from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
import json

class AnalysisSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    company_name: Optional[str] = None
    
    # 存储文件路径列表的 JSON 字符串: '["/path/to/a.pdf", "/path/to/b.txt"]'
    file_paths_json: str = "[]" 
    
    # 将结果作为 JSON 字符串存储
    business_analysis_result: Optional[str] = None
    business_status: str = Field(default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    
    mda_analysis_result: Optional[str] = None
    mda_status: str = Field(default="PENDING")
    
    financial_analysis_result: Optional[str] = None
    financial_status: str = Field(default="PENDING")
    
    valuation_result: Optional[str] = None
    valuation_status: str = Field(default="PENDING")
    
    competitor_analysis_result: Optional[str] = None
    competitor_status: str = Field(default="PENDING")
    
    # 提取的数据
    extracted_financial_data: Optional[str] = None
    moat_rating: Optional[str] = None
    
    @property
    def file_paths(self) -> List[str]:
        return json.loads(self.file_paths_json)
    
    @file_paths.setter
    def file_paths(self, value: List[str]):
        self.file_paths_json = json.dumps(value)
