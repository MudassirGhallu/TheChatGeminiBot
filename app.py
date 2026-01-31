import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="Gemini 2.0 Bot", page_icon="🤖")
st.title("🤖 My Gemini 2.0 Chatbot")

# Clear History Button
if st.sidebar.button("Reset Chat"):
    st.session_state.messages = []
    st.rerun()

# Setup API - Using the most stable 2.0 ID
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
# 'gemini-2.0-flash' is the stable name for 2026
model = genai.GenerativeModel('gemini-2.0-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Logic
if prompt := st.chat_input("Say hi!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # We send only the prompt to keep it simple and avoid 429 errors
            response = model.generate_content(prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("Gemini stayed silent. Try a different prompt.")
        except Exception as e:
            # If 2.0 fails, it will tell us why exactly
            st.error(f"Connection Error: {e}")
