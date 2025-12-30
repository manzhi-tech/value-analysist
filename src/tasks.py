import os
import yaml
from crewai import Task
from src.agents import get_annual_report_agent

def get_download_report_task(agent, company_input):
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'tasks.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    task_config = config['download_report_task']
    
    return Task(
        description=task_config['description'].format(company_input=company_input),
        expected_output=task_config['expected_output'],
        agent=agent
    )
