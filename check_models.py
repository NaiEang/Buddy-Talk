import google.generativeai as genai
import streamlit as st

# Load API key from secrets
api_key = st.secrets.get("google_api_key")
genai.configure(api_key=api_key)

print("Available models:")
print("-" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print("-" * 50)
