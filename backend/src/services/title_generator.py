import pdfplumber
import logging
from src.core.llm_factory import llm_factory
from src.services.session_service import get_session, update_session

logger = logging.getLogger(__name__)

def generate_session_title(session_id: str, file_path: str):
    """
    Reads the first page of the PDF and asks the LLM to generate a concise title
    (e.g., "Company Name 2024 Annual Report").
    Updates the session's company_name field.
    """
    try:
        text_content = ""
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                text_content = first_page.extract_text()
                
        if not text_content:
            logger.warning(f"Could not extract text from first page of {file_path}")
            return

        # Truncate to avoid context limit issues, usually first page is enough
        text_content = text_content[:2000]

        prompt = f"""
You are a helpful assistant. Please identify the Company Name and the Report Type/Year from the following text (which is the cover page of a report).
Combine them into a short, professional title.
Examples: 
- "Apple Inc. 2023 Annual Report"
- "Tesla Q3 2024 Financial Results"
- "Kweichow Moutai 2025 Semi-Annual Report"

If you cannot identify them, just return the Company Name. If that fails, return "Unknown Report".
Do NOT include quotes in your output. Just the title.

Text:
{text_content}
"""
        llm = llm_factory.get_llm()
        # CrewAI LLM object usually has .call or .invoke or similar. 
        # Checking llm_factory usage in other files... 
        # It's usually a LangChain LLM or similar wrapper. 
        # Let's assume standard invoke or predict.
        # Actually in agent.py: self.llm = llm_factory.get_llm(); ... Agent(llm=self.llm...)
        # If it's langchain_openai.ChatOpenAI, it has .invoke() or .predict()
        
        response = llm.predict(prompt)
        title = response.strip().replace('"', '')
        
        logger.info(f"Generated title for session {session_id}: {title}")
        
        session = get_session(session_id)
        if session:
            session.company_name = title
            update_session(session)
            
    except Exception as e:
        logger.error(f"Error generating session title: {e}")
