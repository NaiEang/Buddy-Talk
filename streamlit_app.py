"""
Buddy AI - An AI-powered chat application with Google Gemini
Main application file with clean modular architecture
"""

import streamlit as st
import datetime
import uuid
import time
from backend.firebase_service import (
    save_user_to_firestore, save_chat_to_firestore, load_user_chats, get_db
)
from backend.auth_service import (
    init_google_oauth, get_authorization_url, exchange_code_for_token, verify_google_token
)
from backend.gemini_service import get_gemini_client, get_response
from frontend.ui_components import render_auth_button, render_sidebar, render_chat_interface, PERSONAS

# Configure page
st.set_page_config(
    page_title="Buddy AI", 
    page_icon="asset/icon.png",
    initial_sidebar_state="expanded"
)

init_google_oauth()
client = get_gemini_client()

# Rate limiting constant
MIN_TIME_BETWEEN_REQUESTS = datetime.timedelta(seconds=3)

# Function to generate chat title from first message
def generate_chat_title(first_message: str, max_length: int = 20) -> str:
    """Generate a concise title from the first user message."""
    # Clean up the message
    title = first_message.strip()
    
    # Remove common question words and punctuation for cleaner title
    common_starts = ["what ", "how ", "why ", "can ", "could ", "would ", "should ", "tell ", "explain ", "help ", "show ", "do "]
    for start in common_starts:
        if title.lower().startswith(start):
            title = title[len(start):]
            break
    
    # Remove trailing punctuation
    title = title.rstrip("?!.,")
    
    # Truncate to max length
    if len(title) > max_length:
        title = title[:max_length].rsplit(' ', 1)[0] + "..."
    
    return title if title else "New Chat"

# Import session store from backend (avoids circular imports)
from backend.session_store import get_session_store

# Initialize session state
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "custom_personas" not in st.session_state:
    st.session_state.custom_personas = {}

if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = "Default"

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = None

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

if "stop_processing" not in st.session_state:
    st.session_state.stop_processing = False

if "should_cancel" not in st.session_state:
    st.session_state.should_cancel = False

if "editing" not in st.session_state:
    st.session_state.editing = False

if "edit_message_index" not in st.session_state:
    st.session_state.edit_message_index = None

if "process_message" not in st.session_state:
    st.session_state.process_message = None

if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

# Get user from session state after initialization
user = st.session_state.user

# Restore session from server-side store on page refresh
if not st.session_state.user and "session" in st.query_params:
    session_token = st.query_params["session"]
    session_data = get_session_store().get(session_token)
    if session_data:
        st.session_state.user = session_data["user"]
        st.session_state.chat_sessions = session_data.get("chats", {})
        st.session_state.selected_persona = session_data.get("selected_persona", "Default")
        st.session_state.custom_personas = session_data.get("custom_personas", {})

# Check for OAuth callback
query_params = st.query_params
if 'code' in query_params and not user:
    """Handle OAuth callback"""
    code = query_params['code']
    token_response = exchange_code_for_token(code)
    
    if token_response and 'id_token' in token_response:
        user_info = verify_google_token(token_response['id_token'])
        if user_info:
            # Format user info
            user = {
                'user_id': user_info.get('sub', user_info.get('email')),
                'email': user_info.get('email'),
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', ''),
                'email_verified': user_info.get('email_verified', False)
            }
            
            st.session_state.user = user
            
            # Save user to Firestore
            save_user_to_firestore(user)
            
            # Load user's previous chats from Firestore
            chats = load_user_chats(user['user_id'])
            st.session_state.chat_sessions = chats
            
            # Store session server-side for refresh persistence
            session_token = str(uuid.uuid4())
            get_session_store()[session_token] = {
                "user": user,
                "chats": chats
            }
            
            # Clear auth code, keep session token in URL
            st.query_params.clear()
            st.query_params["session"] = session_token
            st.rerun()
        else:
            st.error("Failed to verify token")

# Main layout
# Always render sidebar on the left
render_sidebar(user)

# Main content area
col1, col2 = st.columns([1, 12])
with col1:
    st.image("asset/icon.png", width=50)
with col2:
    st.markdown("# Buddy AI")
st.markdown("Powered by Google Gemini")

# If not logged in, show auth button for signup opportunity
if not user:
    st.info("👤 Sign in to save your chat history across sessions")

# First, check if there's a message to process from editing OR from new user input
message_to_process = st.session_state.get('process_message') or st.session_state.get('pending_user_input')
st.session_state.process_message = None
if message_to_process == st.session_state.get('pending_user_input'):
    st.session_state.pending_user_input = None

# Handle user input
if message_to_process:
    # 1. SETUP SESSION ID
    if st.session_state.current_session_id is None:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_session_id = new_id
        st.session_state.chat_sessions[new_id] = {
            "title": generate_chat_title(message_to_process),
            "messages": [],
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    # 2. ADD USER MESSAGE (FIXED: Only add if it's not already the last message)
    # This prevents the double-bubble issue during edits
    if not st.session_state.messages or st.session_state.messages[-1].get("content") != message_to_process:
        st.session_state.messages.append({"role": "user", "content": message_to_process})
        st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
    
    # Save user part to Firestore
    if user:
        save_chat_to_firestore(user['user_id'], st.session_state.current_session_id, st.session_state.messages, st.session_state.chat_sessions[st.session_state.current_session_id]["title"])
    
    # 3. RATE LIMIT CHECK
    now = datetime.datetime.now()
    if st.session_state.last_request_time and (now - st.session_state.last_request_time) < MIN_TIME_BETWEEN_REQUESTS:
        st.warning("⏳ Please wait a moment...")
    else:
        with st.chat_message("assistant"):
            stop_btn_container = st.empty()
            thinking_placeholder = st.empty()
            status_container = st.empty()
            try:
                st.session_state.is_processing = True
                st.session_state.stop_processing = False

                if stop_btn_container.button("⏹️ Stop Buddy", key="stop_gen_btn", use_container_width=True):
                    st.session_state.stop_processing = True
                    st.session_state.is_processing = False
                    st.rerun()
                
                gemini_files = []
                if st.session_state.get('uploaded_files'):
                    for uploaded_file in st.session_state.uploaded_files:
                        if st.session_state.stop_processing: break
                        
                        with status_container.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                            import google.generativeai as genai
                            myfile = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)
                            while myfile.state.name == "PROCESSING":
                                if st.session_state.stop_processing: break
                                time.sleep(1)
                                myfile = genai.get_file(myfile.name)
                            status.update(label=f"✅ {uploaded_file.name} ready!", state="complete")
                            gemini_files.append(myfile)
                
                # 4. GET RESPONSE (Only if not stopped)
                if not st.session_state.stop_processing:
                    with st.spinner("Buddy is thinking..."):
                        all_personas = {**PERSONAS, **st.session_state.get('custom_personas', {})}
                        instruction = all_personas.get(st.session_state.selected_persona, PERSONAS["Default"])
                        
                        # Generate the response
                        response_text = get_response(message_to_process, client, gemini_files, system_instruction=instruction)
                
                    # Display response
                    st.markdown(response_text)
                    
                    # Add AI response to memory
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()

                    if user:
                        save_chat_to_firestore(user['user_id'], st.session_state.current_session_id, st.session_state.messages, st.session_state.chat_sessions[st.session_state.current_session_id]["title"])
                    
                    st.session_state.last_request_time = datetime.datetime.now()
                    st.session_state.is_processing = False
                    stop_btn_container.empty()
                    st.rerun() # Refresh to keep bar at bottom
                else:
                    st.warning("✋ Buddy stopped at your request.")
                    st.session_state.is_processing = False
                    stop_btn_container.empty()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.is_processing = False
                if 'stop_btn_container' in locals():
                    stop_btn_container.empty()

# Always render input interface at the bottom
render_chat_interface()