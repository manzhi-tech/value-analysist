from crewai import Agent, Crew, Process, Task
from pathlib import Path
from src.core.llm_factory import llm_factory
from src.agents.base_agent import AgentConfigLoader
from src.tools.dcf_calculator_tool import DCFCalculatorTool

class ValuationCrew:
    def __init__(self, financial_data: dict, moat_rating: str):
        self.financial_data = financial_data
        self.moat_rating = moat_rating
        self.agents_config, self.tasks_config = AgentConfigLoader.load_configs(Path(__file__).parent)
        self.llm = llm_factory.get_llm()

    def run(self) -> str:
        # 1. Tool
        dcf_tool = DCFCalculatorTool()

        # 2. Agent
        valuation_expert = Agent(
            config=self.agents_config['valuation_expert'],
            llm=self.llm,
            tools=[dcf_tool],
            verbose=True
        )

        # 3. Task
        valuation_task = Task(
            config=self.tasks_config['calculate_intrinsic_value'],
            agent=valuation_expert
        )

        # 4. Crew
        crew = Crew(
            agents=[valuation_expert],
            tasks=[valuation_task],
            process=Process.sequential,
            verbose=True
        )

        # 5. Kickoff
        result = crew.kickoff(inputs={
            'financial_data': self.financial_data,
            'moat_rating': self.moat_rating
        })
        return result
