import streamlit as st
from groq import Groq
import requests
import time

# 1. Cyber-Ghallu Styling
st.set_page_config(page_title="TheGhalluBot", page_icon="🎨", layout="centered")
st.markdown("""
    <style>
    .stApp { background: #0a0a0c; color: #00f2ff; }
    .stChatMessage { border-radius: 20px; border: 1px solid #7000ff; padding: 15px; }
    h1 { text-align: center; text-transform: uppercase; letter-spacing: 5px; color: #7000ff; text-shadow: 0 0 10px #7000ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("👾 TheGhalluBot v2.0")

# 2. Setup Clients
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
POL_API_KEY = st.secrets["POLLINATIONS_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Image Generation History
with st.sidebar:
    st.header("🎨 Artist Studio")
    if st.button("🗑️ Wipe Memory"):
        st.session_state.messages = []
        st.rerun()

# 3. The Image Generator Function
def generate_image(prompt):
    # Construct the Pollinations URL with your key
    # Model 'flux' is currently the highest quality available
    encoded_prompt = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true&model=flux&seed={time.time()}"
    headers = {"Authorization": f"Bearer {POL_API_KEY}"}
    
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        return image_url
    return None

# 4. Chat & Art Logic
if prompt := st.chat_input("Ask for a story or a drawing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Check if user wants an image
        trigger_words = ["draw", "generate", "make a picture", "image of", "create"]
        if any(word in prompt.lower() for word in trigger_words):
            with st.spinner("🎨 TheGhalluBot is painting..."):
                img_url = generate_image(prompt)
                if img_url:
                    st.image(img_url, caption=f"Generated: {prompt}", use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": f"![Generated Image]({img_url})"})
                else:
                    st.error("The paintbrush broke! Try again.")
        else:
            # Normal Groq Chat
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
