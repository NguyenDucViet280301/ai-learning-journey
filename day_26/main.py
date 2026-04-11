import streamlit as st
import os
import sys
import glob
from langchain_core.messages import HumanMessage, AIMessage
from agent import get_agent

st.set_page_config(page_title="Day 26 - Testing Agent", page_icon="🧪", layout="wide")

st.title("🧪 Day 26 - Testing AI Agent Engine")
st.markdown("""
In version **Day 26**, we focus on **Testing**:
- **Unit Testing:** Testing individual tools in `tools.py`.
- **Mocking:** Simulating external APIs for fast and reliable testing.
- **Fail-safe Logic:** Updated code to protect against network errors or missing libraries.
""")

st.divider()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "agent_instance" not in st.session_state:
    st.session_state.agent_instance = get_agent()
    
with st.sidebar:
    st.header("⚙️ Settings (Refactored)")
    if st.button("♻️ Reset Session"):
        st.session_state.chat_history = []
        st.session_state.agent_instance = get_agent()
        st.success("Old memories cleared!")
        
    st.divider()
    st.subheader("📚 Documents Repository")
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    if os.path.exists(output_dir):
        files = glob.glob(os.path.join(output_dir, "*.md"))
        files.sort(key=os.path.getmtime, reverse=True) 
        for file_path in files[:5]:
            file_name = os.path.basename(file_path)
            with st.expander(f"📄 {file_name}"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    st.markdown(content)
                st.download_button("📥 Download", data=content, file_name=file_name, mime="text/markdown", key=file_name)

chat_container = st.container(height=500)

with chat_container:
    for msg in st.session_state.chat_history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.write(msg.content)

if prompt := st.chat_input("Assign a complex task..."):
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)
            st.session_state.chat_history.append(HumanMessage(content=prompt))
            
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("🏗️ Refactored Agent Engine is thinking..."):
                try:
                    response = st.session_state.agent_instance.run(prompt, chat_history=st.session_state.chat_history[:-1])
                    st.write(response)
                    st.session_state.chat_history.append(AIMessage(content=response))
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    import subprocess
    if os.environ.get("STREAMLIT_RUNNING") != "true":
        env = os.environ.copy()
        env["STREAMLIT_RUNNING"] = "true"
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__], env=env)
        sys.exit(0)
