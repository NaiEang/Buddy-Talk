"""Google Gemini API service."""
import google.generativeai as genai
import streamlit as st


@st.cache_resource
def get_gemini_client():
    """Initialize and return Gemini API client."""
    api_key = st.secrets.get("google_api_key")
    genai.configure(api_key=api_key)
    return genai


def get_response(question, client, uploaded_files=None, system_instruction=None):
    """Get response from Gemini API."""
    try:
        model = client.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_instruction
        )
        
        # Build content parts
        content_parts = []
        
        if uploaded_files:
            for file in uploaded_files:
                content_parts.append(file)
        
        content_parts.append(question)
        
        # Get response
        response = model.generate_content(content_parts)
        return response.text if response else "No response generated"
    except Exception as e:
        return f"Error in Gemini API: {str(e)}"


def build_prompt(**kwargs):
    """Build a prompt with context."""
    persona = kwargs.get("persona", "helpful assistant")
    context = kwargs.get("context", "")
    question = kwargs.get("question", "")
    
    prompt = f"""You are a {persona}.
{f"Context: {context}" if context else ""}

User: {question}
Assistant:"""
    return prompt


def history_to_text(chat_history):
    """Convert chat history to text format."""
    text = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        text += f"{role}: {msg['content']}\n"
    return text
