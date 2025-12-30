import sys
import os
from dotenv import load_dotenv

# Load env vars before importing anything else to ensure libs pick them up
load_dotenv()

# Ensure we map API_BASE to BASE_URL if needed
if os.getenv("OPENAI_API_BASE") and not os.getenv("OPENAI_BASE_URL"):
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_API_BASE")

from crewai import Crew, Process
from src.agents import get_annual_report_agent
from src.tasks import get_download_report_task

def main():
    if len(sys.argv) < 2:
        # If no argument, ask for input
        print("Please provide a stock code or company name.")
        company_input = input("Enter Stock Code or Name: ")
    else:
        company_input = sys.argv[1]

    print(f"Starting Annual Report Downloader for: {company_input}")

    # Initialize Agent
    report_agent = get_annual_report_agent()

    # Initialize Task
    download_task = get_download_report_task(report_agent, company_input)

    # Initialize Crew
    crew = Crew(
        agents=[report_agent],
        tasks=[download_task],
        process=Process.sequential,
        verbose=True
    )

    # Execute
    result = crew.kickoff()
    
    print("\n################################################")
    print("## Execution Result")
    print("################################################\n")
    print(result)

if __name__ == "__main__":
    main()
