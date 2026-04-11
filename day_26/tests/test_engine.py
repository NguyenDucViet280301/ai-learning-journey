import pytest
from unittest.mock import MagicMock, patch
from engine import AgentEngine
from langchain_core.messages import AIMessage, ToolMessage
import config

@patch("engine.ChatOllama")
def test_engine_no_tools_needed(mock_chat):
    # Mock LLM response: final answer directly
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = AIMessage(content="Final answer.")
    mock_chat.return_value.bind_tools.return_value = mock_llm_instance
    
    engine = AgentEngine(system_prompt="You are an assistant.")
    result = engine.run(user_input="Hello")
    
    assert result == "Final answer."
    mock_llm_instance.invoke.assert_called_once()


@patch("engine.ChatOllama")
def test_engine_with_tool_call(mock_chat):
    # Mock LLM instance 
    mock_llm_instance = MagicMock()
    
    # 1. AI calls tool 'test_tool'
    tool_call = {
        "name": "test_tool",
        "args": {"arg1": "val1"},
        "id": "call_123"
    }
    
    # First invoke returns tool_calls, second returns final result
    mock_llm_instance.invoke.side_effect = [
        AIMessage(content="", tool_calls=[tool_call]),
        AIMessage(content="Report complete.")
    ]
    
    mock_chat.return_value.bind_tools.return_value = mock_llm_instance
    
    # Create mock tool
    mock_tool = MagicMock()
    mock_tool.name = "test_tool"
    mock_tool.invoke.return_value = "Tool result"
    
    engine = AgentEngine(system_prompt="You are an assistant.", tools=[mock_tool])
    result = engine.run(user_input="Run the tool")
    
    assert result == "Report complete."
    assert mock_llm_instance.invoke.call_count == 2
    mock_tool.invoke.assert_called_once_with({"arg1": "val1"})

@patch("engine.ChatOllama")
def test_engine_max_turns(mock_chat):
    # Mock LLM always requesting tool (infinite loop simulation)
    mock_llm_instance = MagicMock()
    tool_call = {"name": "test_tool", "args": {}, "id": "1"}
    mock_llm_instance.invoke.return_value = AIMessage(content="", tool_calls=[tool_call])
    
    mock_chat.return_value.bind_tools.return_value = mock_llm_instance
    
    mock_tool = MagicMock()
    mock_tool.name = "test_tool"
    
    # Lower MAX_REASONING_TURNS for faster testing
    with patch("config.MAX_REASONING_TURNS", 2):
        engine = AgentEngine(system_prompt="Prompt", tools=[mock_tool])
        result = engine.run(user_input="Loop")
        
        # expect it to finish eventually via the protection guard 
        assert mock_llm_instance.invoke.call_count == 3 # 2 turns + 1 protect guard
