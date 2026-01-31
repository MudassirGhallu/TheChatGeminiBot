import streamlit as st
from groq import Groq
import requests
import time

# 1. CSS for Gemini-Style Alignment & Sticky Header
st.set_page_config(page_title="TheGhalluBot", page_icon="🛸", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    
    /* Sticky Header for Bot Name */
    .bot-header { 
        position: sticky; top: 0; background: #131314; z-index: 1000; 
        padding: 15px; border-bottom: 1px solid #333; text-align: center;
        color: #8ab4f8; font-weight: bold; font-size: 24px;
    }

    /* Target User Messages to Right Side */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        text-align: right;
        margin-left: auto;
    }
    
    /* User Message Bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f;
        padding: 12px 18px;
        border-radius: 22px;
        display: inline-block;
        color: white;
    }

    /* Bot Message (No bubble, like Gemini) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
        background-color: transparent;
        padding: 10px 0;
    }

    /* Chat Input Styling */
    .stChatInputContainer { border-radius: 28px !important; border: 1px solid #5f6368 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header
st.markdown('<div class="bot-header">TheGhalluBot</div>', unsafe_allow_html=True)

# 3. Sidebar: Persistent History
if "conversations" not in st.session_state:
    st.session_state.conversations = ["Yesterday's Project", "Code Debugging", "New Idea"]

with st.sidebar:
    st.title("History")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    for chat_name in st.session_state.conversations:
        st.button(f"💬 {chat_name}", use_container_width=True)
    st.divider()
    think_mode = st.toggle("🧠 Think Longer", value=False)

# 4. Chat Logic & History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Integrated Input (Link Icon Included)
# Using accept_file=True enables the 'link' upload icon automatically
chat_input = st.chat_input("Ask TheGhalluBot...", accept_file=True, file_type=["png", "jpg", "jpeg"])

if chat_input:
    # Handle user text & files
    prompt = chat_input.text
    files = chat_input.files
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if files:
            st.image(files[0], width=250)

    # Bot Response
    with st.chat_message("assistant"):
        if think_mode:
            with st.status("Thinking like Gemini...", expanded=False):
                time.sleep(1.5)
                st.write("Reviewing chat context...")

        # Art or Text Logic
        if "draw" in prompt.lower() or "generate" in prompt.lower():
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": f"Image generated: {img_url}"})
        else:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            
            # Gemini Footer (Regenerate)
            if st.button("🔄 Regenerate"):
                st.rerun()
            
            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": res})
