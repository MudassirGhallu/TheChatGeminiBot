import streamlit as st
from google import genai

# Page Config
st.set_page_config(page_title="Gemini 2.0 Bot", page_icon="⚡")
st.title("⚡ Gemini 2.0 Flash Chatbot")

# Setup the NEW Client
# Make sure your Streamlit Secret is still named GOOGLE_API_KEY
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

    # Bot Response
    with st.chat_message("assistant"):
        try:
            # New syntax for Gemini 2.0
            response = client.models.generate_content(
                model=MODEL_ID, 
                contents=prompt
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Something went wrong: {e}")
