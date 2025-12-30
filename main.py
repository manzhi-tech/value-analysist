import sys
import os
from dotenv import load_dotenv

# Load env vars before importing anything else to ensure libs pick them up
load_dotenv()

# Ensure we map API_BASE to BASE_URL if needed
if os.getenv("OPENAI_API_BASE") and not os.getenv("OPENAI_BASE_URL"):
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_API_BASE")

from crewai import Crew, Process
from src.agents import get_annual_report_agent, get_business_analyst_agent
from src.tasks import get_download_report_task, get_business_analysis_task

def main():
    if len(sys.argv) < 2:
        # If no argument, ask for input
        print("Please provide a stock code or company name.")
        company_input = input("Enter Stock Code or Name: ")
    else:
        company_input = sys.argv[1]

    print(f"Starting Annual Report Analysis for: {company_input}")

    # Set up output directory
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize company input for folder name
    safe_company_name = "".join([c for c in company_input if c.isalnum() or c in (' ', '_', '-')]).strip()
    output_dir = os.path.join(os.getcwd(), 'reports', f"{safe_company_name}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set env var for tools to pick up
    os.environ["REPORT_OUTPUT_DIR"] = output_dir
    print(f"Output directory set to: {output_dir}")

    # --- Phase 1: Download ---
    # Initialize Agent
    report_agent = get_annual_report_agent()

    # Initialize Task
    download_task = get_download_report_task(report_agent, company_input)

    # --- Phase 2: Analysis ---
    # Initialize Agent
    analyst_agent = get_business_analyst_agent()
    
    # Initialize Task (dependent on download_task)
    analysis_task = get_business_analysis_task(analyst_agent, context=[download_task])


    # Initialize Crew with both tasks
    crew = Crew(
        agents=[report_agent, analyst_agent],
        tasks=[download_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )

    # Execute
    result = crew.kickoff()
    
    print("\n################################################")
    print("## Execution Result")
    print("################################################\n")
    print(result)
    
    # Save the final report
    output_path = os.path.join(output_dir, 'analysis_report.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(result))
    print(f"\nFinal Analysis Report saved to: {output_path}")

if __name__ == "__main__":
    main()
