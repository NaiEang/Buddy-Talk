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