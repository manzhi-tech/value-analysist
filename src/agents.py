import os
import yaml
from crewai import Agent
from src.config import get_qwen_llm
from src.tools.report_tools import ReportSearchTool, FileDownloadTool

def get_annual_report_agent():
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'agents.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    agent_config = config['annual_report_finder']
    
    return Agent(
        role=agent_config['role'],
        goal=agent_config['goal'],
        backstory=agent_config['backstory'],
        tools=[ReportSearchTool(), FileDownloadTool()],
        llm=get_qwen_llm(),
        verbose=True,
        allow_delegation=False
    )
