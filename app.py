import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Custom Page Styling
st.set_page_config(page_title="TheGhalluBot", page_icon="🔥", layout="centered")

st.markdown("""
    <style>
    .stChatMessage { background-color: #1e1e1e; border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    .stApp { background: linear-gradient(to right, #0f0c29, #302b63, #24243e); color: white; }
    h1 { color: #00d4ff; text-align: center; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 TheGhalluBot")

# 2. Sidebar with Features
with st.sidebar:
    st.header("⚙️ Bot Settings")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.write("📸 **Image Analysis**")
    uploaded_file = st.file_uploader("Upload an image to ask about it!", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Target Image", use_container_width=True)

# 3. Setup Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # 1.5 Flash is best for images

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat & Image Logic
if prompt := st.chat_input("Message TheGhalluBot..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if uploaded_file:
                # If there is an image, send it with the text
                img = Image.open(uploaded_file)
                response = model.generate_content([prompt, img])
            else:
                # Normal text chat
                response = model.generate_content(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
