import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

# 1. Page Styling (Cyberpunk Theme)
st.set_page_config(page_title="TheGhalluBot", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background: #0E1117; color: #00FFA3; }
    .stChatMessage { border: 1px solid #00FFA3; border-radius: 10px; background: #161B22; }
    h1 { text-shadow: 2px 2px #FF007A; font-family: 'Orbitron', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ TheGhalluBot ⚡")

# 2. Setup Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
# Use a Vision-capable model
MODEL_NAME = "llama-3.2-11b-vision-preview" 

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Image Upload
with st.sidebar:
    st.header("📸 Vision Mode")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. Encoding Logic for Images
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# 4. Chat Logic
if prompt := st.chat_input("Ask TheGhalluBot..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Prepare content list for Groq's multimodal API
            content = [{"type": "text", "text": prompt}]
            
            if uploaded_file:
                base64_image = encode_image(uploaded_file)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })

            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": content}],
            )
            
            response_text = completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"Groq Error: {e}")
