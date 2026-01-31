import streamlit as st
from groq import Groq
import requests
import time
import PyPDF2
import io

# 1. Gemini Layout Styling
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
    
    /* Right-aligned User Messages */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse; text-align: right; margin-left: auto;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        background-color: #2b2c2f; padding: 12px 18px; border-radius: 22px; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="bot-header">TheGhalluBot</div>', unsafe_allow_html=True)

# 2. Sidebar (History removed, Settings kept)
with st.sidebar:
    st.title("Settings")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    think_mode = st.toggle("🧠 Deep Research Mode", value=False)
    st.info("Upload any PDF or Text file using the '+' icon in the chat bar!")

# 3. Helper: Extract Text from Files
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([page.extract_text() for page in reader.pages])
    elif uploaded_file.type == "text/plain":
        return str(uploaded_file.read(), "utf-8")
    return ""

# 4. Chat Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. The Magic Input (Link icon for PDFs, Images, and Txt)
chat_input = st.chat_input("Ask or upload a document...", accept_file="multiple")

if chat_input:
    prompt = chat_input.text
    files = chat_input.files
    
    # Process files if attached
    context = ""
    if files:
        for f in files:
            content = extract_text(f)
            if content:
                context += f"\n--- Content from {f.name} ---\n{content}\n"
    
    full_prompt = f"{context}\n\nUser Question: {prompt}" if context else prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if files:
            for f in files: st.caption(f"📎 Attached: {f.name}")

    with st.chat_message("assistant"):
        if think_mode:
            with st.status("Analyzing document data...", expanded=False):
                time.sleep(1)
                st.write("Extracting text...")
                time.sleep(1)

        # Logic for Image Gen vs Text
        if "draw" in prompt.lower():
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": f"![Image]({img_url})"})
        else:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
