import streamlit as st
import os
import sys
import time
import shutil

# Add the current folder to python path to avoid import errors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from config import OLLAMA_BASE_URL, DEFAULT_MODEL, EMBEDDING_MODEL, FAISS_CHAT_DIR, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from chatbot_engine import ChatbotEngine
from session_manager import ChatSessionManager

# Page Configuration
st.set_page_config(
    page_title="Day 35 - AI PDF Chatbot - Multi File Support", 
    page_icon="💬", 
    layout="wide"
)

# Load and inject custom CSS
css_path = os.path.join(BASE_DIR, "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# ----------------- SESSION STATE INITIALIZATION -----------------
# 1. Manage sessions list
sessions = ChatSessionManager.list_sessions()

# 2. Pick active session
if "active_session_id" not in st.session_state or not st.session_state.active_session_id:
    if sessions:
        st.session_state.active_session_id = sessions[0]["session_id"]
    else:
        # Create default first session
        first_id = str(int(time.time()))
        ChatSessionManager.save_session(first_id, "New Conversation", [], [])
        st.session_state.active_session_id = first_id
        sessions = ChatSessionManager.list_sessions()

# 3. Load active session data
active_session = ChatSessionManager.load_session(st.session_state.active_session_id)
if active_session is None:
    # If loaded session is missing, recreate it
    first_id = str(int(time.time()))
    ChatSessionManager.save_session(first_id, "New Conversation", [], [])
    st.session_state.active_session_id = first_id
    active_session = ChatSessionManager.load_session(first_id)

st.session_state.messages = active_session.get("messages", [])
st.session_state.chat_history = active_session.get("chat_history", [])
st.session_state.session_title = active_session.get("title", "New Conversation")

# 4. Check Vector DB Status
doc_count = ChatbotEngine.get_document_count()
indexed_files = ChatbotEngine.get_indexed_files()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">💬 Conversations</div>', unsafe_allow_html=True)
    
    # Button to create a new session
    if st.button("➕ New Conversation", use_container_width=True):
        new_id = str(int(time.time()))
        ChatSessionManager.save_session(new_id, "New Conversation", [], [])
        st.session_state.active_session_id = new_id
        st.toast("New conversation created!")
        st.rerun()
        
    # Render sessions list with active highlighting and delete buttons
    st.markdown("<p style='font-size:13px; color:#888; margin-bottom:5px;'>Saved chats:</p>", unsafe_allow_html=True)
    for s in sessions:
        col_btn, col_del = st.columns([4, 1])
        with col_btn:
            is_active = (s["session_id"] == st.session_state.active_session_id)
            if st.button(
                s["title"], 
                key=f"session_btn_{s['session_id']}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active_session_id = s["session_id"]
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"session_del_{s['session_id']}", help="Delete conversation"):
                ChatSessionManager.delete_session(s["session_id"])
                if s["session_id"] == st.session_state.active_session_id:
                    st.session_state.active_session_id = None
                st.toast("Conversation deleted!")
                st.rerun()
                
    st.divider()
    
    # Rename Active Session
    st.markdown("<p style='font-size:13px; color:#888; margin-bottom:2px;'>Rename current chat:</p>", unsafe_allow_html=True)
    new_title = st.text_input("Title Input", value=st.session_state.session_title, label_visibility="collapsed")
    if new_title != st.session_state.session_title and new_title.strip() != "":
        ChatSessionManager.save_session(
            st.session_state.active_session_id,
            new_title.strip(),
            st.session_state.messages,
            st.session_state.chat_history
        )
        st.session_state.session_title = new_title.strip()
        st.rerun()
        
    st.divider()
    st.markdown('<div class="sidebar-header">📂 Document Management</div>', unsafe_allow_html=True)
    
    # Upload and append PDF
    uploaded_file = st.file_uploader("Upload PDF document:", type=["pdf"])
    
    col_chunk_sz, col_overlap = st.columns(2)
    with col_chunk_sz:
        chunk_size = st.slider("Chunk Size:", min_value=100, max_value=1000, value=DEFAULT_CHUNK_SIZE, step=50)
    with col_overlap:
        chunk_overlap = st.slider("Overlap:", min_value=10, max_value=200, value=DEFAULT_CHUNK_OVERLAP, step=10)
        
    if st.button("🚀 Index Document (Append PDF)", use_container_width=True):
        if uploaded_file is None:
            st.error("Please upload a PDF file first.")
        else:
            with st.spinner("Processing and splitting document..."):
                try:
                    file_bytes = uploaded_file.read()
                    filename = uploaded_file.name
                    
                    chunks_created = ChatbotEngine.process_pdf(
                        file_bytes=file_bytes,
                        filename=filename,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                    st.success(f"Successfully indexed '{filename}'! (+{chunks_created} chunks)")
                    st.rerun()
                except ConnectionError as ce:
                    st.error(str(ce))
                    st.warning("👉 Make sure Ollama is running locally.")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    # Display indexed files list
    st.markdown("<p style='font-size:13px; color:#888; margin-bottom:5px;'>Indexed documents:</p>", unsafe_allow_html=True)
    if not indexed_files:
        st.info("No documents in the vector database.")
    else:
        for f_name in indexed_files:
            # Render a custom styled file card inside streamlit
            st.markdown(f"""
            <div class="file-card">
                <div class="file-name" title="{f_name}">{f_name}</div>
            </div>
            """, unsafe_allow_html=True)
            col_space, col_action = st.columns([3, 1])
            with col_action:
                if st.button("Delete 🗑️", key=f"del_file_{f_name}", use_container_width=True):
                    if ChatbotEngine.delete_file(f_name):
                        st.toast(f"Deleted document '{f_name}'!")
                        st.rerun()

    st.divider()
    st.markdown('<div class="sidebar-header">⚙️ RAG & LLM Configuration</div>', unsafe_allow_html=True)
    
    with st.expander("Parameters Tuning", expanded=False):
        # Dynamic model selection
        local_models = ChatbotEngine.get_local_ollama_models()
        default_idx = local_models.index(DEFAULT_MODEL) if DEFAULT_MODEL in local_models else 0
        selected_model = st.selectbox("LLM Model:", options=local_models, index=default_idx)
        
        temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
        top_k = st.slider("Context Count (Top K):", min_value=1, max_value=10, value=3, step=1)
        
        search_strategy = st.radio("Retrieval Strategy:", options=["similarity", "mmr"], format_func=lambda x: "Similarity Search" if x == "similarity" else "MMR (Diversified)")
        
        fetch_k = 20
        lambda_mult = 0.5
        if search_strategy == "mmr":
            fetch_k = st.slider("MMR Fetch K:", min_value=5, max_value=50, value=20, step=5)
            lambda_mult = st.slider("MMR Lambda (Diversity):", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
            
    # System summary status
    st.info(f"📊 System: **{doc_count}** chunks from **{len(indexed_files)}** documents.")
    
    # Global Reset Button
    if st.button("🗑️ Clear Database (Reset DB)", use_container_width=True, type="secondary"):
        if os.path.exists(FAISS_CHAT_DIR):
            shutil.rmtree(FAISS_CHAT_DIR)
        st.toast("Database cleared successfully!")
        st.rerun()

# ----------------- MAIN SCREEN -----------------
# Header title
st.markdown(f'<h1 class="gradient-text">💬 Day 35 - AI PDF Chatbot - {st.session_state.session_title}</h1>', unsafe_allow_html=True)
st.write("Conversational AI assistant supporting multiple PDF documents with persistent session history.")
st.divider()

if doc_count == 0:
    st.warning("⚠️ The database is currently empty. Please upload PDF files and click **🚀 Index Document (Append PDF)** in the left sidebar to start chatting.")
else:
    # 1. Render message history
    if not st.session_state.messages:
        # Show a beautiful welcome grid when chat is empty
        st.markdown(f"""
        <div class="welcome-card">
            <div class="welcome-title">👋 Welcome to RAG Chatbot!</div>
            <div class="welcome-text">
                I have indexed <b>{len(indexed_files)} documents</b> ({doc_count} semantic chunks). 
                You can ask me any questions about them. Here are some conversation tips:
                <ul style="margin-top: 10px; padding-left: 20px;">
                    <li>Ask detailed questions about the core content of your documents.</li>
                    <li>Feel free to use follow-up questions (the assistant automatically resolves context and pronouns).</li>
                    <li>Check the "Sources & Context Analysis" section below any response to verify source information.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Render source citation card if assistant response
                if msg["role"] == "assistant" and msg.get("sources"):
                    with st.expander("📍 Sources & Context Analysis"):
                        st.write(f"🔍 **Standalone Query:** `{msg.get('standalone_query')}`")
                        st.divider()
                        
                        # Build source cards HTML
                        sources_html = ""
                        for src in msg.get("sources", []):
                            sources_html += f"""
                            <div class="source-card">
                                <div class="source-header">
                                    <span>Chunk #{src['index']} - Source: {src['source']}</span>
                                    <span>Page {src['page']}</span>
                                </div>
                                <div class="source-body">{src['text']}</div>
                            </div>
                            """
                        st.markdown(sources_html, unsafe_allow_html=True)
                        
    # 2. Handle new user input
    if prompt := st.chat_input("Ask anything about your documents..."):
        # Append User message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Save session immediately to update UI in case of errors
        # Auto rename conversation title if it was default
        current_title = st.session_state.session_title
        if current_title == "New Conversation" and len(prompt.strip()) > 0:
            current_title = prompt.strip()[:30] + ("..." if len(prompt.strip()) > 30 else "")
            st.session_state.session_title = current_title
            
        ChatSessionManager.save_session(
            st.session_state.active_session_id,
            current_title,
            st.session_state.messages,
            st.session_state.chat_history
        )
        
        # Call RAG logic
        with st.chat_message("assistant"):
            with st.spinner("Analyzing documents and writing response..."):
                try:
                    result = ChatbotEngine.conversational_rag(
                        query=prompt,
                        chat_history=st.session_state.chat_history,
                        model_name=selected_model,
                        temperature=temperature,
                        top_k=top_k,
                        search_strategy=search_strategy,
                        fetch_k=fetch_k,
                        lambda_mult=lambda_mult
                    )
                    
                    st.markdown(result["answer"])
                    
                    if result["sources"]:
                        with st.expander("📍 Sources & Context Analysis"):
                            st.write(f"🔍 **Standalone Query:** `{result['standalone_query']}`")
                            st.divider()
                            
                            sources_html = ""
                            for src in result["sources"]:
                                sources_html += f"""
                                <div class="source-card">
                                    <div class="source-header">
                                        <span>Chunk #{src['index']} - Source: {src['source']}</span>
                                        <span>Page {src['page']}</span>
                                    </div>
                                    <div class="source-body">{src['text']}</div>
                                </div>
                                """
                            st.markdown(sources_html, unsafe_allow_html=True)
                            
                    # Save assistant response
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                        "standalone_query": result["standalone_query"]
                    })
                    
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
                    
                    # Persist session state
                    ChatSessionManager.save_session(
                        st.session_state.active_session_id,
                        st.session_state.session_title,
                        st.session_state.messages,
                        st.session_state.chat_history
                    )
                    
                    st.rerun()
                    
                except ConnectionError as ce:
                    st.error(str(ce))
                    st.warning("👉 Make sure Ollama is running and the model is pulled.")
                except Exception as e:
                    st.error(f"System error: {e}")

# --- Streamlit auto-launcher block ---
if __name__ == "__main__":
    import subprocess
    if os.environ.get("STREAMLIT_RUNNING") != "true":
        env = os.environ.copy()
        env["STREAMLIT_RUNNING"] = "true"
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__], env=env)
        sys.exit(0)
