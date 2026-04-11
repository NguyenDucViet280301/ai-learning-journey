import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from datetime import datetime
from pydantic import BaseModel, Field
import config

# --- 📦 SCHEMAS ---
class CreatePlanInput(BaseModel):
    plan: str = Field(description="Outline of research steps.")

class WebSearchInput(BaseModel):
    query: str = Field(description="Internet search query.")

class SummarizeWebpageInput(BaseModel):
    url: str = Field(description="URL starting with http/https.")

class SaveResearchReportInput(BaseModel):
    content: str = Field(description="Detailed research report content.")

# --- 🛠️ TOOLS ---

@tool(args_schema=CreatePlanInput)
def create_plan(plan: str):
    """MANDATORY first step: To outline research steps."""
    return f"ACTION PLAN recorded:\n{plan}"

try:
    ddg_search = DuckDuckGoSearchResults(num_results=3)
except Exception:
    ddg_search = None

@tool(args_schema=WebSearchInput)
def web_search(query: str):
    """Searches for URLs on the Internet."""
    if ddg_search is None:
        return "Error: DuckDuckGoSearchResults not configured. Please install 'duckduckgo-search'."
    try:
        return ddg_search.run(query)
    except Exception as e:
        return f"Search Error: {e}"

@tool(args_schema=SummarizeWebpageInput)
def summarize_webpage(url: str):
    """Reads and summarizes the content of a long webpage."""
    url_stripped = url.strip("[]'\" \n\r\t").split()[0]
    parsed = urllib.parse.urlparse(url_stripped)
    if not parsed.scheme or not parsed.netloc:
        return f"Invalid URL '{url_stripped}'."
    
    clean_url = urllib.parse.urlunparse(parsed)
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(clean_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for e in soup(["script", "style"]): e.decompose()
            
        elements = soup.find_all(['p', 'h1', 'h2', 'h3'])
        text = "\n".join([e.get_text().strip() for e in elements if len(e.get_text().strip()) > 30])
        
        if not text: return "Webpage has no text content."
            
        summary_llm = ChatOllama(model=config.DEFAULT_MODEL, temperature=0, base_url=config.OLLAMA_BASE_URL)
        prompt = f"Summarize the following article briefly in under 200 words:\n\n{text[:3000]}"
        return summary_llm.invoke(prompt).content[:800] + "..."
    except Exception as e:
        return f"Page access error: {e}"

@tool(args_schema=SaveResearchReportInput)
def save_research_report(content: str):
    """Saves the report to a file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_{timestamp}.md"
        path = os.path.join(config.OUTPUT_DIR, filename)
        
        header = f"# 🎓 RESEARCH REPORT (DAY 26)\n**Export Date**: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n---\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + content)
            
        return f"✅ File saved: {filename}"
    except Exception as e:
        return f"File saving error: {e}"

# Package tool list for easy engine loading
RESEARCH_TOOLS = [create_plan, web_search, summarize_webpage, save_research_report]
