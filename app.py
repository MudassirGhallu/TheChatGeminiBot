import streamlit as st
from groq import Groq
import requests
import time

# 1. Gemini Layout & Styling
st.set_page_config(page_title="TheGhalluBot", page_icon="🛸", layout="wide")

st.markdown("""
    <style>
    /* Dark Theme Background */
    .stApp { background-color: #131314; color: #e3e3e3; font-family: 'Google Sans', Arial, sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #1e1f20; border-right: 1px solid #333; }
    
    /* Message Container Logic */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    
    /* User Message: Right Aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        text-align: right;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f;
        padding: 10px 15px;
        border-radius: 20px;
        display: inline-block;
        max-width: 80%;
    }

    /* Bot Message: Left Aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
        background-color: transparent;
        padding: 10px 0;
        max-width: 90%;
    }
    
    /* Floating Chat Input */
    .stChatInputContainer { background-color: #1e1f20 !important; border-radius: 30px !important; border: 1px solid #3c4043 !important; }

    /* Sticky Header for Bot Name */
    .bot-header { position: sticky; top: 0; background: #131314; z-index: 999; padding: 10px; border-bottom: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header and Sidebar
st.markdown('<div class="bot-header"><h2>🛸 TheGhalluBot</h2></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("Ghallu History")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.toggle("🧠 Deep Research Mode", key="think_mode")

# 3. Setup Clients
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Gemini Chat Logic
chat_data = st.chat_input("Ask TheGhalluBot...", accept_file=True, file_type=["png", "jpg", "jpeg"])

if chat_data:
    prompt = chat_data.text
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot Response
    with st.chat_message("assistant"):
        # Optional Thinking Log
        if st.session_state.think_mode:
            with st.status("Thinking...", expanded=False):
                time.sleep(1)
                st.write("Processing context...")

        # Art or Text
        if "draw" in prompt.lower():
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true"
            st.image(img_url)
            # Regenerate / Download logic
            st.download_button("📥 Download", requests.get(img_url).content, "art.png")
        else:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            # Gemini style footer for assistant
            col1, col2 = st.columns([1, 8])
            with col1:
                st.button("🔄", help="Regenerate", on_click=lambda: None) # Simple refresh placeholder
            st.session_state.messages.append({"role": "assistant", "content": res})
