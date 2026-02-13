# Buddy AI 🤖 — Your Instant Second Brain

Buddy AI is an advanced multimodal AI assistant powered by Google Gemini that helps you analyze and understand files like never before. Upload PDFs, videos, or audio files and get intelligent, timestamped answers with direct citations.

**Works instantly without login!** Optionally sign in with Google to save and sync your chat history across sessions.

## 🌟 Features

- **🚀 No Login Required**: Start chatting immediately — authentication is optional
- **🔐 Google Authentication**: Sign in to save your chat history across sessions
- **💾 Auto-Save Chat History**: Conversations automatically saved to Firebase Firestore when signed in
- **☁️ Cloud Sync**: Access your chat history from anywhere
- **🎭 Persona System**: Switch between Default, Academic, Friendly, and Personal Therapist personas — or create your own
- **📝 Smart Chat Titles**: Chat titles auto-generated from your first message
- **📎 Multimodal File Analysis**: Support for PDFs (100+ pages), videos (up to 2 hours), and audio files
- **🤖 Intelligent Responses**: Get timestamped references, direct citations, and page numbers
- **💬 General AI Assistant**: Ask any question — coding, problem-solving, explanations, or general conversation
- **📂 Chat Management**: Create multiple chat sessions, navigate history, and organize conversations
- **📤 File Upload**: Drag-and-drop support for multiple files with instant analysis
- **🎨 Clean Interface**: Modern, intuitive design built with Streamlit

## 🚀 Getting Started


### Prerequisites

- **Python 3.11** (recommended; Python 3.14 is not supported)
- Google Gemini API key (free tier available)
- Google Cloud Console account (for OAuth)
- Firebase project (for database)
- pip for package management

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/NaiEang/Buddy-Talk
   cd Buddy-Talk
   ```


2. **Create a virtual environment (recommended):**

   ```bash
   # Using Python 3.11
   py -3.11 -m venv .venv
   
   # Activate on Windows
   .venv\Scripts\activate
   
   # Activate on macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

#### 1. Get your Google Gemini API key:

- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Sign in with your Google account
- Click "Get API Key" or "Create API Key"
- Copy the generated API key

#### 2. Set up Google OAuth (for Authentication):

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select existing one
- Enable Google+ API
- Go to "APIs & Services" → "Credentials"
- Create OAuth 2.0 Client ID (Web application)
- Add authorized redirect URI: `http://localhost:8501`
- Copy the **Client ID** and **Client Secret**

#### 3. Set up Firebase (for Database):

- Go to [Firebase Console](https://console.firebase.google.com/)
- Create a new project
- Enable Firestore Database (start in test mode)
- Go to Project Settings → Service Accounts
- Generate new private key (downloads a JSON file)
- Keep this JSON file safe

#### 4. Configure secrets file:

Create `.streamlit/secrets.toml` with all your credentials:

```toml
# Gemini API Key
google_api_key = "YOUR_GEMINI_API_KEY"

# Google OAuth Credentials
google_oauth_client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
google_oauth_client_secret = "YOUR_CLIENT_SECRET"

# Firebase Service Account Credentials
[firebase_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

> **Note**: Copy the contents from your Firebase JSON file for the `firebase_credentials` section.

### Running the Application

1. **Activate your virtual environment (Important!):**


   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

2. **Start the Streamlit app:**

   ```bash
   streamlit run streamlit_app.py
   ```

   The app will start on `http://localhost:8501`

3. **Start chatting right away:**

   - No sign-in required — just type and chat!
   - Optionally click "Sign in with Google" to save your history
   - Upload files (PDF, video, audio) for analysis
   - Switch personas from the sidebar
   - Create multiple chat sessions

## 🔐 Authentication & Data Storage

**How it works:**
- **Google OAuth 2.0**: Secure authentication using your Google account
- **Firebase Firestore**: Cloud database storing user data and chat history
- **Auto-save**: Every message is automatically saved
- **Persistent**: Your chats are available across sessions and devices

**Database Structure:**
```
Firestore:
└── users/
    └── {user_id}/
        ├── email
        ├── name
        ├── picture
        ├── last_login
        └── chats/
            └── {chat_id}/
                ├── title
                ├── messages[]
                ├── created_at
                └── updated_at
```

## 📁 Supported File Types

- **Documents**: PDF
- **Videos**: MP4, AVI, MOV
- **Audio**: MP3, WAV, M4A

## 🛠️ Project Structure

```
Buddy-Talk/
├── .streamlit/
│   └── secrets.toml                 # API keys and credentials (create this)
├── asset/
│   └── icon.png                     # App icon/logo
├── backend/
│   ├── __init__.py
│   ├── auth_service.py              # Google OAuth 2.0 authentication
│   ├── firebase_service.py          # Firestore database operations
│   ├── gemini_service.py            # Google Gemini API integration
│   └── ...
├── frontend/
│   ├── __init__.py
│   ├── ui_components.py             # Sidebar, chat UI, personas
│   └── ...
├── test/                            # Backup/test files
├── streamlit_app.py                 # Main application entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🔧 Technologies Used

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.5 Flash
- **Authentication**: Google OAuth 2.0 (optional)
- **Database**: Firebase Firestore
- **Architecture**: Modular (backend/frontend separation)
- **Language**: Python 3.11 (recommended)
- **Key Libraries**: 
  - `streamlit` - Web framework
   - `google-generativeai` - Gemini API (see note below)
## ⚠️ Compatibility Note

**Python 3.14 is not supported by Streamlit and some dependencies. Use Python 3.11 for best compatibility.**

If you see errors related to threading, semaphores, or `watchdog`, downgrade your Python version to 3.11 and recreate your virtual environment.

### "ModuleNotFoundError: No module named 'google.generativeai'"
- **Solution**: Install the package with:
   ```bash
   pip install google-generativeai
   ```
   > **Note:** You may see a warning that support for `google-generativeai` is ending. For future compatibility, consider migrating to `google-genai` and updating your code accordingly.
  - `firebase-admin` - Firebase integration
  - `google-auth` - OAuth authentication

## 🔧 Configuration Options

You can customize the app by modifying these parameters:

```python
# streamlit_app.py
MIN_TIME_BETWEEN_REQUESTS = 3           # Rate limiting (seconds)
generate_chat_title(max_length=20)      # Chat title length

# backend/gemini_service.py
MODEL = "gemini-2.5-flash"              # AI model to use
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

### "ModuleNotFoundError: No module named 'firebase_admin'"
- **Solution**: Activate your virtual environment first:
  ```bash
  # Windows
  .\venv\Scripts\activate
  
  # Then run Streamlit
  streamlit run streamlit_app.py
  ```

### "Token verification failed: Token used too early"
- **Cause**: Clock skew between your computer and Google's servers
- **Solution**: The app includes 10-second tolerance, but you can also:
  - Windows: Settings → Time & Language → Date & Time → Sync now
  - The app will automatically handle minor time differences

### "Authentication failed" or redirects to login page
- Check that your Google OAuth redirect URI is set to: `http://localhost:8501`
- Ensure you're accessing the app on port 8501 (not 8502 or other ports)
- Verify your Client ID and Client Secret in `.streamlit/secrets.toml`

### "API Key Error"
- Ensure your `.streamlit/secrets.toml` file exists and contains the correct API key
- Check that the key is wrapped in quotes: `google_api_key = "your-key"`
- Verify the file is in the `.streamlit` folder at the project root

### "Quota Exceeded Error"
- Google Gemini free tier has daily limits
- Wait a few hours or upgrade to a paid plan
- Try switching to a different model in the configuration

### "Firebase permission denied"
- Ensure Firestore Database is enabled in Firebase Console
- Check that your Firebase service account credentials are correct
- Verify Firestore security rules allow read/write (test mode for development)

### "File Upload Failed"
- Check file size (large files may take longer)
- Ensure file type is supported (PDF, MP4, AVI, MOV, MP3, WAV, M4A)
- Check your internet connection
- Large files are uploaded to Gemini's servers, which may take time

### Port Already in Use
- If port 8501 is occupied:
  ```bash
  # Kill existing Streamlit processes
  taskkill /F /IM streamlit.exe  # Windows
  pkill -f streamlit             # macOS/Linux
  
  # Or specify a different port
  streamlit run streamlit_app.py --server.port=8502
  ```
  - Remember to update OAuth redirect URI if you change the port!

## 🚀 Deployment

### Deploy to Streamlit Community Cloud

1. Push your code to GitHub (exclude `.streamlit/secrets.toml`)
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Add secrets in the Streamlit Cloud dashboard:
   - Copy contents from your local `.streamlit/secrets.toml`
   - Paste into Streamlit Cloud secrets section
5. Update Google OAuth redirect URI to include your deployment URL:
   - Add: `https://your-app-name.streamlit.app`
6. Deploy!

**Important**: Never commit `.streamlit/secrets.toml` to GitHub!

## 🔒 Security Notes

- ✅ Never share or commit your `secrets.toml` file
- ✅ Keep your Firebase service account credentials private
- ✅ Use test mode for Firestore only during development
- ✅ Update Firestore security rules for production:
  ```javascript
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      match /users/{userId}/{document=**} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
  }
  ```

## 📚 Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)