import time
import streamlit as st
from google import genai

# Page Config
st.set_page_config(page_title="Gemini 2.0 Bot", page_icon="⚡")
st.title("⚡ Gemini 2.0 Flash Chatbot")

# Sidebar - Clear Chat Button
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# Setup the Client
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_ID = "gemini-2.0-flash"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask Gemini 2.0 anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot Response with Retry Logic
    with st.chat_message("assistant"):
        success = False
        retries = 3
        for i in range(retries):
            try:
                # We send the whole message history so it has memory
                response = client.models.generate_content(
                    model=MODEL_ID, 
                    contents=st.session_state.messages 
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                success = True
                break 
            except Exception as e:
                if "429" in str(e):
                    st.warning(f"Rate limit hit! Retrying in {i+2} seconds...")
                    time.sleep(i + 2)
                else:
                    st.error(f"Error: {e}")
                    break
        
        if not success:
            st.error("I'm a bit overwhelmed. Please click 'Clear Conversation' or wait a minute.")
