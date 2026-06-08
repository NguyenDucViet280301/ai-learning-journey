import os
import json
import time
from config import CHAT_SESSIONS_DIR

class ChatSessionManager:
    """Manages persistent chat sessions stored as JSON files on disk."""

    @staticmethod
    def _get_filepath(session_id: str) -> str:
        return os.path.join(CHAT_SESSIONS_DIR, f"{session_id}.json")

    @staticmethod
    def list_sessions() -> list[dict]:
        """Lists all saved sessions sorted by updated time (newest first)."""
        if not os.path.exists(CHAT_SESSIONS_DIR):
            return []
        
        sessions = []
        for filename in os.listdir(CHAT_SESSIONS_DIR):
            if filename.endswith(".json"):
                session_id = filename[:-5]
                filepath = os.path.join(CHAT_SESSIONS_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append({
                            "session_id": session_id,
                            "title": data.get("title", "New Conversation"),
                            "updated_at": data.get("updated_at", os.path.getmtime(filepath))
                        })
                except Exception as e:
                    print(f"Error reading session file {filename}: {e}")
                    
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions

    @staticmethod
    def load_session(session_id: str) -> dict | None:
        """Loads a session's details by session_id."""
        filepath = ChatSessionManager._get_filepath(session_id)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    @staticmethod
    def save_session(session_id: str, title: str, messages: list, chat_history: list) -> bool:
        """Saves or updates a chat session on disk."""
        filepath = ChatSessionManager._get_filepath(session_id)
        data = {
            "session_id": session_id,
            "title": title,
            "messages": messages,
            "chat_history": chat_history,
            "updated_at": time.time()
        }
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return False

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Deletes a chat session file."""
        filepath = ChatSessionManager._get_filepath(session_id)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"Error deleting session {session_id}: {e}")
        return False
