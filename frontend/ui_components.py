"""Frontend UI components."""
import streamlit as st
import datetime
import uuid
import textwrap
from backend.auth_service import get_authorization_url


# Predefined personas - detailed descriptions from backup
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


def render_auth_button():
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


def render_sidebar(user):
    """Render sidebar with persona selection and chat history."""
    col1, col2 = st.sidebar.columns([1, 4])
    with col1:
        st.image("asset/icon.png", width=40)
    with col2:
        st.markdown("## Buddy AI")
    
    # New chat button
    if st.sidebar.button("New Chat", use_container_width=True):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.rerun()
    
    if user:
        st.sidebar.markdown("---")
        
        # Persona selection
        st.sidebar.markdown("### Persona")
        
        all_personas = {**PERSONAS, **st.session_state.get('custom_personas', {})}
        selected = st.sidebar.selectbox(
            "Choose a persona:",
            options=list(all_personas.keys()),
            index=list(all_personas.keys()).index(st.session_state.get('selected_persona', 'Default')),
            label_visibility="collapsed"
        )
        
        st.session_state.selected_persona = selected
        
        # Create custom persona - compact single input
        with st.sidebar.expander("➕ Create Custom Persona", expanded=False):
            persona_name = st.text_input("Persona Name", placeholder="e.g., Python Mentor", key="new_persona_name", label_visibility="collapsed")
            persona_instructions = st.text_area("Instructions", placeholder="e.g., You are a patient Python teacher.", height=50, key="new_persona_instructions", label_visibility="collapsed")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key="save_persona_btn", use_container_width=True):
                    if persona_name and persona_name.strip() and persona_instructions and persona_instructions.strip():
                        if persona_name not in all_personas:
                            st.session_state.custom_personas[persona_name] = persona_instructions
                            st.session_state.selected_persona = persona_name
                            st.success(f"✅ Added!")
                            st.rerun()
                        else:
                            st.error("Exists!")
                    else:
                        st.warning("Fill both!")
            
            with col2:
                if st.session_state.selected_persona in st.session_state.get('custom_personas', {}):
                    if st.button("Delete", key="delete_persona_btn", use_container_width=True):
                        del st.session_state.custom_personas[st.session_state.selected_persona]
                        st.session_state.selected_persona = 'Default'
                        st.rerun()
        
        st.sidebar.markdown("---")
    
    # Chat History
    st.sidebar.markdown("### History")
    
    if st.session_state.get('chat_sessions'):
        # Convert timestamps to comparable format for sorting
        def get_sortable_timestamp(timestamp):
            """Convert various timestamp formats to a sortable value."""
            if timestamp is None:
                return 0
            if isinstance(timestamp, str):
                try:
                    return datetime.datetime.fromisoformat(timestamp).timestamp()
                except Exception:
                    return 0
            # Firestore Timestamp object
            if hasattr(timestamp, 'timestamp'):
                return timestamp.timestamp()
            return 0
        
        # Group chats by date
        today_chats = []
        older_chats = []
        today = datetime.datetime.now().date()
        
        for session_id, session_data in sorted(
            st.session_state.chat_sessions.items(), 
            key=lambda x: get_sortable_timestamp(x[1].get("timestamp")),
            reverse=True
        ):
            # Handle both string timestamps and Firestore Timestamp objects
            timestamp = session_data.get("timestamp")
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        chat_date = datetime.datetime.fromisoformat(timestamp).date()
                    else:
                        # Firestore Timestamp object
                        chat_date = timestamp.date() if hasattr(timestamp, 'date') else datetime.datetime.now().date()
                except Exception:
                    chat_date = datetime.datetime.now().date()
            else:
                chat_date = datetime.datetime.now().date()
            
            if chat_date == today:
                today_chats.append((session_id, session_data))
            else:
                older_chats.append((session_id, session_data))
        
        # Today's chats
        if today_chats:
            st.sidebar.markdown("**Today**")
            for session_id, session_data in today_chats:
                col1, col2 = st.sidebar.columns([4, 1])
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
                            from backend.firebase_service import delete_chat_from_firestore
                            delete_chat_from_firestore(user['user_id'], session_id)
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
        
        # Older chats
        if older_chats:
            st.sidebar.markdown("**Earlier**")
            for session_id, session_data in older_chats:
                col1, col2 = st.sidebar.columns([4, 1])
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
                            from backend.firebase_service import delete_chat_from_firestore
                            delete_chat_from_firestore(user['user_id'], session_id)
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
    else:
        st.sidebar.caption("No chats yet")
    
    # Profile Section at Bottom
    st.sidebar.markdown("---")
    if user:
        col1, col2 = st.sidebar.columns([1, 4])
        with col1:
            if user.get('picture'):
                st.image(user['picture'], width=40)
            else:
                st.markdown("👤")
        with col2:
            st.markdown(f"**{user.get('name', 'User')}**")
        
        if st.sidebar.button("Sign Out", key="signout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        auth_url = get_authorization_url()
        st.sidebar.markdown(f"""
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


def render_chat_interface():
    """Render the chat interface."""
    # Initialize messages list
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
    
    # Store uploaded files in session state
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
    
    return st.chat_input(placeholder_text)
