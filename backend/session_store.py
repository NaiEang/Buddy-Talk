"""Server-side session store for persisting user sessions across page refreshes."""
import streamlit as st


@st.cache_resource
def get_session_store():
    """Persistent session store that survives page refreshes."""
    return {}
