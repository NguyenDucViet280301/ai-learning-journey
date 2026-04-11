from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import config

class AgentEngine:
    """The HEART of the Agent system. Reasoning loop independent of tool types."""
    
    def __init__(self, system_prompt, tools=[]):
        self.llm = ChatOllama(
            model=config.DEFAULT_MODEL,
            temperature=config.TEMPERATURE,
            base_url=config.OLLAMA_BASE_URL
        ).bind_tools(tools)
        
        self.system_prompt = system_prompt
        self.tools_map = {tool.name: tool for tool in tools}

    def run(self, user_input, chat_history=[]):
        # 🧠 CONTEXT PROTECTION: Set system message first
        messages = [("system", self.system_prompt)]
        
        # Add chat history (HumanMessage/AIMessage objects)
        if chat_history:
            messages.extend(chat_history)
            
        # Add the actual user input
        messages.append(("human", user_input))
        
        current_turn = 0
        while current_turn < config.MAX_REASONING_TURNS:
            current_turn += 1
            response = self.llm.invoke(messages)
            
            # 1. AI provides final answer
            if not response.tool_calls:
                return response.content
            
            # 2. AI wants to call a Tool
            messages.append(response)
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"].lower()
                if tool_name in self.tools_map:
                    try:
                        observation = self.tools_map[tool_name].invoke(tool_call["args"])
                    except Exception as e:
                        observation = f"Tool Error '{tool_name}': {e}"
                else:
                    observation = f"Tool '{tool_name}' does not exist in the arsenal."
                
                messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(observation)))

        # 3. Final response if max turns reached (Protection Guard)
        messages.append(("human", "Please summarize the information and answer now."))
        final_response = self.llm.invoke(messages)
        return final_response.content
