"""
Buddy AI - An AI-powered chat application with Google Gemini
Main application file with clean modular architecture
"""

import streamlit as st
import datetime
import uuid
import time
from backend.firebase_service import (
    save_user_to_firestore, save_chat_to_firestore, load_user_chats, 
    load_user_flashcards, delete_flashcards_from_firestore,
    load_user_personas, save_persona_to_firestore, delete_persona_from_firestore,
    get_db
)
from backend.auth_service import (
    init_google_oauth, get_authorization_url, exchange_code_for_token, verify_google_token
)
from backend.gemini_service import get_gemini_client, get_response, get_response_streaming
from backend.session_store import create_session, get_session, delete_session
from frontend.ui_components import render_auth_button, render_sidebar, render_chat_interface, PERSONAS
from frontend.flashcard_components import render_flashcard_interface
from frontend.analytics_components import render_analytics_page

# Configure page
st.set_page_config(
    page_title="BUDDY AI", 
    page_icon="asset/icon.png",
    initial_sidebar_state="expanded"
)

# Load global CSS FIRST — before anything else renders
# This ensures top padding applies to ALL pages (chat, analytics, flashcards)
from frontend.ui_components import load_css as _load_css
_global_css = _load_css("frontend/styles.css")
if _global_css:
    st.markdown(_global_css, unsafe_allow_html=True)

# Load app icon as base64 for inline use
import base64, pathlib
_icon_bytes = pathlib.Path("asset/icon.png").read_bytes()
_icon_b64 = base64.b64encode(_icon_bytes).decode()

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

if "partial_response" not in st.session_state:
    st.session_state.partial_response = None

if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

if "queued_files" not in st.session_state:
    st.session_state.queued_files = []

if "show_upload_modal" not in st.session_state:
    st.session_state.show_upload_modal = False

if "upload_for_message_idx" not in st.session_state:
    st.session_state.upload_for_message_idx = None

if "flashcard_mode" not in st.session_state:
    st.session_state.flashcard_mode = False

if "sidebar_tab" not in st.session_state:
    st.session_state.sidebar_tab = "home"

if "editing_msg_idx" not in st.session_state:
    st.session_state.editing_msg_idx = None

# --- Handle sign-out flag (set by sign-out button, processed on this rerun) ---
if st.session_state.get('_signing_out'):
    # Delete server-side session
    token = st.query_params.get('session')
    if token:
        delete_session(token)
    # Reset user-related session state
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.chat_sessions = {}
    st.session_state.current_session_id = None
    st.session_state.selected_persona = "Default"
    st.session_state.flashcard_mode = False
    st.session_state._signing_out = False
    # Clear query params (removes session token from URL)
    st.query_params.clear()
    st.rerun()

# Get user from session state after initialization
user = st.session_state.user

# Restore session from server-side token on page refresh
if not user:
    token = st.query_params.get('session')
    if token:
        stored_user = get_session(token)
        if stored_user:
            st.session_state.user = stored_user
            user = stored_user
            # Load chats from Firestore for the restored user
            chats = load_user_chats(stored_user['user_id'])
            st.session_state.chat_sessions = chats

            # Load user's flashcard sets
            from backend.firebase_service import load_user_flashcards
            flashcard_sets = load_user_flashcards(user['user_id'])
            st.session_state.flashcard_sets = flashcard_sets

            custom_personas = load_user_personas(user['user_id'])
            st.session_state.custom_personas = custom_personas  

# Check for OAuth callback
query_params = st.query_params
if 'code' in query_params and not user:
    # Show a welcome animation while OAuth processes
    import base64, pathlib
    _icon_bytes = pathlib.Path("asset/icon.png").read_bytes()
    _icon_b64 = base64.b64encode(_icon_bytes).decode()
    st.markdown(f"""
    <style>
        @keyframes buddyPulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.85; }}
            50% {{ transform: scale(1.08); opacity: 1; }}
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes dotBounce {{
            0%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-8px); }}
        }}
        .welcome-wrap {{
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 70vh; gap: 18px;
            animation: fadeInUp 0.6s ease-out;
        }}
        .welcome-icon {{
            width: 80px; height: 80px;
            animation: buddyPulse 1.8s ease-in-out infinite;
        }}
        .welcome-icon img {{
            width: 100%; height: 100%; object-fit: contain;
            border-radius: 16px;
        }}
        .welcome-title {{
            font-size: 28px; font-weight: 700; color: #e5e7eb;
            letter-spacing: -0.5px;
        }}
        .welcome-dots {{ display: flex; gap: 6px; margin-top: 4px; }}
        .welcome-dots span {{
            width: 8px; height: 8px; border-radius: 50%;
            background: #818cf8; display: inline-block;
            animation: dotBounce 1.2s ease-in-out infinite;
        }}
        .welcome-dots span:nth-child(2) {{ animation-delay: 0.15s; }}
        .welcome-dots span:nth-child(3) {{ animation-delay: 0.3s; }}
        .welcome-sub {{
            font-size: 15px; color: #9ca3af; margin-top: -4px;
        }}
    </style>
    <div class="welcome-wrap">
        <div class="welcome-icon"><img src="data:image/png;base64,{_icon_b64}" alt="Buddy AI" /></div>
        <div class="welcome-title">Welcome to B<span style="color: #8b5cf6;">U</span>DDY AI</div>
        <div class="welcome-dots"><span></span><span></span><span></span></div>
        <div class="welcome-sub">Signing you in…</div>
    </div>
    """, unsafe_allow_html=True)

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

            from backend.firebase_service import load_user_flashcards
            flash_sets = load_user_flashcards(user['user_id'])
            st.session_state.flashcard_sets = flash_sets
            
            # Save user to Firestore
            save_user_to_firestore(user)
            
            # Load user's previous chats from Firestore
            chats = load_user_chats(user['user_id'])
            st.session_state.chat_sessions = chats

            flashcard_sets = load_user_flashcards(stored_user['user_id'])
            st.session_state.flashcard_sets = flashcard_sets

            # Load user's custom personas  ← ADD THIS
            custom_personas = load_user_personas(stored_user['user_id'])
            st.session_state.custom_personas = custom_personas
            
            # Create server-side session and put token in URL
            session_token = create_session(user)
            st.query_params.clear()
            st.query_params['session'] = session_token
            st.rerun()
        else:
            st.error("Failed to verify token")

# Main layout
# Always render sidebar on the left
render_sidebar(user)

if st.session_state.get('sidebar_tab') == 'analytics':
    render_analytics_page()
elif st.session_state.get('flashcard_mode', False):
    if user and not st.session_state.get('flashcard_sets'):
        from backend.firebase_service import load_user_flashcards
        st.session_state.flashcard_sets = load_user_flashcards(user['user_id'])
    render_flashcard_interface()
else:

    # Main content area
    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 12px;">'
        f'<img src="data:image/png;base64,{_icon_b64}" style="width: 42px; height: 42px; border-radius: 8px;" />'
        f'<h1 style="margin: 0; padding: 0;">B<span style="color: #818cf8;">U</span>DDY AI</h1>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("Powered by Google Gemini")

    # If not logged in, show auth button for signup opportunity
    if not user:
        st.info("👤 Sign in to save your chat history across sessions")

    # Check if there's a message to process from user input
    message_to_process = st.session_state.get('pending_user_input')
    if message_to_process:
        st.session_state.pending_user_input = None

    # STEP 1: Prepare user message in state BEFORE rendering chat history
    if message_to_process:
        # Setup session ID
        if st.session_state.current_session_id is None:
            new_id = str(uuid.uuid4())[:8]
            st.session_state.current_session_id = new_id
            st.session_state.chat_sessions[new_id] = {
                "title": generate_chat_title(message_to_process),
                "messages": [],
                "timestamp": datetime.datetime.now().isoformat(),
                "persona": st.session_state.get('selected_persona', 'Default')
            }
        
        # Add user message (only if not already the last message)
        if not st.session_state.messages or st.session_state.messages[-1].get("content") != message_to_process:
            st.session_state.messages.append({"role": "user", "content": message_to_process})
            st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
        
        # Save user part to Firestore
        if user:
            save_chat_to_firestore(user['user_id'], st.session_state.current_session_id, st.session_state.messages, st.session_state.chat_sessions[st.session_state.current_session_id]["title"])

    # STEP 1.5: Recover partial response if generation was stopped mid-stream
    if st.session_state.get('partial_response') and not message_to_process:
        partial = st.session_state.partial_response
        st.session_state.partial_response = None
        if partial.strip():
            st.session_state.messages.append({"role": "assistant", "content": partial})
            if st.session_state.current_session_id:
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
                if user:
                    save_chat_to_firestore(user['user_id'], st.session_state.current_session_id, st.session_state.messages, st.session_state.chat_sessions[st.session_state.current_session_id]["title"])
        st.session_state.stop_processing = False
        st.session_state.is_processing = False

    # STEP 2: Render chat history (includes newly added user message)
    user_input = render_chat_interface()
    if user_input:
        st.session_state.pending_user_input = user_input
        st.rerun()

    # STEP 3: Stream the AI response AFTER chat history is displayed
    if message_to_process:
        now = datetime.datetime.now()
        if st.session_state.last_request_time and (now - st.session_state.last_request_time) < MIN_TIME_BETWEEN_REQUESTS:
            st.warning("⏳ Please wait a moment...")
        else:
            with st.chat_message("assistant"):
                status_container = st.empty()
                response_container = st.empty()

            # Stop button outside chat message — fixed at bottom center via CSS
            stop_btn_container = st.empty()

            try:
                st.session_state.is_processing = True
                st.session_state.stop_processing = False
                st.session_state.partial_response = None

                gemini_files = []
                # Handle uploaded files AND queued files from follow-ups
                all_files_to_process = (st.session_state.get('uploaded_files') or []) + (st.session_state.get('queued_files') or [])

                if all_files_to_process:
                    for uploaded_file in all_files_to_process:
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

                # GET STREAMING RESPONSE (Only if not stopped)
                if not st.session_state.stop_processing:
                    all_personas = {**PERSONAS, **st.session_state.get('custom_personas', {})}
                    instruction = all_personas.get(st.session_state.selected_persona, PERSONAS["Default"])

                    # Show "Buddy is thinking..." while waiting for first chunk
                    status_container.markdown("""
                    <style>
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                        .thinking-spinner {
                            display: inline-block;
                            width: 20px;
                            height: 20px;
                            border: 3px solid #818cf8;
                            border-top: 3px solid transparent;
                            border-radius: 50%;
                            animation: spin 0.8s linear infinite;
                            margin-right: 8px;
                            vertical-align: middle;
                        }
                    </style>
                    <div style="display: flex; align-items: center;">
                        <span class="thinking-spinner"></span>
                        <span>💭 <strong>Buddy is thinking...</strong></span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Stop button with on_click callback so partial response survives rerun
                    def _stop_generation():
                        st.session_state.stop_processing = True
                        st.session_state.is_processing = False

                    stop_btn_container.button(
                        "⏹ Stop generating",
                        key="stop_gen_btn",
                        on_click=_stop_generation,
                    )

                    # Build chat history for follow-up context
                    history_for_gemini = st.session_state.messages[:-1]  # exclude current user msg

                    # Stream the response in real-time
                    full_response = ""
                    first_chunk = True
                    for chunk in get_response_streaming(message_to_process, client, gemini_files, system_instruction=instruction, chat_history=history_for_gemini):
                        if st.session_state.stop_processing:
                            break
                        if first_chunk:
                            status_container.empty()
                            first_chunk = False
                        full_response += chunk
                        st.session_state.partial_response = full_response
                        response_container.markdown(full_response)

                    # Clear stop button after generation completes
                    stop_btn_container.empty()

                    # Save the response (full or partial)
                    if full_response:
                        st.session_state.partial_response = None
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()

                        st.session_state.queued_files = []
                        st.session_state.uploaded_files = None

                        if user:
                            save_chat_to_firestore(user['user_id'], st.session_state.current_session_id, st.session_state.messages, st.session_state.chat_sessions[st.session_state.current_session_id]["title"])

                    st.session_state.last_request_time = datetime.datetime.now()
                    st.session_state.is_processing = False
                    st.rerun()
                else:
                    status_container.empty()
                    response_container.empty()
                    stop_btn_container.empty()
                    st.session_state.is_processing = False

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.is_processing = False
                st.session_state.partial_response = None
                if 'stop_btn_container' in locals():
                    stop_btn_container.empty()