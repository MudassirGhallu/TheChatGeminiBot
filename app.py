import time
import streamlit as st
from google import genai

# Page Config
st.set_page_config(page_title="Gemini 2.0 Bot", page_icon="⚡")
st.title("⚡ Gemini 2.0 Flash Chatbot")

# Sidebar - Clear Chat
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# Setup the Client
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_ID = "gemini-2.0-flash"

# Initialize chat history with the NEW format Gemini 2.0 likes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Accessing the text inside the 'parts' list
        st.markdown(message["parts"][0])

# User Input
if prompt := st.chat_input("Ask Gemini 2.0 anything..."):
    # NEW FORMAT: role must be 'user' and text must be inside 'parts'
    user_msg = {"role": "user", "parts": [prompt]}
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        success = False
        for i in range(3): # 3 Retries
            try:
                # Passing the history correctly
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=st.session_state.messages
                )
                
                bot_text = response.text
                st.markdown(bot_text)
                
                # Store assistant response in the same 'parts' format
                st.session_state.messages.append({"role": "model", "parts": [bot_text]})
                success = True
                break
            except Exception as e:
                if "429" in str(e):
                    st.warning(f"Rate limit hit! Waiting {i+2}s...")
                    time.sleep(i + 2)
                else:
                    st.error(f"Error: {e}")
                    break
        
        if not success:
            st.error("Still hitting limits. Try 'Clear Conversation'.")
