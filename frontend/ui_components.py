"""Frontend UI components."""
import streamlit as st
import datetime
import uuid
import textwrap
import os
import json
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

def load_css(file_path):
    """Read css file and return as markdown string."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f"<style>{f.read()}</style>"
    return ""
    
def render_auth_button():
    """Display Google Sign-In button with OAuth flow."""
    auth_url = get_authorization_url()
    
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh;">
        <div style="text-align: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #1f2937; margin-bottom: 0.5rem;">🤖 Welcome to BUDDY AI</h1>
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
    """Render sidebar with icon navigation tabs and sectioned content."""
    
    # Initialize sidebar tab
    if 'sidebar_tab' not in st.session_state:
        st.session_state.sidebar_tab = 'home'
    
    active_tab = st.session_state.sidebar_tab
    
    # --- Navigation CSS (dynamic active state) ---
    st.sidebar.markdown(f"""
    <style>
        /* ===== Disable sidebar resize handle ===== */
        [data-testid="stSidebar"] > div:first-child {{
            width: 300px !important;
        }}
        [data-testid="stSidebar"][aria-expanded="true"] {{
            min-width: 300px !important;
            max-width: 300px !important;
        }}
        [data-testid="stSidebar"] .st-emotion-cache-1gwvy71,
        [data-testid="stSidebar"] > div:nth-child(2) {{
            pointer-events: none !important;
            cursor: default !important;
        }}
        /* Reduce sidebar top padding */
        section[data-testid="stSidebar"] > div:first-child {{
            padding-top: 0 !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding-top: 0.5rem !important;
        }}
        /* Position the collapse button row */
        [data-testid="stSidebarCollapseButton"] {{
            top: 0.2rem !important;
        }}
        /* Hide the drag handle */
        [data-testid="stSidebar"] > div[style*="cursor"] {{
            display: none !important;
        }}
        [data-testid="collapsedControl"] + div {{
            pointer-events: none !important;
        }}
        /* ===== Sidebar Navigation Buttons ===== */
        .st-key-nav_home button,
        .st-key-nav_analytics button,
        .st-key-nav_persona button {{
            text-align: left !important;
            background: transparent !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            font-size: 15px !important;
            color: #9ca3af !important;
            transition: all 0.15s ease !important;
            box-shadow: none !important;
            margin-bottom: 2px !important;
        }}
        .st-key-nav_home button:hover,
        .st-key-nav_analytics button:hover,
        .st-key-nav_persona button:hover {{
            background: rgba(255, 255, 255, 0.06) !important;
            color: #e5e7eb !important;
        }}
        /* Active tab highlight */
        .st-key-nav_{active_tab} button {{
            background: rgba(99, 102, 241, 0.12) !important;
            color: #818cf8 !important;
            font-weight: 600 !important;
        }}
        .st-key-nav_{active_tab} button:hover {{
            background: rgba(99, 102, 241, 0.18) !important;
            color: #818cf8 !important;
        }}
        /* ===== New Chat Button ===== */
        .st-key-new_chat_btn button {{
            border: 1px dashed rgba(99, 102, 241, 0.4) !important;
            border-radius: 10px !important;
            color: #818cf8 !important;
            background: transparent !important;
            font-weight: 500 !important;
        }}
        .st-key-new_chat_btn button:hover {{
            background: rgba(99, 102, 241, 0.1) !important;
            border-style: solid !important;
        }}
        /* ===== Sign Out Button ===== */
        .st-key-signout button {{
            background: transparent !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
            color: #9ca3af !important;
            font-size: 13px !important;
        }}
        .st-key-signout button:hover {{
            background: rgba(239, 68, 68, 0.1) !important;
            border-color: #ef4444 !important;
            color: #ef4444 !important;
        }}
        /* ===== Pin profile section to bottom of sidebar ===== */
        [data-testid="stSidebar"] .st-key-profile_section {{
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            width: 300px !important;
            padding: 12px 24px 16px 24px !important;
            background-color: var(--secondary-background-color, #262730) !important;
            border-top: 1px solid rgba(250, 250, 250, 0.1) !important;
            z-index: 999 !important;
            box-sizing: border-box !important;
        }}
        /* Sidebar bottom padding so content doesn't hide behind profile */
        section[data-testid="stSidebar"] > div {{
            padding-bottom: 100px !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # --- Header with icon ---
    import base64 as _b64, pathlib as _pl
    _icon_data = _b64.b64encode(_pl.Path("asset/icon.png").read_bytes()).decode()
    st.sidebar.markdown(
        f'<div style="text-align: center; margin-top: -0.5rem; margin-bottom: 0.1rem; padding-top: 0;">'
        f'<img src="data:image/png;base64,{_icon_data}" style="width: 68px; height: 68px; border-radius: 12px;" />'
        f'</div>'
        f'<h2 style="margin-top: 0.15rem; margin-bottom: 0.5rem; padding-top: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: 1px; line-height: 1; text-align: center;">B<span style="color: #818cf8;">U</span>DDY AI</h2>',
        unsafe_allow_html=True,
    )
    
    # --- Navigation Tabs ---
    if st.sidebar.button("🏠  Home", key="nav_home", use_container_width=True):
        st.session_state.sidebar_tab = 'home'
        st.session_state.flashcard_mode = False
        st.rerun()
    
    if st.sidebar.button("📊  Analytics", key="nav_analytics", use_container_width=True):
        st.session_state.sidebar_tab = 'analytics'
        st.session_state.flashcard_mode = False
        st.rerun()
    
    if st.sidebar.button("🎭  Persona", key="nav_persona", use_container_width=True):
        st.session_state.sidebar_tab = 'persona'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =============================================
    # TAB CONTENT
    # =============================================
    
    if active_tab == 'home':
        # --- Home Tab: New Chat + Flashcards + Chat History ---
        if st.sidebar.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.session_state.flashcard_mode = False
            st.rerun()
        
        if st.sidebar.button("📚 Flashcards", use_container_width=True):
            st.session_state.flashcard_mode = True
            st.session_state.current_session_id = None
            st.rerun()
        
        st.sidebar.markdown("")
        st.sidebar.markdown("##### Chat History")
        
        if st.session_state.get('chat_sessions'):
            def get_sortable_timestamp(timestamp):
                """Convert various timestamp formats to a sortable value."""
                if timestamp is None:
                    return 0
                if isinstance(timestamp, str):
                    try:
                        return datetime.datetime.fromisoformat(timestamp).timestamp()
                    except Exception:
                        return 0
                if hasattr(timestamp, 'timestamp'):
                    return timestamp.timestamp()
                return 0
            
            today_chats = []
            older_chats = []
            today = datetime.datetime.now().date()
            
            for session_id, session_data in sorted(
                st.session_state.chat_sessions.items(),
                key=lambda x: get_sortable_timestamp(x[1].get("timestamp")),
                reverse=True
            ):
                timestamp = session_data.get("timestamp")
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            chat_date = datetime.datetime.fromisoformat(timestamp).date()
                        else:
                            chat_date = timestamp.date() if hasattr(timestamp, 'date') else datetime.datetime.now().date()
                    except Exception:
                        chat_date = datetime.datetime.now().date()
                else:
                    chat_date = datetime.datetime.now().date()
                
                if chat_date == today:
                    today_chats.append((session_id, session_data))
                else:
                    older_chats.append((session_id, session_data))
            
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
                            if 'flashcard_mode' in st.session_state:
                                st.session_state.flashcard_mode = False
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
                            if 'flashcard_mode' in st.session_state:
                                st.session_state.flashcard_mode = False
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
    
    elif active_tab == 'analytics':
        # --- Analytics Tab: summary shown in sidebar ---
        st.sidebar.caption("View your analytics on the main screen.")
    
    elif active_tab == 'persona':
        # --- Persona Tab: Model/Persona Selection ---
        if user:
            st.sidebar.markdown("##### 🎭 Prompt Model")
            
            all_personas = {**PERSONAS, **st.session_state.get('custom_personas', {})}
            selected = st.sidebar.selectbox(
                "Choose a persona:",
                options=list(all_personas.keys()),
                index=list(all_personas.keys()).index(st.session_state.get('selected_persona', 'Default')),
                label_visibility="collapsed"
            )
            st.session_state.selected_persona = selected
            
            # Show current persona description
            current_desc = all_personas.get(selected, "")
            preview = current_desc.strip().split('\n')[0][:80] + "..." if current_desc.strip() else ""
            if preview:
                st.sidebar.caption(preview)
            
            st.sidebar.markdown("")
            
            # Create custom persona
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
        else:
            st.sidebar.info("👤 Sign in to customize personas")
    
    # =============================================
    # PROFILE SECTION (fixed to bottom of sidebar)
    # =============================================
    with st.sidebar.container(key="profile_section"):
        if user:
            col1, col2 = st.columns([1, 4])
            with col1:
                if user.get('picture'):
                    st.image(user['picture'], width=40)
                else:
                    st.markdown("👤")
            with col2:
                st.markdown(f"**{user.get('name', 'User')}**")
            
            if st.button("Sign Out", key="signout", use_container_width=True):
                # Set flag — actual session cleanup happens at top of next rerun
                st.session_state._signing_out = True
                st.rerun()
        else:
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

def render_chat_interface():
    # CSS is loaded globally in streamlit_app.py — no duplicate loading needed
    
    # Add custom CSS to make edit buttons invisible/transparent
    # st.markdown("""
    # <style>
    #     /* Remove borders from edit buttons */
    #     button[kind="secondary"] {
    #         border: none !important;
    #         background: transparent !important;
    #         box-shadow: none !important;
    #         padding: 0px !important;
    #         height: auto !important;
    #     }
    #     button[kind="secondary"]:hover {
    #         background: rgba(0, 0, 0, 0.05) !important;
    #         border: none !important;
    #         box-shadow: none !important;
    #     }
        
    #     /* Target edit buttons by aria-label */
    #     button[aria-label*="Edit"] {
    #         border: none !important;
    #         background: transparent !important;
    #         box-shadow: none !important;
    #         padding: 0px !important;
    #         height: auto !important;
    #     }
    # </style>
    # """, unsafe_allow_html=True)

    # 1. INITIALIZE STATE FIRST (Always do this before rendering)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = None    

    # 3. TOP UPLOADER (ONLY shows when there are NO messages)
    if len(st.session_state.messages) == 0:
        st.markdown("### 📎 Upload Files")
        st.caption("Upload PDFs, videos, or audio files for Buddy to analyze")
        
        # We put the uploader INSIDE the if statement
        top_upload = st.file_uploader(
            "Initial context for your second brain",
            type=["pdf", "mp4", "avi", "mov", "mp3", "wav", "m4a"],
            accept_multiple_files=True,
            key="initial_drop_zone",
            label_visibility="collapsed"
        )
        if top_upload:
            st.session_state.uploaded_files = top_upload
            st.success(f"✅ {len(top_upload)} files selected.")
        
        st.markdown("---") # Visual divider

    # 4. DISPLAY CHAT HISTORY (The messages go here in scrollable container)
    st.markdown('<div class="messages-scroll-container">', unsafe_allow_html=True)
    
    # Find the last assistant message index to only show uploader there
    last_assistant_idx = None
    for i in range(len(st.session_state.messages) - 1, -1, -1):
        if st.session_state.messages[i]["role"] == "assistant":
            last_assistant_idx = i
            break

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(message["content"])
                
                # ── Copy button: store text in hidden div, copy via JS ──
                import html as _html
                _safe_content = _html.escape(message["content"])
                _uid = f"copytext_{idx}"
                _copy_html = (
                    f'<div id="{_uid}" style="display:none;">{_safe_content}</div>'
                    f'<button class="msg-action-btn" id="copybtn_{idx}" onclick="'
                    f"var t=document.getElementById('{_uid}').textContent;"
                    f"navigator.clipboard.writeText(t).then(function(){{"
                    f"var b=document.getElementById('copybtn_{idx}');"
                    f"b.innerHTML='&#10003; Copied';"
                    f"setTimeout(function(){{b.innerHTML='&#128203; Copy';}},1500);"
                    f"}});"
                    f'" title="Copy response">&#128203; Copy</button>'
                )
                st.markdown(_copy_html, unsafe_allow_html=True)
                
                # File uploader only below the LAST assistant response
                if idx == last_assistant_idx:
                    st.markdown("---")
                    follow_up_files = st.file_uploader(
                        "Upload files for follow-up",
                        type=["pdf", "mp4", "avi", "mov", "mp3", "wav", "m4a"],
                        accept_multiple_files=True,
                        key=f"uploader_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    if follow_up_files:
                        st.session_state.queued_files = follow_up_files
                        st.success(f"✅ {len(follow_up_files)} file(s) uploaded!")
            
            elif message["role"] == "user":
                # Check if this message is being edited
                if st.session_state.get("editing_msg_idx") == idx:
                    edited = st.text_area(
                        "Edit your message",
                        value=message["content"],
                        key=f"edit_area_{idx}",
                        label_visibility="collapsed",
                        height=100,
                    )
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("✅ Save & Resend", key=f"save_edit_{idx}", use_container_width=True):
                            # Truncate conversation: keep everything up to (not including) this message
                            st.session_state.messages = st.session_state.messages[:idx]
                            # Clear editing state and queue the edited message for processing
                            st.session_state.editing_msg_idx = None
                            st.session_state.pending_user_input = edited
                            # Update session store
                            if st.session_state.current_session_id:
                                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()
                            st.rerun()
                    with ec2:
                        if st.button("✖ Cancel", key=f"cancel_edit_{idx}", use_container_width=True):
                            st.session_state.editing_msg_idx = None
                            st.rerun()
                else:
                    st.markdown(message["content"])
                    # Edit icon — positioned to the right via CSS
                    if not st.session_state.get("is_processing"):
                        if st.button("\u270f\ufe0f", key=f"edit_btn_{idx}", help="Edit message"):
                            st.session_state.editing_msg_idx = idx
                            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. BOTTOM CHAT INPUT — returned outside containers so Streamlit pins it to the bottom
    prompt_text = "Ask Buddy something..." if not st.session_state.messages else "Ask a follow-up..."
    return st.chat_input(prompt_text)