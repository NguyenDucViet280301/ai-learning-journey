# 🏗️ Day 26: Testing Your AI Agent

Welcome to the lesson on **Testing**!

Today we will learn how to ensure our Agent system operates stably by writing automated tests. This is crucial as your project grows larger and more complex.

## 🎯 Today's Learning Objectives:
1. **Unit Testing**: Testing individual small functions in `tools.py`.
2. **Mocking**: Simulating external API calls (like LLM or web requests) so testing is cost/time efficient and can run even offline.
3. **Reasoning Loop Testing**: Ensuring the `AgentEngine` can handle tool-calling scenarios and protect itself from infinite loops.

## 🚀 How to Run Tests
1. Open terminal in the `day_26` directory.
2. Run the commands:
   ```bash
   pip install -r requirements.txt
   $env:PYTHONPATH="."; pytest -v tests/
   ```
   *(Note: `$env:PYTHONPATH="."` is used to help Python recognize files in the current directory).*

## 📂 Updated Directory Structure:
- **`tests/`**: Contains all test files.
  - **`test_tools.py`**: Tests for research tools.
  - **`test_engine.py`**: Tests for the Agent's reasoning core.
- **`tools.py`**: Updated to be more resilient, preventing errors if libraries like `duckduckgo-search` are missing.

## 💡 Why do we need Testing?
- **Avoid Regression**: When you modify code in `engine.py`, tests will immediately alert you if you accidentally break existing features.
- **Confidence in Refactoring**: You can restructure your source code freely knowing you have a "safety net" provided by the test suite.
- **Faster Development**: Instead of manually opening the UI and entering data each time you fix code, you can just run tests in 2 seconds.

**Try writing more test cases of your own!**
