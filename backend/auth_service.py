"""Google OAuth authentication service."""
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as auth_requests
import streamlit as st


GOOGLE_CLIENT_ID = None
GOOGLE_CLIENT_SECRET = None
REDIRECT_URI = "http://localhost:8501"


def init_google_oauth():
    """Initialize Google OAuth configuration."""
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    GOOGLE_CLIENT_ID = st.secrets.get("google_oauth_client_id")
    GOOGLE_CLIENT_SECRET = st.secrets.get("google_oauth_client_secret")


def get_authorization_url():
    """Get Google OAuth authorization URL."""
    if GOOGLE_CLIENT_ID is None:
        init_google_oauth()
    
    return (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"response_type=code&"
        f"scope=openid+profile+email&"
        f"redirect_uri={REDIRECT_URI}&"
        f"state=state"
    )


def exchange_code_for_token(code):
    """Exchange authorization code for access token."""
    if GOOGLE_CLIENT_ID is None:
        init_google_oauth()
    
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    
    response = requests.post(token_url, data=payload)
    return response.json()


def verify_google_token(id_token_str):
    """Verify Google ID token and extract user info."""
    if GOOGLE_CLIENT_ID is None:
        init_google_oauth()
    
    try:
        user_info = id_token.verify_oauth2_token(
            id_token_str,
            auth_requests.Request(),
            clock_skew_in_seconds=300,
        )
        # Verify the token audience matches our client ID
        if user_info.get('aud') != GOOGLE_CLIENT_ID:
            raise ValueError('Token audience does not match client ID')
        
        return user_info
    except Exception as e:
        print(f"Token verification error: {e}")
        return None
