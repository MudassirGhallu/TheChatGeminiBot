import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="Gemini 1.5 Bot", page_icon="🤖")
st.title("🤖 Gemini 1.5 Flash Bot")

# Sidebar to reset everything
if st.sidebar.button("Reset Bot & Clear History"):
    st.session_state.messages = []
    st.rerun()

# Setup 1.5 Flash
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Simple and easy syntax for 1.5
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
