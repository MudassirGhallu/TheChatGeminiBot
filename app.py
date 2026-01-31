import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini 1.5 Bot", page_icon="🤖")
st.title("🤖 Stable Gemini Bot")

if st.sidebar.button("Reset Bot"):
    st.session_state.messages = []
    st.rerun()

# --- THE FIX IS HERE ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Use just 'gemini-1.5-flash' without prefixes
# Adding a system_instruction helps prevent long, quota-draining answers
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="You are a helpful assistant. Keep your answers brief and concise."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # We use 'generate_content' on the simple prompt for now 
            # to ensure the connection is working.
            response = model.generate_content(prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("The model returned an empty response.")
        except Exception as e:
            st.error(f"Error: {e}")
