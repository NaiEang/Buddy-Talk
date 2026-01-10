import os
from google import genai
from dotenv import load_dotenv

# 1. Load your key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialize the NEW Google Gen AI Client
# This automatically uses the correct 'v1' API version
client = genai.Client(api_key=api_key)

# 3. Use a current 2.0 or 2.5 model to avoid the 404 error
MODEL_ID = "gemini-2.0-flash" 

try:
    print(f"Connecting to {MODEL_ID}...")
    response = client.models.generate_content(
        model=MODEL_ID,
        contents="Say hello and tell me your version name."
    )
    print("\nGemini Response:")
    print(response.text)

except Exception as e:
    # If it still fails, this will tell us exactly why
    print(f"\nSomething went wrong: {e}")