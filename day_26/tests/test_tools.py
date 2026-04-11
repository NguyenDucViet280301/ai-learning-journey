import pytest
import os
from unittest.mock import MagicMock, patch
from tools import create_plan, web_search, summarize_webpage, save_research_report
import config

def test_create_plan():
    plan = "Step 1: Research. Step 2: Analysis."
    result = create_plan.invoke({"plan": plan})
    assert "ACTION PLAN recorded:" in result
    assert plan in result

def test_web_search():
    with patch("tools.ddg_search") as mock_ddg:
        mock_ddg.run.return_value = "Result 1, Result 2"
        result = web_search.invoke({"query": "AI news"})
        assert result == "Result 1, Result 2"
        mock_ddg.run.assert_called_once_with("AI news")

@patch("tools.requests.get")
@patch("tools.ChatOllama")
def test_summarize_webpage(mock_chat, mock_get):
    # Mock requests.get
    mock_response = MagicMock()
    mock_response.text = "<h1>Test Title</h1><p>This is a long content for testing. " * 10
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    # Mock LLM
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value.content = "This is a summary."
    mock_chat.return_value = mock_llm_instance
    
    result = summarize_webpage.invoke({"url": "http://example.com"})
    assert "This is a summary." in result
    mock_get.assert_called_once()
    mock_chat.assert_called_once()

def test_save_research_report(tmp_path):
    # Use pytest tmp_path to avoid writing to actual directory
    test_output_dir = tmp_path / "outputs"
    test_output_dir.mkdir()
    
    with patch("config.OUTPUT_DIR", str(test_output_dir)):
        content = "Detailed report content."
        result = save_research_report.invoke({"content": content})
        
        assert "✅ File saved: Report_" in result
        
        # Verify file exists
        files = list(test_output_dir.glob("Report_*.md"))
        assert len(files) == 1
        with open(files[0], "r", encoding="utf-8") as f:
            saved_content = f.read()
            assert content in saved_content
