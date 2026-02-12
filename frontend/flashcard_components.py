"""Flashcard UI components with interactive card flipping and save/load."""
from pkgutil import get_data
import streamlit as st
import uuid
import datetime

def render_flashcard_interface():
    """Render the flashcard study interface."""
    
    # Custom CSS for flashcard animations with a distinctive aesthetic
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Libre+Baskerville:wght@400;700&display=swap');
    
    .flashcard-container {
        perspective: 1000px;
        width: 100%;
        max-width: 700px;
        margin: 2rem auto;
        font-family: 'Libre Baskerville', serif;
    }
    
    .flashcard {
        position: relative;
        width: 100%;
        height: 400px;
        transition: transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1);
        transform-style: preserve-3d;
        cursor: pointer;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    }
    
    .flashcard.flipped {
        transform: rotateY(180deg);
    }
    
    .flashcard-face {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 3rem;
        box-sizing: border-box;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .flashcard-front {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .flashcard-back {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        transform: rotateY(180deg);
    }
    
    .flashcard-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.875rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        opacity: 0.8;
        margin-bottom: 1.5rem;
    }
    
    .flashcard-content {
        font-size: 1.5rem;
        line-height: 1.6;
        text-align: center;
        font-weight: 400;
    }
    
    .flashcard-hint {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 2rem;
        letter-spacing: 1px;
    }
    
    .flashcard-controls {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem auto;
        max-width: 700px;
    }
    
    .flashcard-nav-btn {
        font-family: 'Space Mono', monospace;
        padding: 0.875rem 2rem;
        border: 2px solid #667eea;
        background: white;
        color: #667eea;
        border-radius: 50px;
        font-size: 0.875rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .flashcard-nav-btn:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .flashcard-nav-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        transform: none;
    }
    
    .flashcard-progress {
        font-family: 'Space Mono', monospace;
        text-align: center;
        font-size: 1rem;
        color: #667eea;
        margin-bottom: 1rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .upload-section {
        max-width: 700px;
        margin: 2rem auto;
        padding: 3rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        font-family: 'Libre Baskerville', serif;
        font-size: 1.8rem;
        color: #2d3748;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .upload-subtitle {
        font-family: 'Space Mono', monospace;
        font-size: 0.875rem;
        color: #718096;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize flashcard state
    if 'flashcard_mode' not in st.session_state:
        st.session_state.flashcard_mode = False
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    if 'current_card_index' not in st.session_state:
        st.session_state.current_card_index = 0
    if 'card_flipped' not in st.session_state:
        st.session_state.card_flipped = False
    if 'current_flashcard_id' not in st.session_state:
        st.session_state.current_flashcard_id = None
    if 'flashcard_sets' not in st.session_state:
        st.session_state.flashcard_sets = {}
    
    # Header
    st.markdown("# Flashcard Study Mode")
    st.markdown("*Generate and study flashcards from your documents*")
    st.markdown("---")
    
    user = st.session_state.get('user')
    
    # Check if flashcards exist
    if not st.session_state.flashcards:

        

        # Upload and generate section
        st.markdown('<div class="upload-section">📚 Create Flashcards</div>', unsafe_allow_html=True)
        st.markdown('<div class="upload-subtitle">Upload files or describe a topic to generate study cards</div>', unsafe_allow_html=True)
        
        # Topic input
        topic = st.text_input(
            "What do you want to study?",
            placeholder="e.g., Python programming basics, World War II, Cell biology...",
            label_visibility="visible"
        )
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload study materials (optional)",
            type=["pdf", "mp4", "avi", "mov", "mp3", "wav", "m4a"],
            accept_multiple_files=True,
            help="Upload PDFs, videos, or audio files to generate flashcards from"
        )
        
        # Number of cards
        num_cards = st.slider(
            "Number of flashcards to generate",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Generate Flashcards", use_container_width=True, type="primary"):
                if topic or uploaded_files:
                    with st.spinner("🤖 Buddy is creating your flashcards..."):
                        # Import flashcard service
                        from backend.flashcard_service import generate_flashcards
                        from backend.gemini_service import get_gemini_client
                        import google.generativeai as genai
                        
                        client = get_gemini_client()
                        
                        # Process uploaded files for Gemini
                        gemini_files = []
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                gemini_file = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)
                                gemini_files.append(gemini_file)
                        
                        # Generate flashcards
                        flashcards = generate_flashcards(
                            topic if topic else "Study materials",
                            client,
                            gemini_files if gemini_files else None,
                            num_cards
                        )
                        
                        st.session_state.flashcards = flashcards
                        st.session_state.current_card_index = 0
                        st.session_state.card_flipped = False
                        
                        # Create new flashcard set ID
                        st.session_state.current_flashcard_id = str(uuid.uuid4())[:8]
                        
                        # Auto-save if user is logged in
                        user = st.session_state.get('user')
                        if user:
                            from backend.firebase_service import save_flashcards_to_firestore, load_user_flashcards
                            st.session_state.flashcard_sets = load_user_flashcards(user['user_id'])
                            title = topic[:50] if topic else "Flashcard Set"
                            save_flashcards_to_firestore(
                                user['user_id'],
                                st.session_state.current_flashcard_id,
                                flashcards,
                                title
                            )
                            # Add to local session
                            st.session_state.flashcard_sets[st.session_state.current_flashcard_id] = {
                                'title': title,
                                'cards': flashcards,
                                'timestamp': datetime.datetime.now()
                            }
                            st.success(f"✅ Flashcards saved!")
                        
                        st.rerun()
                else:
                    st.warning("⚠️ Please provide a topic or upload files to generate flashcards")
        
        if user and st.session_state.get('flashcard_sets'):
            st.markdown("### 📂 Your Flashcard Sets")

            for set_id, set_data in st.session_state.flashcard_sets.items():
                with st.expander(f"📖 {set_data.get('title', 'Untitled Set')}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        cards_in_set = set_data.get('cards', [])
                        st.write(f"Total cards: {len(set_data.get('cards', []))}")
                        st.caption(f"Created: {set_data.get('timestamp')}")
                    with col2:
                        # LOADING LOGIC: Clicking this loads the set into the active session
                        if st.button("Study Now", key=f"load_{set_id}", use_container_width=True):
                            st.session_state.flashcards = set_data['cards']
                            st.session_state.current_flashcard_id = set_id
                            st.session_state.current_card_index = 0
                            st.session_state.card_flipped = False
                            st.rerun()
                        
                        if st.button("Delete", key=f"del_{set_id}", use_container_width=True):
                            from backend.firebase_service import delete_flashcards_from_firestore
                            delete_flashcards_from_firestore(st.session_state.user['user_id'], set_id)
                            del st.session_state.flashcard_sets[set_id]
                            st.rerun()
                    st.markdown("---")
                            
        # Tips section
        st.markdown("---")
        st.markdown("### 💡 Study Tips")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**📖 Active Recall**")
            st.caption("Try to answer before flipping the card")
        with col2:
            st.markdown("**🔄 Spaced Repetition**")
            st.caption("Review cards multiple times over several days")
        with col3:
            st.markdown("**✍️ Self-Test**")
            st.caption("Write or speak answers before checking")
    
    else:
        # Display flashcards
        total_cards = len(st.session_state.flashcards)
        current_index = st.session_state.current_card_index
        
        if current_index < total_cards:
            current_card = st.session_state.flashcards[current_index]
            
            # Progress indicator with save button
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f'<div class="flashcard-progress">Card {current_index + 1} of {total_cards}</div>',
                    unsafe_allow_html=True
                )
            with col2:
                user = st.session_state.get('user')
                if user and st.button("💾 Save Set", key="save_flashcards", help="Save this flashcard set"):
                    from backend.firebase_service import save_flashcards_to_firestore
                    
                    # Get or create flashcard ID
                    if not st.session_state.current_flashcard_id:
                        st.session_state.current_flashcard_id = str(uuid.uuid4())[:8]
                    
                    # Generate title from first card
                    title = st.session_state.flashcards[0]['question'][:50] + "..."
                    
                    # Save to Firestore
                    save_flashcards_to_firestore(
                        user['user_id'],
                        st.session_state.current_flashcard_id,
                        st.session_state.flashcards,
                        title
                    )
                    
                    # Add to local session
                    st.session_state.flashcard_sets[st.session_state.current_flashcard_id] = {
                        'title': title,
                        'cards': st.session_state.flashcards,
                        'timestamp': datetime.datetime.now()
                    }
                    
                    st.success("✅ Flashcards saved!")
                    st.rerun()
            
            # Flashcard display
            flip_class = "flipped" if st.session_state.card_flipped else ""
            
            st.markdown(f"""
            <div class="flashcard-container">
                <div class="flashcard {flip_class}" id="flashcard">
                    <div class="flashcard-face flashcard-front">
                        <div class="flashcard-label">Question</div>
                        <div class="flashcard-content">{current_card['question']}</div>
                        <div class="flashcard-hint">Click to reveal answer</div>
                    </div>
                    <div class="flashcard-face flashcard-back">
                        <div class="flashcard-label">Answer</div>
                        <div class="flashcard-content">{current_card['answer']}</div>
                        <div class="flashcard-hint">Click to see question</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Flip button (invisible but covers the card area)
            if st.button("🔄 Flip Card", key="flip", use_container_width=True):
                st.session_state.card_flipped = not st.session_state.card_flipped
                st.rerun()
            
            # Navigation controls
            st.markdown('<div class="flashcard-controls">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button("⏮️ First", disabled=(current_index == 0), key="first"):
                    st.session_state.current_card_index = 0
                    st.session_state.card_flipped = False
                    st.rerun()
            
            with col2:
                if st.button("◀️ Previous", disabled=(current_index == 0), key="prev"):
                    st.session_state.current_card_index -= 1
                    st.session_state.card_flipped = False
                    st.rerun()
            
            with col3:
                if st.button("Next ▶️", disabled=(current_index >= total_cards - 1), key="next"):
                    st.session_state.current_card_index += 1
                    st.session_state.card_flipped = False
                    st.rerun()
            
            with col4:
                if st.button("Last ⏭️", disabled=(current_index >= total_cards - 1), key="last"):
                    st.session_state.current_card_index = total_cards - 1
                    st.session_state.card_flipped = False
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Keyboard navigation hint
            st.markdown("---")
            st.caption("💡 **Tip:** Use arrow keys on your keyboard to navigate between cards")
            
            # Reset button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Finish Review", use_container_width=True):
                    st.session_state.flashcards = []
                    st.session_state.current_card_index = 0
                    st.session_state.card_flipped = False
                    st.session_state.current_flashcard_id = None
                    st.rerun()
        
        else:
            # Completion screen
            st.success("🎉 You've reviewed all flashcards!")
            st.balloons()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Review Again", use_container_width=True):
                    st.session_state.current_card_index = 0
                    st.session_state.card_flipped = False
                    st.rerun()
                
                if st.button("📚 Create New Set", use_container_width=True):
                    st.session_state.flashcards = []
                    st.session_state.current_card_index = 0
                    st.session_state.card_flipped = False
                    st.session_state.current_flashcard_id = None
                    st.rerun()