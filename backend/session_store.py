"""Server-side session store for persisting user sessions across page refreshes.

How it works:
- A cached dict maps session tokens (UUIDs) to user data.
- @st.cache_resource ensures the dict persists across reruns/refreshes.
- The token is passed via st.query_params so it survives page refreshes.
- On login: generate token -> store user -> set query param -> rerun.
- On refresh: read token from query param -> look up user in store.
- On sign-out: delete token from store -> clear query param -> rerun.
"""
import streamlit as st
import uuid


@st.cache_resource
def _get_store():
    """Internal persistent dict. Survives reruns and page refreshes."""
    return {}


def create_session(user: dict) -> str:
    """Store user data and return a new session token."""
    token = str(uuid.uuid4())
    _get_store()[token] = user
    return token


def get_session(token: str) -> dict | None:
    """Look up user data by session token. Returns None if invalid/expired."""
    return _get_store().get(token)


def delete_session(token: str):
    """Remove a session token from the store."""
    _get_store().pop(token, None)
