"""
Buddy AI - An AI-powered chat application with Google Gemini
Main application file with clean modular architecture
"""

import streamlit as st
import datetime
import uuid

# Configure page
st.set_page_config(
    page_title="Buddy AI", 
    page_icon="asset/icon.png",
    initial_sidebar_state="expanded"
)

# Import backend services
from backend.firebase_service import (
    save_user_to_firestore, save_chat_to_firestore, load_user_chats, get_db
)
from backend.auth_service import (
    init_google_oauth, get_authorization_url, exchange_code_for_token, verify_google_token
)
from backend.gemini_service import get_gemini_client, get_response

# Import frontend components
from frontend.ui_components import render_auth_button, render_sidebar, render_chat_interface, PERSONAS

# Initialize Google OAuth
init_google_oauth()

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

# Server-side session store (persists across page refreshes)
@st.cache_resource
def get_session_store():
    """Persistent session store that survives page refreshes."""
    return {}

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

# Restore session from server-side store on page refresh
if not st.session_state.user and "session" in st.query_params:
    session_token = st.query_params["session"]
    session_data = get_session_store().get(session_token)
    if session_data:
        st.session_state.user = session_data["user"]
        st.session_state.chat_sessions = session_data.get("chats", {})
        st.session_state.selected_persona = session_data.get("selected_persona", "Default")
        st.session_state.custom_personas = session_data.get("custom_personas", {})

# Get Gemini client
client = get_gemini_client()

# Check for OAuth callback
query_params = st.query_params
user = st.session_state.user

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

# Render chat interface (works with or without login)
user_input = render_chat_interface()

# Handle user input
if user_input:
    # Create a new session if none exists
    if st.session_state.current_session_id is None:
        new_id = str(uuid.uuid4())[:8]
        # Generate title from first message
        chat_title = generate_chat_title(user_input)
        st.session_state.chat_sessions[new_id] = {
            "title": chat_title,
            "messages": [],
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.current_session_id = new_id
    
    # Add user message to current session
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
    
    # Save to Firestore only if logged in
    if user:
        save_chat_to_firestore(
            user['user_id'],
            st.session_state.current_session_id,
            st.session_state.messages,
            st.session_state.chat_sessions[st.session_state.current_session_id]["title"]
        )
    
    # Display the user's message immediately
    with st.chat_message("user"):
        st.write(user_input)
    
    # Check rate limiting
    now = datetime.datetime.now()
    if st.session_state.last_request_time and (now - st.session_state.last_request_time) < MIN_TIME_BETWEEN_REQUESTS:
        st.warning("⏳ Please wait a moment before asking another question...")
    else:
        with st.chat_message("assistant"):
            try:
                # Prepare uploaded files for Gemini
                gemini_files = None
                if st.session_state.get('uploaded_files'):
                    gemini_files = []
                    for uploaded_file in st.session_state.uploaded_files:
                        # Upload file to Gemini
                        import google.generativeai as genai
                        gemini_file = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)
                        gemini_files.append(gemini_file)
                
                # Get selected persona instruction
                all_personas = {**PERSONAS, **st.session_state.get('custom_personas', {})}
                persona_instruction = all_personas.get(st.session_state.selected_persona, PERSONAS["Default"])
                
                # Get response from Gemini
                response = get_response(user_input, client, gemini_files, system_instruction=persona_instruction)
                
                # Display response
                st.write(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Save to session and Firestore (only if logged in)
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
                if user:
                    save_chat_to_firestore(
                        user['user_id'],
                        st.session_state.current_session_id,
                        st.session_state.messages,
                        st.session_state.chat_sessions[st.session_state.current_session_id]["title"]
                    )
                
                st.session_state.last_request_time = now
                
                # Sync session store for refresh persistence
                if "session" in st.query_params:
                    store = get_session_store()
                    token = st.query_params["session"]
                    if token in store:
                        store[token]["chats"] = st.session_state.chat_sessions
                
            except Exception as e:
                error_msg = f"❌ Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
                if user:
                    save_chat_to_firestore(
                        user['user_id'],
                        st.session_state.current_session_id,
                        st.session_state.messages,
                        st.session_state.chat_sessions[st.session_state.current_session_id]["title"]
                    )
