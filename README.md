# Buddy AI 🤖 — Your Instant Second Brain

Buddy AI is an advanced multimodal AI assistant powered by Google Gemini that helps you analyze and understand files like never before. Upload PDFs, videos, or audio files and get intelligent, timestamped answers with direct citations.

## 🌟 Features

- **Multimodal File Analysis**: Support for PDFs (100+ pages), videos (up to 2 hours), and audio files
- **Intelligent Responses**: Get timestamped references, direct citations, and page numbers
- **General AI Assistant**: Ask any question - coding, problem-solving, explanations, or general conversation
- **Chat Management**: Create multiple chat sessions, navigate history, and organize conversations
- **File Upload**: Drag-and-drop support for multiple files with instant analysis
- **Streaming Responses**: Real-time word-by-word responses for better user experience
- **Clean Interface**: Modern, intuitive design built with Streamlit

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free tier available)
- pip or conda for package management

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ratanaknoch/buddy_ai.git
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   # Using venv
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install streamlit google-generativeai
   ```

### Configuration

1. **Get your Google Gemini API key:**

   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Get API Key" or "Create API Key"
   - Copy the generated API key

2. **Create the secrets file:**

   Create a folder named `.streamlit` in the project directory if it doesn't exist:

   ```bash
   mkdir .streamlit
   ```

3. **Add your API key:**

   Create a file named `secrets.toml` inside the `.streamlit` folder:

   ```bash
   # On Windows
   type nul > .streamlit\secrets.toml
   
   # On macOS/Linux
   touch .streamlit/secrets.toml
   ```

   Open `.streamlit/secrets.toml` and add your API key:

   ```toml
   google_api_key = "YOUR_GOOGLE_GEMINI_API_KEY_HERE"
   ```

   Replace `YOUR_GOOGLE_GEMINI_API_KEY_HERE` with the actual API key you obtained.

### Running the Application

1. **Start the Streamlit app:**

   ```bash
   streamlit run streamlit_app_gemini.py
   ```

2. **Open your browser:**

   The app will automatically open in your default browser, typically at `http://localhost:8501`

3. **Start using Buddy AI:**

   - Type any question in the chat input
   - Upload files (PDF, video, audio) for analysis
   - Create multiple chat sessions
   - Navigate your chat history in the sidebar

## 📁 Supported File Types

- **Documents**: PDF
- **Videos**: MP4, AVI, MOV
- **Audio**: MP3, WAV, M4A

## 🛠️ Project Structure

```
demo-ai-assistant/
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # API keys (create this)
├── streamlit_app_gemini.py  # Main application
├── check_models.py          # Utility to check available models
├── README.md                # This file
└── DEVELOPMENT_REPORT.md    # Detailed development documentation
```

## 🔧 Configuration Options

You can customize the app by modifying these parameters in `streamlit_app_gemini.py`:

```python
MODEL = "gemini-2.5-flash"              # AI model to use
HISTORY_LENGTH = 5                       # Number of messages in context
MIN_TIME_BETWEEN_REQUESTS = 3           # Rate limiting (seconds)
```

## 💡 Usage Tips

1. **For PDF Analysis**: Upload your document and ask specific questions like:
   - "Summarize this document"
   - "What does page 15 say about [topic]?"
   - "Extract key points from chapter 3"

2. **For Video Analysis**: Upload your video and ask:
   - "What happens at timestamp 12:30?"
   - "Summarize the main topics discussed"
   - "Find when [specific topic] is mentioned"

3. **For Audio Analysis**: Upload audio files and ask:
   - "Transcribe this audio"
   - "What are the key points discussed?"
   - "Summarize the conversation"

4. **General Questions**: No file needed! Ask anything:
   - Coding help and debugging
   - Explanations and tutorials
   - Problem-solving assistance

## 🐛 Troubleshooting

### "API Key Error"
- Ensure your `.streamlit/secrets.toml` file exists and contains the correct API key
- Check that the key is wrapped in quotes: `google_api_key = "your-key"`

### "Quota Exceeded Error"
- Google Gemini free tier has daily limits
- Wait a few hours or upgrade to a paid plan
- Try switching to a different model in the configuration

### "Model Not Found"
- Run `check_models.py` to see available models
- Update the `MODEL` variable in `streamlit_app_gemini.py`

### "File Upload Failed"
- Check file size (large files may take longer)
- Ensure file type is supported
- Check your internet connection

### "ModuleNotFoundError: No module named 'htbuilder'"
- The `htbuilder` package is required for Streamlit styling components
- Install it using: `pip install htbuilder`
- If using a virtual environment, ensure it's activated before installing

## 📚 Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Development Report](DEVELOPMENT_REPORT.md) - Detailed feature documentation

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is developed for educational purposes.

## 👨‍💻 Author

Developed by ratanaknoch

---

**Note**: This project uses Google's Gemini API. Make sure you comply with [Google's API Terms of Service](https://ai.google.dev/terms) when using this application.