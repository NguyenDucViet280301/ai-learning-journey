# 💬 Day 35: AI PDF Chatbot - Multi File Support

Welcome to the next level of chatbot development: **Day 35**!

In the previous project (Day 34), we built a conversational chatbot that can rephrase follow-up questions using history to query a single PDF file. However, in real-world applications, users need:
1. **To query across multiple different documents simultaneously.**
2. **Flexible document management** (adding new files, deleting specific files from the Vector DB without re-indexing everything from scratch).
3. **Multiple independent chat sessions** (similar to ChatGPT or Claude) to view history or resume a past conversation.

In this project, we implement all of these advanced features!

---

## 🎯 Key Features of Day 35:
1. **Multi-File Support (Multi-Document Management):**
   - Supports appending multiple PDF files into a single FAISS Vector DB index.
   - Scans the FAISS metadata directly to list all currently stored documents in the sidebar.
   - **Specific File Deletion**: Dynamically filters and deletes all vector chunks belonging to a chosen file from the FAISS index without affecting other documents.
2. **Persistent Chat Sessions:**
   - Automatically saves and loads chat conversations in a local `chat_sessions/` directory in JSON format.
   - Manage sessions directly from the sidebar: add a new session, rename the current session, or delete old sessions.
   - Retains conversation history even after browser refresh (F5).
3. **Advanced Retrieval Options:**
   - Toggle search strategies between standard **Similarity Search** and **MMR (Maximal Marginal Relevance)** to diversify results.
   - Dynamically calls the local Ollama API (`/api/tags`) to populate the model selectbox with downloaded models on your machine.
   - Customize Temperature and Top K parameters directly in the UI.
4. **Premium UI/UX:**
   - Injects custom CSS (`style.css`) to use modern typography (Outfit), custom glassmorphism styling, and sleek chat bubbles.
   - Displays sources beautifully inside responsive cards with hover effects and monospace text blocks.

---

## 📂 Project Structure:
* **`config.py`**: Configuration parameters including paths for FAISS index, chat sessions, and default chunk settings.
* **`chatbot_engine.py`**: The core `ChatbotEngine` class handling RAG pipelines, now with MMR retrieval, specific file deletion, and local Ollama model scanning.
* **`session_manager.py`**: Handles JSON file CRUD operations for persistent conversation history.
* **`style.css`**: Custom CSS stylesheet for enhanced UI design.
* **`main.py`**: The Streamlit frontend linking all components together.
* **`requirements.txt`**: Project dependencies including the additional `requests` library.

---

## 🚀 How to Run:
1. Open your terminal in the project directory `day_35` and install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Make sure **Ollama** is running locally:
   ```bash
   ollama list
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. On the UI:
   - **Sidebar**:
     - Create a few chats with the **New Conversation** button. You will see JSON files created in the `chat_sessions/` folder.
     - Upload a PDF and click **🚀 Index Document (Append PDF)**. Repeat to index multiple files.
     - Test deleting files from the database and watch the indexed files and chunk metrics update.
   - **Main Panel**:
     - Chat with the assistant. Click the expander at the bottom of any response to check standalone queries and sources.

*Enjoy coding your professional AI PDF Chatbot with Day 35!*
