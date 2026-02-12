"""Flashcard generation service using Gemini."""
import google.generativeai as genai


def generate_flashcards(content_description, client, uploaded_files=None, num_cards=10):
    """Generate flashcards from uploaded content.
    
    Args:
        content_description: User's description or topic for flashcards
        client: Gemini client instance
        uploaded_files: List of uploaded files to analyze
        num_cards: Number of flashcards to generate
    
    Returns:
        List of flashcard dictionaries with 'question' and 'answer' keys
    """
    
    prompt = f"""Based on the provided content, generate {num_cards} high-quality flashcards for studying.

IMPORTANT: Respond ONLY with valid JSON. Do not include any preamble, explanation, or markdown formatting.

Each flashcard should have:
- A clear, specific question on one side
- A comprehensive but concise answer on the other side

Return your response as a JSON array in this exact format:
[
  {{"question": "What is...", "answer": "..."}},
  {{"question": "How does...", "answer": "..."}}
]

Topic/Context: {content_description}

Generate flashcards that:
1. Cover key concepts and important details
2. Progress from fundamental to advanced topics
3. Use varied question types (what, how, why, compare, etc.)
4. Include specific examples where relevant
5. Are suitable for active recall studying

Return ONLY the JSON array, nothing else."""

    try:
        model = client.GenerativeModel("gemini-2.5-flash")
        
        # Build content parts
        content_parts = []
        
        if uploaded_files:
            for file in uploaded_files:
                content_parts.append(file)
        
        content_parts.append(prompt)
        
        # Get response
        response = model.generate_content(content_parts)
        response_text = response.text if response else "[]"
        
        # Clean up response - remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        import json
        flashcards = json.loads(response_text)
        
        # Validate format
        if not isinstance(flashcards, list):
            raise ValueError("Response is not a list")
        
        for card in flashcards:
            if not isinstance(card, dict) or 'question' not in card or 'answer' not in card:
                raise ValueError("Invalid flashcard format")
        
        # Add IDs to each flashcard
        import uuid
        import datetime
        for card in flashcards:
            card['id'] = str(uuid.uuid4())
            card['created_at'] = datetime.datetime.now().isoformat()
        
        return flashcards
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        return [{
            "question": "Error generating flashcards",
            "answer": f"Failed to parse response. Please try again. Error: {str(e)}"
        }]
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return [{
            "question": "Error generating flashcards", 
            "answer": f"An error occurred: {str(e)}"
        }]


def save_flashcard_set(user_id, flashcard_set):
    """Save a complete set of flashcards to Firestore.
    
    Args:
        user_id: The user's ID
        flashcard_set: Dictionary containing set metadata and flashcards
            {
                'set_id': str,
                'title': str,
                'flashcards': list of flashcard dicts,
                'topic': str (optional),
                'created_at': str (ISO format datetime)
            }
    """
    from backend.firebase_service import get_db
    import datetime
    
    db = get_db()
    set_id = flashcard_set.get('set_id') or str(__import__('uuid').uuid4())
    
    # Save the set metadata
    db.collection("users").document(user_id).collection("flashcard_sets").document(set_id).set({
        "set_id": set_id,
        "title": flashcard_set.get('title', 'Untitled Set'),
        "topic": flashcard_set.get('topic', ''),
        "card_count": len(flashcard_set.get('flashcards', [])),
        "created_at": flashcard_set.get('created_at', datetime.datetime.now().isoformat()),
        "updated_at": datetime.datetime.now().isoformat()
    }, merge=True)
    
    # Save individual flashcards
    for flashcard in flashcard_set.get('flashcards', []):
        card_id = flashcard.get('id') or str(__import__('uuid').uuid4())
        flashcard['set_id'] = set_id  # Link to the set
        db.collection("users").document(user_id).collection("flashcards").document(card_id).set(
            flashcard, merge=True
        )