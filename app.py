import streamlit as st
import os
import requests
import time
from PIL import Image
from groq import Groq
from markitdown import MarkItDown

# --- 1. ICON & PAGE SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, "1.png") # Updated to your new filename

try:
    bot_icon = Image.open(icon_path)
except Exception:
    bot_icon = "🛸"

st.set_page_config(
    page_title="TheGhalluBot",
    page_icon=bot_icon,
    layout="wide"
)

# --- 2. GEMINI-STYLE STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    
    /* Header Styling with Logo on Left */
    .header-container {
        position: sticky;
        top: 0;
        background: #131314;
        z-index: 1000;
        padding: 20px 30px;
        border-bottom: 1px solid #333;
        display: flex;
        align-items: center;
        gap: 15px; /* Space between logo and text */
    }
    .header-logo {
        height: 40px; /* Adjust size as needed */
        width: auto;
    }
    .header-text {
        color: #8ab4f8;
        font-weight: bold;
        font-size: 32px; /* Increased Font Size */
        font-family: 'Google Sans', Arial, sans-serif;
    }

    [data-testid="stSidebar"] { background-color: #1e1f20; }
    
    /* User Message: Right Aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse; text-align: right; margin-left: auto;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f; padding: 12px 18px; border-radius: 22px; display: inline-block;
    }
    
    /* Bot Message: Left Aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
        background-color: transparent; padding: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CUSTOM HEADER INJECTION ---
# This creates the (Logo + TheGhalluBot) layout
header_html = f"""
    <div class="header-container">
        <img src="data:image/png;base64,{requests.utils.quote('')}" class="header-logo" id="bot-logo">
        <span class="header-text">TheGhalluBot</span>
    </div>
"""
# Since we can't easily pass local bytes to raw HTML src, we use a cleaner Streamlit column approach
col1, col2 = st.columns([0.05, 0.95])
with col1:
    st.image(bot_icon, width=50)
with col2:
    st.markdown(f'<h1 style="color: #8ab4f8; margin-top: -10px;">TheGhalluBot</h1>', unsafe_allow_html=True)
st.divider()

# --- 4. SIDEBAR ---
with st.sidebar:
    if not isinstance(bot_icon, str):
        st.image(bot_icon, width=80)
    else:
        st.error("1.png not found!")
        
    st.title("Settings")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    think_mode = st.toggle("🧠 Deep Research Mode", value=False)
    st.caption("Supports: PDF, DOCX, PPTX, XLSX, TXT, & Images")

# --- 5. CORE LOGIC ---
md_converter = MarkItDown()

def process_universal_file(uploaded_file):
    try:
        result = md_converter.convert(uploaded_file)
        return result.text_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. CHAT INPUT ---
chat_input = st.chat_input("Ask, Draw, or Upload...", accept_file="multiple")

if chat_input:
    prompt = chat_input.text
    files = chat_input.files
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if files:
            for f in files: st.caption(f"📁 Attached: {f.name}")

    with st.chat_message("assistant"):
        image_triggers = ["draw", "generate", "make a picture", "paint", "image of"]
        
        if any(word in prompt.lower() for word in image_triggers):
            with st.spinner("🎨 TheGhalluBot is painting..."):
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true&model=flux"
                st.image(img_url)
                
                img_bytes = requests.get(img_url).content
                st.download_button("📥 Download Art", img_bytes, "ghallu_art.png", "image/png")
                st.session_state.messages.append({"role": "assistant", "content": f"![Generated Image]({img_url})"})

        else:
            context = ""
            if files:
                with st.spinner("Reading documents..."):
                    for f in files:
                        file_text = process_universal_file(f)
                        context += f"\n\n--- DOCUMENT: {f.name} ---\n{file_text}"

            full_query = f"CONTEXT:\n{context}\n\nUSER QUESTION: {prompt}" if context else prompt

            if think_mode:
                with st.status("Analyzing...", expanded=False):
                    time.sleep(1)
                    st.write("Cross-referencing data...")

            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            messages_to_send = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            messages_to_send.append({"role": "user", "content": full_query})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_to_send
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
