import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Gemini 2.0 Bot", page_icon="⚡")
st.title("⚡ Gemini 2.0 Flash Chatbot")

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_ID = "gemini-2.0-flash"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Gemini 2.0 anything..."):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate response
    with st.chat_message("assistant"):
        try:
            # We convert our list into the format the NEW SDK expects
            history_for_api = []
            for m in st.session_state.messages:
                history_for_api.append(
                    types.Content(role=m["role"], parts=[types.Part(text=m["content"])])
                )

            response = client.models.generate_content(
                model=MODEL_ID,
                contents=history_for_api
            )
            
            bot_text = response.text
            st.markdown(bot_text)
            st.session_state.messages.append({"role": "model", "content": bot_text})
            
        except Exception as e:
            if "429" in str(e):
                st.error("Rate limit hit. Please wait 60 seconds and try again.")
            else:
                st.error(f"Error: {e}")
