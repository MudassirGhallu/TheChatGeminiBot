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

# ... (Keep your Styling and Sidebar code the same) ...

# 5. Integrated Input (Accepts ALL file types)
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
        # --- THE FIX STARTS HERE ---
        # 1. Check for IMAGE GENERATION first!
        image_triggers = ["draw", "generate", "make a picture", "paint", "image of"]
        
        if any(word in prompt.lower() for word in image_triggers):
            with st.spinner("🎨 TheGhalluBot is painting..."):
                # Use the clean prompt for Pollinations
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true&model=flux"
                st.image(img_url)
                
                # Download Button
                img_bytes = requests.get(img_url).content
                st.download_button("📥 Download Art", img_bytes, "ghallu_art.png", "image/png")
                st.session_state.messages.append({"role": "assistant", "content": f"![Generated Image]({img_url})"})

        # 2. Otherwise, handle UNIVERSAL FILE READING & CHAT
        else:
            context = ""
            if files:
                with st.spinner("Reading documents..."):
                    for f in files:
                        try:
                            # Use MarkItDown for universal conversion
                            file_text = process_universal_file(f)
                            context += f"\n\n--- DOCUMENT: {f.name} ---\n{file_text}"
                        except:
                            st.error(f"Could not read {f.name}")

            # Combine file text with prompt for Groq
            full_query = f"CONTEXT:\n{context}\n\nUSER QUESTION: {prompt}" if context else prompt

            if think_mode:
                with st.status("Analyzing...", expanded=False):
                    time.sleep(1)
                    st.write("Cross-referencing files...")

            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_query}]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
                messages=[{"role": "user", "content": full_query}]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
