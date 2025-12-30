from crewai.tools import BaseTool
from pypdf import PdfReader
import os
from typing import Optional

def _get_pdf_path(file_path: Optional[str]) -> str:
    """Helper to resolve PDF path."""
    if file_path and file_path != 'None' and os.path.exists(file_path):
        return file_path
    
    # Try to find latest in reports/
    # Check for env var override
    custom_output_dir = os.environ.get("REPORT_OUTPUT_DIR")
    if custom_output_dir and os.path.exists(custom_output_dir):
        reports_dir = custom_output_dir
    else:
        reports_dir = os.path.join(os.getcwd(), 'reports')
        
    if not os.path.exists(reports_dir):
        raise FileNotFoundError("Reports directory not found.")
    files = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if f.endswith('.pdf')]
    if not files:
        raise FileNotFoundError("No PDF files found in reports directory.")
    # Sort by modification time
    return max(files, key=os.path.getmtime)

class PDFCatalogTool(BaseTool):
    name: str = "PDF Catalog/TOC Reader"
    description: str = "Reads the first 15 pages of a PDF to find the Table of Contents (Directory). Use this FIRST to understand the document structure."

    def _run(self, file_path: str = None) -> str:
        try:
            resolved_path = _get_pdf_path(file_path)
            reader = PdfReader(resolved_path)
            
            full_text = []
            # Read first 15 pages (covers most TOCs)
            page_limit = min(15, len(reader.pages))
            
            for i in range(page_limit):
                text = reader.pages[i].extract_text()
                if text:
                    full_text.append(f"--- Page {i+1} ---\n{text}")
            
            return f"Use these initial pages to identify the relevant chapter page numbers:\n\n" + "\n".join(full_text)
            
        except Exception as e:
            return f"Error reading PDF catalog: {str(e)}"

class PDFContentReaderTool(BaseTool):
    name: str = "PDF Specific Pages Reader"
    description: str = "Reads specific page ranges from a PDF. Input page range should be comma-separated or hyphenated (e.g. '20-25' or '20, 22, 30')."

    def _run(self, page_range: str, file_path: str = None) -> str:
        try:
            resolved_path = _get_pdf_path(file_path)
            reader = PdfReader(resolved_path)
            total_pages = len(reader.pages)
            
            pages_to_read = set()
            
            # Parse page range
            # Supports "20-25", "20, 21", "20-22, 25"
            parts = page_range.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    # PDF pages are 0-indexed in code, but 1-indexed in human request
                    # Input is human (1-indexed)
                    for p in range(start, end + 1):
                        if 1 <= p <= total_pages:
                            pages_to_read.add(p)
                else:
                    try:
                        p = int(part)
                        if 1 <= p <= total_pages:
                            pages_to_read.add(p)
                    except ValueError:
                        continue
            
            sorted_pages = sorted(list(pages_to_read))
            if not sorted_pages:
                return "No valid pages to read."
            
            # Limit to 50 pages to prevent context explosion
            if len(sorted_pages) > 50:
                sorted_pages = sorted_pages[:50]
                warning = "\n(Warning: Truncated to first 50 requested pages)"
            else:
                warning = ""
                
            full_text = []
            for p in sorted_pages:
                # p is 1-indexed, convert to 0-indexed
                text = reader.pages[p-1].extract_text()
                if text:
                    full_text.append(f"--- Page {p} ---\n{text}")
            
            return f"Content from pages {sorted_pages}:{warning}\n\n" + "\n".join(full_text)
            
        except Exception as e:
            return f"Error reading PDF pages: {str(e)}"
