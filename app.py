import streamlit as st
from groq import Groq
import requests
import time
import io

# 1. Custom Styling for v3.0
st.set_page_config(page_title="TheGhalluBot", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050505; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #333; }
    .stChatInputContainer { padding-bottom: 20px; }
    .thinking-log { background: #1a1a1a; border-left: 3px solid #7000ff; padding: 10px; font-style: italic; color: #aaa; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Chat History
with st.sidebar:
    st.title("🛸 TheGhalluBot")
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.write("📜 **Recent Conversations**")
    # This simulates history entries
    if "history_list" not in st.session_state: st.session_state.history_list = ["Project Alpha", "Image Gen Test"]
    for chat in st.session_state.history_list:
        st.button(f"💬 {chat}", key=chat, use_container_width=True)

# 3. Setup Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
POL_API_KEY = st.secrets["POLLINATIONS_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Integrated Chat Input with Upload ("Link" icon enabled)
user_input = st.chat_input("Ask or Draw something...", accept_file=True, file_type=["png", "jpg", "jpeg"])

if user_input:
    prompt = user_input.text
    files = user_input.files # Attached images
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if files: st.info(f"📎 Attached: {files[0].name}")

    with st.chat_message("assistant"):
        # DEEP RESEARCH FEATURE: Thinking Log
        with st.expander("🧠 Thinking Process...", expanded=True):
            log_placeholder = st.empty()
            log_placeholder.markdown("🔍 Analyzing prompt...")
            time.sleep(1)
            log_placeholder.markdown("🔍 Checking for image generation triggers...")
            time.sleep(1)
            log_placeholder.markdown("🔍 Synthesizing final response...")

        # ART LOGIC
        if "draw" in prompt.lower() or "generate" in prompt.lower():
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true&model=flux"
            st.image(img_url)
            
            # DOWNLOAD BUTTON
            img_data = requests.get(img_url).content
            st.download_button(label="📥 Download Image", data=img_data, file_name="ghallu_art.png", mime="image/png")
            st.session_state.messages.append({"role": "assistant", "content": f"Generated image: {img_url}"})
        
        # TEXT LOGIC
        else:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
