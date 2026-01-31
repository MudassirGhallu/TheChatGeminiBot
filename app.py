import streamlit as st
from groq import Groq
import requests
import time

# 1. Advanced Styling & Layout
st.set_page_config(page_title="TheGhalluBot", page_icon="🛸", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050505; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #0f0f11; border-right: 1px solid #222; }
    .stChatInputContainer { border-top: 1px solid #333; }
    .thought-bubble { background: #1a1a2e; border-left: 4px solid #00f2ff; padding: 12px; font-size: 0.9em; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Gemini-Style Chat History
with st.sidebar:
    st.title("🛸 TheGhalluBot")
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    # Deep Research Toggle
    think_mode = st.toggle("🧠 Deep Research Mode", value=False, help="When on, the bot logs its thinking steps.")
    
    st.divider()
    st.subheader("📜 Recent Chats")
    # Simulated History
    history = ["Design Ideas", "Logic Puzzle", "Flux Art Gen"]
    for chat in history:
        st.button(f"💬 {chat}", use_container_width=True, key=f"hist_{chat}")

# 3. Setup Clients
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
POL_API_KEY = st.secrets["POLLINATIONS_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Integrated Input (Link icon + Text)
# accept_file=True adds the paperclip/link icon inside the input bar
chat_data = st.chat_input("Ask or Draw...", accept_file=True, file_type=["png", "jpg", "jpeg"])

if chat_data:
    prompt = chat_data.text
    files = chat_data.files
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if files:
            st.image(files[0], caption="Attached Image", width=300)

    with st.chat_message("assistant"):
        # Optional Thinking Log
        if think_mode:
            with st.status("🔍 TheGhalluBot is analyzing...", expanded=True) as status:
                st.write("Step 1: Parsing user intent...")
                time.sleep(0.8)
                st.write("Step 2: Searching knowledge base...")
                time.sleep(0.8)
                st.write("Step 3: Generating final response.")
                status.update(label="✅ Analysis Complete", state="complete")

        # ART TRIGGER
        if any(word in prompt.lower() for word in ["draw", "generate", "image"]):
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true&model=flux"
            st.image(img_url)
            
            # 📥 Download Button
            img_bytes = requests.get(img_url).content
            st.download_button(label="📥 Download Art", data=img_bytes, file_name="ghallu_bot_art.png", mime="image/png")
            st.session_state.messages.append({"role": "assistant", "content": f"Image generated: {img_url}"})
        
        # CHAT TRIGGER
        else:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            bot_res = completion.choices[0].message.content
            st.markdown(bot_res)
            st.session_state.messages.append({"role": "assistant", "content": bot_res})
