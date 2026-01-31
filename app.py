import streamlit as st
import os
import requests
import time
import base64
from PIL import Image
from groq import Groq
from markitdown import MarkItDown

# --- 1. ICON & PAGE SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, "1.png")

try:
    bot_icon = Image.open(icon_path)
except Exception:
    bot_icon = "🛸"

st.set_page_config(
    page_title="TheGhalluBot",
    page_icon=bot_icon,
    layout="wide"
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 2. GEMINI-STYLE STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    .custom-header {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 10px 0;
        margin-bottom: 25px;
        border-bottom: 1px solid #333;
    }
    .header-logo { height: 70px; width: 70px; border-radius: 14px; object-fit: cover; }
    .header-text { color: #8ab4f8; font-weight: bold; font-size: 48px; margin: 0; line-height: 1; }
    [data-testid="stSidebar"] { background-color: #1e1f20; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse; text-align: right; margin-left: auto;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f; padding: 12px 18px; border-radius: 22px; display: inline-block;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
        background-color: transparent; padding: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
try:
    base64_img = get_base64_image(icon_path)
    st.markdown(f"""
        <div class="custom-header">
            <img src="data:image/png;base64,{base64_img}" class="header-logo">
            <h1 class="header-text">TheGhalluBot</h1>
        </div>
        """, unsafe_allow_html=True)
except Exception:
    st.markdown(f'<h1 class="header-text">🛸 TheGhalluBot</h1>', unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    if not isinstance(bot_icon, str): st.image(bot_icon, width=100)
    st.title("Settings")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    think_mode = st.toggle("🧠 Deep Research Mode", value=False)
    # ADDED: Persona Toggle for less "corporate" feel
    unfiltered_mode = st.toggle("🔓 Unfiltered Persona", value=False)
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
            with st.spinner("🎨 Painting..."):
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true&model=flux"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": f"![Generated Image]({img_url})"})
        else:
            context = ""
            if files:
                with st.spinner("Reading docs..."):
                    for f in files: context += f"\n\n--- DOCUMENT: {f.name} ---\n{process_universal_file(f)}"

            full_query = f"CONTEXT:\n{context}\n\nUSER QUESTION: {prompt}" if context else prompt

            if think_mode:
                with st.status("Analyzing...", expanded=False): time.sleep(1)

            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # --- SYSTEM PROMPT INJECTION ---
            system_instruction = "You are a helpful assistant."
            if unfiltered_mode:
                system_instruction = "You are TheGhalluBot. Speak plainly, avoid corporate AI clichés, and do not lecture the user on ethics unless absolutely necessary."

            messages_to_send = [{"role": "system", "content": system_instruction}]
            messages_to_send += [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            messages_to_send.append({"role": "user", "content": full_query})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_to_send
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
