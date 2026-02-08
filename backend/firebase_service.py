"""Firebase database service."""
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st


@st.cache_resource
def init_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        firebase_creds = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def get_db():
    """Get Firestore database client."""
    return init_firebase()


def save_user_to_firestore(user_info):
    """Save or update user in Firestore."""
    db = get_db()
    user_id = user_info.get('user_id') or user_info.get('sub')
    if user_id:
        db.collection("users").document(user_id).set(user_info, merge=True)


def save_chat_to_firestore(user_id, session_id, messages, title):
    """Save chat messages to Firestore."""
    db = get_db()
    db.collection("users").document(user_id).collection("chats").document(session_id).set({
        "messages": messages,
        "title": title,
        "timestamp": __import__('datetime').datetime.now()
    }, merge=True)


def load_user_chats(user_id):
    """Load user's chat history from Firestore."""
    db = get_db()
    try:
        chats_ref = db.collection("users").document(user_id).collection("chats")
        chats = chats_ref.order_by("timestamp", direction="DESCENDING").stream()
        return {chat.id: chat.to_dict() for chat in chats}
    except Exception as e:
        print(f"Error loading chats: {e}")
        return {}


def delete_chat_from_firestore(user_id, session_id):
    """Delete a chat from Firestore."""
    db = get_db()
    db.collection("users").document(user_id).collection("chats").document(session_id).delete()
