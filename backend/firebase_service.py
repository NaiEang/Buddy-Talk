"""Firebase database service - WITH DEBUGGING."""
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import datetime

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


def save_flashcards_to_firestore(user_id, session_id, flashcards, title):
    """Save flashcard set to Firestore - WITH DEBUG OUTPUT."""
    db = get_db()
    try:
        # DEBUG: Print what we're saving
        print("=" * 60)
        print(f"🔍 DEBUG: Saving flashcards to Firestore")
        print(f"  📍 User ID: {user_id}")
        print(f"  📍 Session ID: {session_id}")
        print(f"  📍 Title: {title}")
        print(f"  📍 Flashcards type: {type(flashcards)}")
        print(f"  📍 Number of cards: {len(flashcards) if isinstance(flashcards, list) else 'NOT A LIST!'}")
        
        if isinstance(flashcards, list) and len(flashcards) > 0:
            print(f"  📍 First card preview: {flashcards[0]}")
            print(f"  📍 All cards valid: {all('question' in c and 'answer' in c for c in flashcards)}")
        else:
            print(f"  ⚠️  WARNING: flashcards is not a valid list!")
            print(f"  ⚠️  Actual value: {flashcards}")
        
        flashcard_ref = db.collection("users").document(user_id).collection("flashcards").document(session_id)
        
        # Create the document data
        flashcard_data = {
            'title': title,
            'cards': flashcards,  # This MUST be the full list of dictionaries
            'card_count': len(flashcards) if isinstance(flashcards, list) else 0,
            'updated_at': datetime.datetime.now(),
            'created_at': datetime.datetime.now()
        }
        
        print(f"  📍 Document structure: {list(flashcard_data.keys())}")
        print(f"  📍 Saving to path: users/{user_id}/flashcards/{session_id}")
        
        # Save to Firestore
        flashcard_ref.set(flashcard_data, merge=True)
        
        print(f"  ✅     successful!")
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR saving flashcards: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def load_user_flashcards(user_id):
    """Load all flashcard sets for a user from Firestore - WITH DEBUG OUTPUT."""
    db = get_db()
    try:
        print(f"🔍 Loading flashcards for user: {user_id}")
        
        flashcards_ref = db.collection("users").document(user_id).collection("flashcards")
        flashcard_sets = flashcards_ref.order_by("updated_at", direction=firestore.Query.DESCENDING).stream()
        
        user_flashcards = {}
        for flashcard_set in flashcard_sets:
            flashcard_data = flashcard_set.to_dict()
            
            # DEBUG: Check what we loaded
            print(f"  📍 Loaded flashcard set: {flashcard_set.id}")
            print(f"     Title: {flashcard_data.get('title', 'NO TITLE')}")
            print(f"     Cards type: {type(flashcard_data.get('cards'))}")
            print(f"     Cards count: {len(flashcard_data.get('cards', []))}")
            
            user_flashcards[flashcard_set.id] = {
                'title': flashcard_data.get('title', 'Untitled Flashcards'),
                'cards': flashcard_data.get('cards', []),  # This should be the full list
                'timestamp': flashcard_data.get('updated_at', __import__('datetime').datetime.now())
            }
        
        print(f"  ✅ Loaded {len(user_flashcards)} flashcard sets")
        return user_flashcards
        
    except Exception as e:
        print(f"❌ Error loading flashcards: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def delete_flashcards_from_firestore(user_id, session_id):
    """Delete a flashcard set from Firestore."""
    db = get_db()
    try:
        print(f"🗑️  Deleting flashcard set: {session_id}")
        db.collection("users").document(user_id).collection("flashcards").document(session_id).delete()
        print(f"  ✅ Deleted successfully")
        return True
    except Exception as e:
        print(f"❌ Error deleting flashcards: {str(e)}")
        return False