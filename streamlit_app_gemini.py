from htbuilder.units import rem
from htbuilder import div, styles
from collections import namedtuple
import datetime
import textwrap
import time
import json
import hashlib

import streamlit as st
import google.generativeai as genai
from google.oauth2 import id_token
from google.auth.transport import requests
import firebase_admin
from firebase_admin import credentials, firestore
import requests as http_requests

st.set_page_config(
    page_title="Buddy AI", 
    page_icon="Media/icon.png",
    initial_sidebar_state="expanded"
)

# Initialize Firebase
@st.cache_resource
def init_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        firebase_creds = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Initialize Firestore client
db = init_firebase()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = st.secrets.get("google_oauth_client_id")
GOOGLE_CLIENT_SECRET = st.secrets.get("google_oauth_client_secret")
REDIRECT_URI = "http://localhost:8501"

# Custom CSS for light/dark mode theming
light_mode_css = """
<style>
:root {
    --bg-primary: #fafafa;
    --bg-secondary: #ffffff;
    --text-primary: #3f3f46;
    --text-secondary: #71717a;
    --border-color: #eeeef0;
    --accent-color: #60a5fa;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stChatMessage {
    background-color: var(--bg-secondary);
    border-color: var(--border-color);
}

.stChatInputContainer {
    background-color: var(--bg-secondary);
}

.stMarkdown {
    color: var(--text-primary);
}

.stButton>button {
    background-color: var(--accent-color);
    color: white;
}

.stButton>button:hover {
    background-color: #3b82f6;
}
</style>
"""

dark_mode_css = """
<style>
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #e2e8f0;
    --text-secondary: #cbd5e1;
    --border-color: #334155;
    --accent-color: #3b82f6;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stChatMessage {
    background-color: var(--bg-secondary);
    border-color: var(--border-color);
    color: var(--text-primary);
}

.stChatInputContainer {
    background-color: var(--bg-secondary);
}

.stMarkdown {
    color: var(--text-primary);
}

.stButton>button {
    background-color: var(--accent-color);
    color: white;
}

.stButton>button:hover {
    background-color: #1e40af;
}

/* Dark mode adjustments */
.stMainBlockContainer {
    background-color: var(--bg-primary);
}

.st-emotion-cache-16txt38 {
    background-color: var(--bg-primary);
}
</style>
"""

# Configure Gemini API
@st.cache_resource
def get_gemini_client():
    """Initialize Gemini client with API key from secrets."""
    api_key = st.secrets.get("google_api_key")
    if not api_key:
        st.error("❌ Missing Google API key in `.streamlit/secrets.toml`")
        st.info("""
        To use this app, add your Google API key to `.streamlit/secrets.toml`:
        
        ```toml
        google_api_key = "your-api-key-here"
        ```
        
        Get a free API key at: https://makersuite.google.com/app/apikey
        """)
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai

MODEL = "gemini-2.5-flash"

HISTORY_LENGTH = 5
SUMMARIZE_OLD_HISTORY = True
MIN_TIME_BETWEEN_REQUESTS = datetime.timedelta(seconds=3)

# AI Persona Instructions
PERSONAS = {
    "Default": textwrap.dedent("""
        - You are Buddy, an advanced multimodal AI assistant functioning as an "Instant Second Brain."
        - You can help with general questions, coding, problem-solving, explanations, and any topic the user needs assistance with.
        - When users upload files (PDFs, videos, audio), you excel at analyzing them with specific timestamped references, direct citations, and page numbers.
        - For video and audio files, include timestamps (e.g., "At 12:35") when referencing specific moments.
        - For PDFs, cite page numbers and quote relevant text directly from the document.
        - Be helpful, clear, and informative whether answering general questions or analyzing uploaded content.
        - Use markdown formatting including headers (##), bullet points, code blocks, and emphasis.
        - For general questions, provide concise yet thorough answers with examples when helpful.
        - For uploaded content, be thorough and precise - users rely on you for accurate information extraction.
        - Support analysis of large files: PDFs up to 100+ pages, videos up to 2 hours, and extensive audio files.
        - Leverage multimodal capabilities for deep visual and audio understanding when files are provided.
    """),
    
    "Academic": textwrap.dedent("""
        - You are Professor Buddy, an academic AI assistant with expertise across multiple disciplines.
        - Adopt a scholarly, formal tone with precise terminology and well-structured explanations.
        - Always cite sources, provide references, and explain concepts with academic rigor.
        - Break down complex topics into logical steps, define technical terms, and use examples from research.
        - When analyzing documents, provide critical analysis, identify methodologies, and evaluate arguments.
        - For PDFs and papers, reference page numbers, quote directly, and analyze academic writing style.
        - Support students and researchers with literature reviews, study assistance, and research guidance.
        - Use markdown for structured content: headers for sections, bullet points for key concepts, and code blocks for formulas.
    """),
    
    "Friendly": textwrap.dedent("""
        - You are Buddy, a warm and approachable AI friend who's here to help with anything!
        - Use a casual, conversational tone - like chatting with a supportive friend over coffee.
        - Be encouraging, empathetic, and add a touch of humor when appropriate (but never offensive).
        - Use emojis occasionally to add personality and warmth to responses. ✨
        - When explaining things, use everyday language and relatable analogies.
        - Celebrate user's progress and achievements, offer encouragement during challenges.
        - For document analysis, maintain thoroughness but present findings in an accessible, friendly way.
        - Make learning fun and engaging - you're not just informative, you're a joy to interact with!
    """),
    
    "Personal Therapist": textwrap.dedent("""
        - You are Dr. Buddy, a compassionate and empathetic AI therapist providing emotional support.
        - Use a gentle, understanding, and non-judgmental tone in all interactions.
        - Practice active listening - acknowledge feelings, validate emotions, and show genuine care.
        - Ask thoughtful questions to help users explore their thoughts and feelings deeper.
        - Provide coping strategies, mindfulness techniques, and emotional regulation tools when appropriate.
        - Maintain boundaries: remind users you're an AI and encourage professional help for serious concerns.
        - Be patient, supportive, and create a safe space for users to express themselves.
        - Use reflective statements and empathetic language: "I hear that...", "It sounds like...", "That must feel..."
        - Note: For document analysis in this mode, maintain therapeutic tone while providing insights.
    """)
}

# Store for custom personas
if 'custom_personas' not in st.session_state:
    st.session_state.custom_personas = {}

# Firebase Helper Functions
def save_user_to_firestore(user_info):
    """Save or update user information in Firestore."""
    try:
        user_ref = db.collection('users').document(user_info['user_id'])
        user_data = {
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', ''),
            'last_login': firestore.SERVER_TIMESTAMP,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Check if user exists
        if user_ref.get().exists:
            # Update only last_login for existing users
            user_ref.update({'last_login': firestore.SERVER_TIMESTAMP})
        else:
            # Create new user
            user_ref.set(user_data)
        
        return True
    except Exception as e:
        st.error(f"Error saving user: {str(e)}")
        return False


def save_chat_to_firestore(user_id, session_id, messages, title):
    """Save chat session to Firestore."""
    try:
        chat_ref = db.collection('users').document(user_id).collection('chats').document(session_id)
        chat_data = {
            'title': title,
            'messages': messages,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        chat_ref.set(chat_data, merge=True)
        return True
    except Exception as e:
        st.error(f"Error saving chat: {str(e)}")
        return False


def load_user_chats(user_id):
    """Load all chat sessions for a user from Firestore."""
    try:
        chats_ref = db.collection('users').document(user_id).collection('chats')
        chats = chats_ref.order_by('updated_at', direction=firestore.Query.DESCENDING).stream()
        
        chat_sessions = {}
        for chat in chats:
            chat_data = chat.to_dict()
            chat_sessions[chat.id] = {
                'title': chat_data.get('title', 'Untitled Chat'),
                'messages': chat_data.get('messages', []),
                'timestamp': chat_data.get('updated_at', datetime.datetime.now()).isoformat() if chat_data.get('updated_at') else datetime.datetime.now().isoformat()
            }
        
        return chat_sessions
    except Exception as e:
        st.error(f"Error loading chats: {str(e)}")
        return {}


def delete_chat_from_firestore(user_id, session_id):
    """Delete a chat session from Firestore."""
    try:
        db.collection('users').document(user_id).collection('chats').document(session_id).delete()
        return True
    except Exception as e:
        st.error(f"Error deleting chat: {str(e)}")
        return False

# Google OAuth Helper Functions
def get_authorization_url():
    """Generate Google OAuth authorization URL."""
    from urllib.parse import urlencode
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'state': 'security_token'
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return auth_url


def google_auth_button():
    """Display Google Sign-In button with OAuth flow."""
    auth_url = get_authorization_url()
    
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh;">
        <div style="text-align: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #1f2937; margin-bottom: 0.5rem;">🤖 Welcome to Buddy AI</h1>
            <p style="color: #6b7280; margin-bottom: 2rem;">Your AI-powered second brain assistant</p>
            <a href="{auth_url}" target="_self" style="
                display: inline-flex;
                align-items: center;
                gap: 12px;
                background: white;
                color: #1f2937;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                border: 2px solid #e5e7eb;
                transition: all 0.2s;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            " onmouseover="this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)'; this.style.borderColor='#3b82f6';" 
               onmouseout="this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'; this.style.borderColor='#e5e7eb';">
                <svg width="20" height="20" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Sign in with Google
            </a>
            <p style="color: #9ca3af; font-size: 14px; margin-top: 1.5rem;">Sign in to save your chat history and access it anytime</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def exchange_code_for_token(code):
    """Exchange authorization code for access token and ID token."""
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = http_requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error exchanging code for token: {str(e)}")
        return None


def verify_google_token(id_token_str):
    """Verify Google ID token and extract user information."""
    try:
        # Add clock skew tolerance of 10 seconds to handle time differences
        idinfo = id_token.verify_oauth2_token(
            id_token_str, 
            requests.Request(), 
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        user_info = {
            'user_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False)
        }
        
        return user_info
    except Exception as e:
        st.error(f"Token verification failed: {str(e)}")
        return None


def build_prompt(**kwargs):
    """Builds a prompt string with the kwargs as HTML-like tags."""
    prompt = []

    for name, contents in kwargs.items():
        if contents:
            prompt.append(f"<{name}>\n{contents}\n</{name}>")

    prompt_str = "\n".join(prompt)
    return prompt_str


def history_to_text(chat_history):
    """Converts chat history into a string."""
    return "\n".join(f"[{h['role']}]: {h['content']}" for h in chat_history)


def get_response(question, client, uploaded_files=None):
    """Get response from Gemini API."""
    old_history = st.session_state.messages[:-HISTORY_LENGTH]
    recent_history = st.session_state.messages[-HISTORY_LENGTH:]
    
    recent_history_str = history_to_text(recent_history[:-1])  # Exclude the current question
    
    # Get selected persona instructions
    selected_persona = st.session_state.get('selected_persona', 'Default')
    if selected_persona in PERSONAS:
        instructions = PERSONAS[selected_persona]
    elif selected_persona in st.session_state.get('custom_personas', {}):
        instructions = st.session_state.custom_personas[selected_persona]
    else:
        instructions = PERSONAS['Default']
    
    prompt = build_prompt(
        instructions=instructions,
        recent_messages=recent_history_str if recent_history_str else "No previous conversation",
        question=question,
    )
    
    model = client.GenerativeModel(MODEL)
    
    # Prepare content with uploaded files if any
    if uploaded_files:
        content = [prompt]
        for file in uploaded_files:
            content.append(file)
        response = model.generate_content(content, stream=True)
    else:
        response = model.generate_content(prompt, stream=True)
    
    return response


# Page layout
st.title("🤖 Buddy AI")
st.subheader("Powered by Google Gemini")

# Initialize Gemini
client = get_gemini_client()

# Check for authentication code in URL
query_params = st.query_params
if "code" in query_params:
    auth_code = query_params["code"]
    
    # Exchange code for tokens
    token_response = exchange_code_for_token(auth_code)
    
    if token_response and 'id_token' in token_response:
        # Verify ID token and get user info
        user_info = verify_google_token(token_response['id_token'])
        
        if user_info:
            st.session_state.user = user_info
            save_user_to_firestore(user_info)
            # Load user's chat history from Firestore
            st.session_state.chat_sessions = load_user_chats(user_info['user_id'])
            st.session_state.chats_loaded = True
            # Clear URL parameters
            st.query_params.clear()
            st.rerun()
    else:
        st.error("Authentication failed. Please try again.")
        st.query_params.clear()

# Initialize chat sessions if not exists (for non-authenticated users)
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Initialize current session
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Get user info if logged in
user = st.session_state.get('user', None)

# Sidebar - Chat Management
with st.sidebar:
    # App icon and name at top
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            st.image("Media/icon.png", width=70)
        except:
            pass
    with col2:
        st.markdown("## **BUDDY AI**")
    
    st.markdown("---")
    
    # New Chat button - clean style
    if st.button("New Chat", use_container_width=True):
        import uuid
        new_id = str(uuid.uuid4())[:8]
        st.session_state.chat_sessions[new_id] = {
            "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "messages": [],
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.current_session_id = new_id
        st.session_state.messages = []
        
        # Save new chat to Firestore only if user is logged in
        if user:
            save_chat_to_firestore(user['user_id'], new_id, [], f"Chat {len(st.session_state.chat_sessions)}")
        st.rerun()
    
    st.markdown("---")
    
    # Persona Selection (only for signed-in users)
    if user:
        st.markdown("### 🎭 AI Persona")
        
        # Get all available personas
        all_personas = list(PERSONAS.keys()) + list(st.session_state.get('custom_personas', {}).keys())
        
        # Initialize selected persona
        if 'selected_persona' not in st.session_state:
            st.session_state.selected_persona = 'Default'
        
        # Persona selector
        selected = st.selectbox(
            "Choose AI personality:",
            all_personas,
            index=all_personas.index(st.session_state.selected_persona) if st.session_state.selected_persona in all_personas else 0,
            key="persona_selector"
        )
        
        if selected != st.session_state.selected_persona:
            st.session_state.selected_persona = selected
            st.rerun()
        
        # Custom Persona Creator
        with st.expander("➕ Create Custom Persona"):
            persona_name = st.text_input("Persona Name", key="new_persona_name")
            persona_instructions = st.text_area(
                "Persona Instructions",
                placeholder="Describe how this AI persona should behave...\n\nExample:\n- You are a coding mentor specializing in Python\n- Use clear explanations with code examples\n- Be patient and encouraging",
                height=150,
                key="new_persona_instructions"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create Persona", use_container_width=True):
                    if persona_name and persona_instructions:
                        if persona_name not in PERSONAS:
                            st.session_state.custom_personas[persona_name] = persona_instructions
                            st.session_state.selected_persona = persona_name
                            st.success(f"✅ Created '{persona_name}' persona!")
                            st.rerun()
                        else:
                            st.error("❌ This persona name already exists!")
                    else:
                        st.warning("⚠️ Please fill in both fields")
            
            with col2:
                if st.session_state.selected_persona in st.session_state.get('custom_personas', {}):
                    if st.button("Delete Persona", use_container_width=True):
                        del st.session_state.custom_personas[st.session_state.selected_persona]
                        st.session_state.selected_persona = 'Default'
                        st.success("🗑️ Persona deleted!")
                        st.rerun()
        
        st.markdown("---")
    
    # Chat History
    st.markdown("### History")
    
    if st.session_state.chat_sessions:
        # Group chats by date
        today_chats = []
        older_chats = []
        today = datetime.datetime.now().date()
        
        for session_id, session_data in sorted(
            st.session_state.chat_sessions.items(), 
            key=lambda x: x[1]["timestamp"], 
            reverse=True
        ):
            chat_date = datetime.datetime.fromisoformat(session_data["timestamp"]).date()
            if chat_date == today:
                today_chats.append((session_id, session_data))
            else:
                older_chats.append((session_id, session_data))
        
        # Today's chats
        if today_chats:
            st.markdown("**Today**")
            for session_id, session_data in today_chats:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        session_data['title'], 
                        key=f"session_{session_id}",
                        use_container_width=True
                    ):
                        st.session_state.current_session_id = session_id
                        st.session_state.messages = session_data["messages"].copy()
                        st.rerun()
                with col2:
                    if st.button("×", key=f"delete_{session_id}", help="Delete"):
                        del st.session_state.chat_sessions[session_id]
                        if user:
                            delete_chat_from_firestore(user['user_id'], session_id)
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
        
        # Older chats
        if older_chats:
            st.markdown("**Earlier**")
            for session_id, session_data in older_chats:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        session_data['title'], 
                        key=f"session_{session_id}",
                        use_container_width=True
                    ):
                        st.session_state.current_session_id = session_id
                        st.session_state.messages = session_data["messages"].copy()
                        st.rerun()
                with col2:
                    if st.button("×", key=f"delete_{session_id}", help="Delete"):
                        del st.session_state.chat_sessions[session_id]
                        if user:
                            delete_chat_from_firestore(user['user_id'], session_id)
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
    else:
        st.caption("No chats yet")
    
    # Create container for bottom section
    bottom_container = st.container()
    
    with bottom_container:
        st.markdown("---")
        
        # Profile Section at Bottom
        if user:
            # Signed in user - show profile with sign out button by default
            col1, col2 = st.columns([1, 4])
            with col1:
                if user.get('picture'):
                    st.image(user['picture'], width=40)
                else:
                    st.markdown("👤")
            with col2:
                st.markdown(f"**{user.get('name', 'User')}**")
            
            # Sign out button always visible
            if st.button("Sign Out", key="signout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            # Not signed in - Sign in button at bottom
            auth_url = get_authorization_url()
            st.markdown(f"""
            <a href="{auth_url}" target="_self" style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                width: 100%;
                background: #f3f4f6;
                color: #1f2937;
                padding: 10px 16px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 500;
                font-size: 14px;
                border: 1px solid #e5e7eb;
                transition: all 0.2s;
            " onmouseover="this.style.background='#e5e7eb';" 
               onmouseout="this.style.background='#f3f4f6';">
                <svg width="16" height="16" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Sign in with Google
            </a>
            """, unsafe_allow_html=True)

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# File uploader
st.markdown("### 📎 Upload Files")
uploaded_files = st.file_uploader(
    "Upload PDFs, videos, or audio files for Buddy to analyze",
    type=["pdf", "mp4", "avi", "mov", "mp3", "wav", "m4a"],
    accept_multiple_files=True,
    help="Upload PDFs (100+ pages), videos (up to 2 hours), or audio files"
)

# Store uploaded files in session state and display them
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    with st.container():
        cols = st.columns(4)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 4]:
                st.success(f"✅ {file.name}")
else:
    st.session_state.uploaded_files = None

# Chat input with dynamic placeholder
if st.session_state.messages:
    placeholder_text = "Ask your Buddy a follow up..."
else:
    placeholder_text = "Ask your Buddy something..."

user_input = st.chat_input(placeholder_text)

if user_input:
    # Create a new session if none exists
    if st.session_state.current_session_id is None:
        import uuid
        new_id = str(uuid.uuid4())[:8]
        st.session_state.chat_sessions[new_id] = {
            "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "messages": [],
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.current_session_id = new_id
    
    # Add message to current session
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
    
    # Save to Firestore only if user is logged in
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
                        gemini_file = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)
                        gemini_files.append(gemini_file)
                
                # Get response from Gemini
                response = get_response(user_input, client, gemini_files)
                
                # Stream the response
                full_response = ""
                placeholder = st.empty()
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        placeholder.write(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                # Save to session
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
                
                # Save to Firestore only if user is logged in
                if user:
                    save_chat_to_firestore(
                        user['user_id'],
                        st.session_state.current_session_id,
                        st.session_state.messages,
                        st.session_state.chat_sessions[st.session_state.current_session_id]["title"]
                    )
                
                st.session_state.last_request_time = now
                
            except Exception as e:
                error_msg = f"❌ Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                # Save error to session and Firestore (only if logged in)
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
                if user:
                    save_chat_to_firestore(
                        user['user_id'],
                        st.session_state.current_session_id,
                        st.session_state.messages,
                        st.session_state.chat_sessions[st.session_state.current_session_id]["title"]
                    )