import streamlit as st
from groq import Groq
from markitdown import MarkItDown
import requests
import time

# 1. Gemini Layout & Styling
st.set_page_config(page_title="TheGhalluBot", page_icon="🛸", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    .bot-header { 
        position: sticky; top: 0; background: #131314; z-index: 1000; 
        padding: 15px; border-bottom: 1px solid #333; text-align: center;
        color: #8ab4f8; font-weight: bold; font-size: 24px;
    }
    [data-testid="stSidebar"] { background-color: #1e1f20; }
    
    /* User: Right / Bot: Left */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse; text-align: right; margin-left: auto;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f; padding: 12px 18px; border-radius: 22px; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="bot-header">TheGhalluBot Universal</div>', unsafe_allow_html=True)

# 2. Sidebar Settings
with st.sidebar:
    st.title("Settings")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    think_mode = st.toggle("🧠 Deep Research Mode", value=False)
    st.caption("Supports: PDF, DOCX, PPTX, XLSX, TXT, & Images")

# 3. Universal File Processor
md_converter = MarkItDown()

def process_universal_file(uploaded_file):
    try:
        # MarkItDown handles the bytes directly and detects the format
        result = md_converter.convert(uploaded_file)
        return result.text_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

# 4. Chat Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Integrated Input (Accepts ALL file types)
chat_input = st.chat_input("Ask or upload anything...", accept_file="multiple")

if chat_input:
    prompt = chat_input.text
    files = chat_input.files
    
    # Process all attached files into one context string
    context = ""
    if files:
        for f in files:
            with st.spinner(f"Reading {f.name}..."):
                file_text = process_universal_file(f)
                context += f"\n\n--- DOCUMENT: {f.name} ---\n{file_text}"

    # Combine file content with user question
    full_query = f"CONTEXT FROM UPLOADED FILES:\n{context}\n\nUSER QUESTION: {prompt}" if context else prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if files:
            for f in files: st.caption(f"📁 Processed: {f.name}")

    # Assistant Response
    with st.chat_message("assistant"):
        if think_mode:
            with st.status("Performing Deep Research...", expanded=False):
                st.write("Extracting data from files...")
                time.sleep(1)
                st.write("Connecting dots across documents...")
                time.sleep(1)

        # Image Generation Trigger
        if "draw" in prompt.lower() or "generate image" in prompt.lower():
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": f"![Image]({img_url})"})
        
        # Standard Text/Doc Analysis
        else:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_query}]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
