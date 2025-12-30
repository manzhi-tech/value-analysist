import os
import requests
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun

class ReportSearchTool(BaseTool):
    name: str = "Annual Report Search Tool"
    description: str = "Search for the latest annual report PDF link for a given company or stock code on cninfo.com.cn."

    def _run(self, query: str) -> str:
        try:
            # Try importing the new package name first, then fallback
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            
            import datetime
            # Calculate target year (usually previous year for annual reports)
            # If current month is early in the year (e.g. before April), the report might not be out,
            # but usually we search for the previous year's report.
            current_year = datetime.datetime.now().year
            target_year = current_year - 1
            
            results = []
            queries = [
                f"site:cninfo.com.cn {query} {target_year} 年报 PDF",
                f"{query} {target_year} 年报 PDF cninfo",
                f"{query} {target_year} Annual Report PDF",
                # Also try searching without year to catch "latest" indexed pages
                f"site:cninfo.com.cn {query} 最新 年报 PDF"
            ]

            with DDGS() as ddgs:
                for q in queries:
                    try:
                        # Use 'text' method as per new API, backend='auto' is default
                        # restrict max_results to avoid rate limits
                        search_results = list(ddgs.text(q, max_results=3))
                        if search_results:
                            for r in search_results:
                                title = r.get('title', '')
                                link = r.get('href', '')
                                snippet = r.get('body', '')
                                results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")
                    except Exception as e:
                        print(f"Search warning for query '{q}': {e}")
                        continue
        
            if not results:
                return "No results found for annual report. Please try providing a specific stock code."
            
            # Deduplicate results based on link
            unique_results = {}
            for r in results:
                link = r.split("Link: ")[1].split("\n")[0]
                if link not in unique_results:
                    unique_results[link] = r
            
            return "\n\n".join(list(unique_results.values())[:5])

        except Exception as e:
            return f"Search tool failed: {str(e)}"

class FileDownloadTool(BaseTool):
    name: str = "File Download Tool"
    description: str = "Download a file from a specific URL and save it to the local directory. Input should be the URL."

    def _run(self, url: str) -> str:
        try:
            # Basic cleanup if the URL is wrapped in quotes or markdown
            clean_url = url.strip().strip("'").strip('"').split('(')[-1].strip(')')
            
            if not clean_url.startswith("http"):
                 return f"Error: Invalid URL provided: {url}"

            # Create reports directory if it doesn't exist
            # Check for env var override
            custom_output_dir = os.environ.get("REPORT_OUTPUT_DIR")
            if custom_output_dir:
                reports_dir = custom_output_dir
            else:
                reports_dir = os.path.join(os.getcwd(), 'reports')
                
            os.makedirs(reports_dir, exist_ok=True)

            filename = clean_url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            
            # Ensure unique filename if generic
            if filename == "download.pdf" or len(filename) < 5:
                import uuid
                filename = f"report_{uuid.uuid4()}.pdf"
            
            file_path = os.path.join(reports_dir, filename)

            # User agent to avoid 403s
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(clean_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return f"Successfully downloaded file to: {file_path}"
        except Exception as e:
            return f"Failed to download file: {str(e)}"
