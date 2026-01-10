import streamlit as st
from google import genai # FIXED: New import
from google.genai import types # Added for System Instructions
import os
from dotenv import load_dotenv

# --- CONFIGURATION & LOGIC ---
load_dotenv() 

st.set_page_config(page_title="Buddy - AI Second Brain", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [] 

# --- SIDEBAR: SETTINGS & BRANDING ---
with st.sidebar:
    st.title("🤖 Buddy Settings")

    # Check .env first, if empty, use the input box
    env_key = os.getenv("GOOGLE_API_KEY", "")
    api_key_input = st.text_input("Gemini API Key:", type="password", value=env_key)
    
    buddy_mode = st.selectbox(
        "Choose Persona:",
        ["Strict Academic", "Casual Summarizer", "Corporate Professional"]
    )
    
    st.info(f"Buddy is currently in **{buddy_mode}** mode.")
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- GEMINI AI INITIALIZATION ---
if api_key_input:
    # FIXED: New way to initialize the client
    client = genai.Client(api_key=api_key_input)
    
    if buddy_mode == "Strict Academic":
        instructions = "You are Buddy, a formal academic assistant. Focus on citations and factual accuracy."
    elif buddy_mode == "Casual Summarizer":
        instructions = "You are Buddy, a friendly helper. Keep answers short and use emojis."
    else:
        instructions = "You are Buddy, a corporate analyst. Focus on action items and concise summaries."
else:
    st.warning("Please enter your Gemini API key in the sidebar to start.")
    st.stop()

# --- MAIN CHAT INTERFACE ---
st.title("💬 Chat with Buddy")
st.caption("A multimodal AI that remembers your files for you.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Ask Buddy something..."):
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Buddy is thinking..."):
            try:
                # FIXED: New way to call the model with System Instructions
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions
                    )
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                st.error(f"Something went wrong: {e}")