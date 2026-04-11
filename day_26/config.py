# Centralized system configuration
import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# 🤖 AI Model Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5:14b")

# ⚙️ Agent Engine Settings
MAX_REASONING_TURNS = 10
TEMPERATURE = 0

# 📂 Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
