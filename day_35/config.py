import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

# 📂 Directories & Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_CHAT_DIR = os.path.join(BASE_DIR, "faiss_chat_db")
CHAT_SESSIONS_DIR = os.path.join(BASE_DIR, "chat_sessions")

# Ensure necessary directories exist
os.makedirs(CHAT_SESSIONS_DIR, exist_ok=True)

# ⚙️ Chunking Parameters
DEFAULT_CHUNK_SIZE = 400
DEFAULT_CHUNK_OVERLAP = 50

# 🧠 Ollama Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5:14b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
