# Copyright 2025 Snowflake Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from htbuilder.units import rem
from htbuilder import div, styles
from collections import namedtuple
import datetime
import textwrap
import time

import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="BUDDY AI", 
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

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

INSTRUCTIONS = textwrap.dedent("""
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
""")

SUGGESTIONS = {
    ":blue[:material/description:] Summarize this document": (
        "Please provide a comprehensive summary of the uploaded document, including key points and main themes."
    ),
    ":green[:material/video_library:] Find specific moment in video": (
        "Help me find the part in the video where [topic] is discussed. Provide timestamps."
    ),
    ":violet[:material/search:] Search for specific information": (
        "Search through the uploaded file for information about [topic] and provide direct quotes with page numbers or timestamps."
    ),
    ":red[:material/analytics:] Analyze and compare": (
        "Analyze the main arguments presented and compare different perspectives mentioned in the content."
    ),
}


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
    
    prompt = build_prompt(
        instructions=INSTRUCTIONS,
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

# Initialize chat history storage
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Sidebar - Chat Management
with st.sidebar:
    st.markdown("### 💬 Chat Management")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        import uuid
        new_id = str(uuid.uuid4())[:8]
        st.session_state.chat_sessions[new_id] = {
            "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "messages": [],
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.current_session_id = new_id
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Chat History
    st.markdown("### 📚 History")
    
    if st.session_state.chat_sessions:
        for session_id, session_data in sorted(
            st.session_state.chat_sessions.items(), 
            key=lambda x: x[1]["timestamp"], 
            reverse=True
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(
                    f"🗨️ {session_data['title']}", 
                    key=f"session_{session_id}",
                    use_container_width=True
                ):
                    st.session_state.current_session_id = session_id
                    st.session_state.messages = session_data["messages"].copy()
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{session_id}", help="Delete chat"):
                    del st.session_state.chat_sessions[session_id]
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.caption("No chat history yet")
    
    st.divider()
    st.markdown("""
    **About this assistant:**
    - Powered by Google Gemini
    - Builded on Streamlit
    """)

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
                st.session_state.last_request_time = now
                
            except Exception as e:
                error_msg = f"❌ Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                # Save error to session
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages.copy()