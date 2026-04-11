from engine import AgentEngine
from tools import RESEARCH_TOOLS

class ResearchAgent(AgentEngine):
    """
    Extends AgentEngine and applies it to the RESEARCH domain.
    Day 26: Decoupling Prompts and Tools from the Core engine.
    """
    
    SYSTEM_PROMPT = """You are a Multi-Step AI Research Specialist (Research Master). ANSWER THE USER IN ENGLISH.
    
IRON RULES:
1. Upon receiving a user question, you MUST immediately use 'create_plan' to outline the research steps.
2. From that outline, use 'web_search' to find information and 'summarize_webpage' to read the data.
3. After gathering enough information, SYNTHESIZE all data into a deep, professional research report with clear Markdown headers.
4. DO NOT repeat search more than 5 times. If not found, report based on what is available."""

    def __init__(self):
        super().__init__(
            system_prompt=self.SYSTEM_PROMPT,
            tools=RESEARCH_TOOLS
        )

def get_agent():
    return ResearchAgent()
