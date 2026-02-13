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
        flashcard_ref = db.collection("users").document(user_id).collection("flashcards").document(session_id)
    
        # Create the document data
        flashcard_data = {
            'title': title,
            'cards': flashcards,  # This MUST be the full list of dictionaries
            'card_count': len(flashcards) if isinstance(flashcards, list) else 0,
            'updated_at': datetime.datetime.now(),
            'created_at': datetime.datetime.now()
        }
    
        # Save to Firestore
        flashcard_ref.set(flashcard_data, merge=True)
        
        print(f"  Success!")
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"ERROR saving flashcards: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def load_user_flashcards(user_id):
    """Load all flashcard sets for a user from Firestore - WITH DEBUG OUTPUT."""
    db = get_db()
    try:
        
        flashcards_ref = db.collection("users").document(user_id).collection("flashcards")
        flashcard_sets = flashcards_ref.order_by("updated_at", direction=firestore.Query.DESCENDING).stream()
        
        user_flashcards = {}
        for flashcard_set in flashcard_sets:
            flashcard_data = flashcard_set.to_dict()
            
            user_flashcards[flashcard_set.id] = {
                'title': flashcard_data.get('title', 'Untitled Flashcards'),
                'cards': flashcard_data.get('cards', []),
                'timestamp': flashcard_data.get('updated_at', __import__('datetime').datetime.now())
            }
        
        return user_flashcards
        
    except Exception as e:
        print(f"Error loading flashcards: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def delete_flashcards_from_firestore(user_id, session_id):
    """Delete a flashcard set from Firestore."""
    db = get_db()
    try:
        db.collection("users").document(user_id).collection("flashcards").document(session_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting flashcards: {str(e)}")
        return False
    
def save_persona_to_firestore(user_id, persona_name, persona_instructions):
    db = get_db()
    try:        
        persona_ref = db.collection("users").document(user_id).collection("personas").document(persona_name)
        persona_data = {
            'name': persona_name,
            'instructions': persona_instructions,
            'created_at': __import__('datetime').datetime.now(),
            'updated_at': __import__('datetime').datetime.now()
        }
        
        persona_ref.set(persona_data, merge=True)
        return True
        
    except Exception as e:
        print(f"Error saving persona: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def load_user_personas(user_id):
    """Load all custom personas for a user from Firestore.
    
    Args:
        user_id: User's unique ID
    
    Returns:
        dict: Dictionary of {persona_name: persona_instructions}
    """
    db = get_db()
    try:
        print(f"Loading personas for user {user_id}")
        
        personas_ref = db.collection("users").document(user_id).collection("personas")
        personas = personas_ref.stream()
        
        user_personas = {}
        for persona in personas:
            persona_data = persona.to_dict()
            persona_name = persona_data.get('name', persona.id)
            persona_instructions = persona_data.get('instructions', '')
            user_personas[persona_name] = persona_instructions

        return user_personas
        
    except Exception as e:
        print(f"Error loading personas: {str(e)}")
        return {}


def delete_persona_from_firestore(user_id, persona_name):
    """Delete a custom persona from Firestore."""
    db = get_db()
    try:
        db.collection("users").document(user_id).collection("personas").document(persona_name).delete()
        return True
        
    except Exception as e:
        print(f"Error deleting persona: {str(e)}")
        return False


def update_persona_in_firestore(user_id, persona_name, persona_instructions):
    """Update an existing persona in Firestore."""
    db = get_db()
    try:
        print(f"Updating persona '{persona_name}' for user {user_id}")
        
        persona_ref = db.collection("users").document(user_id).collection("personas").document(persona_name)
        persona_ref.update({
            'instructions': persona_instructions,
            'updated_at': __import__('datetime').datetime.now()
        })

        return True
        
    except Exception as e:
        print(f"Error updating persona: {str(e)}")
        return save_persona_to_firestore(user_id, persona_name, persona_instructions)