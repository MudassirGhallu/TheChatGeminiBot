import streamlit as st
import os
import requests
import time
from PIL import Image
from groq import Groq
from markitdown import MarkItDown

# --- 1. ICON & PAGE SETUP ---
# This looks for the image in the same folder as your app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, "1.png")

try:
    bot_icon = Image.open(icon_path)
except Exception:
    # Fallback to emoji if the file isn't found
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
    .bot-header { 
        position: sticky; top: 0; background: #131314; z-index: 1000; 
        padding: 15px; border-bottom: 1px solid #333; text-align: center;
        color: #8ab4f8; font-weight: bold; font-size: 24px;
    }
    [data-testid="stSidebar"] { background-color: #1e1f20; }
    
    /* User Message: Right Aligned with Bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse; text-align: right; margin-left: auto;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f; padding: 12px 18px; border-radius: 22px; display: inline-block;
    }
    
    /* Bot Message: Left Aligned, No Bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
        background-color: transparent; padding: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="bot-header">TheGhalluBot</div>', unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    # If the icon loaded, show it at the top of the sidebar too
    if not isinstance(bot_icon, str):
        st.image(bot_icon, width=100)
    else:
        st.error("1.png not found in root directory!")
        
    st.title("Settings")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    think_mode = st.toggle("🧠 Deep Research Mode", value=False)
    st.caption("Supports: PDF, DOCX, PPTX, XLSX, TXT, & Images")

# --- 4. CORE LOGIC ---
md_converter = MarkItDown()

def process_universal_file(uploaded_file):
    try:
        result = md_converter.convert(uploaded_file)
        return result.text_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. CHAT INPUT ---
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
        # PRIORITY 1: Image Generation
        image_triggers = ["draw", "generate", "make a picture", "paint", "image of"]
        
        if any(word in prompt.lower() for word in image_triggers):
            with st.spinner("🎨 TheGhalluBot is painting..."):
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true&model=flux"
                st.image(img_url)
                
                img_bytes = requests.get(img_url).content
                st.download_button("📥 Download Art", img_bytes, "Generated_by_Ghallu.png", "image/png")
                st.session_state.messages.append({"role": "assistant", "content": f"![Generated Image]({img_url})"})

        # PRIORITY 2: Document/Text Analysis
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
            
            # History + Current Prompt
            messages_to_send = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            messages_to_send.append({"role": "user", "content": full_query})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_to_send
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
