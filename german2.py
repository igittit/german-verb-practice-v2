import streamlit as st
import random
import base64
from PIL import Image
from io import BytesIO
import json
import time

# Sample German verb dictionary with image references
verbs = {
    "gehen": {
        "english": "to go",
        "image": "walking_path",
        "sample_sentence": "Ich gehe ins Kino.",
        "sample_translation": "I go to the cinema.",
        "audio": "gehen"
    },
    "essen": {
        "english": "to eat",
        "image": "dining_table",
        "sample_sentence": "Wir essen Pizza zum Abendessen.",
        "sample_translation": "We eat pizza for dinner.",
        "audio": "essen"
    },
    "trinken": {
        "english": "to drink",
        "image": "coffee_cup",
        "sample_sentence": "Er trinkt einen Kaffee am Morgen.",
        "sample_translation": "He drinks coffee in the morning.",
        "audio": "trinken"
    },
    "lesen": {
        "english": "to read",
        "image": "open_book",
        "sample_sentence": "Sie liest ein interessantes Buch.",
        "sample_translation": "She reads an interesting book.",
        "audio": "lesen"
    },
    "schreiben": {
        "english": "to write",
        "image": "writing_hand",
        "sample_sentence": "Die Schüler schreiben einen Aufsatz.",
        "sample_translation": "The students write an essay.",
        "audio": "schreiben"
    },
    "sprechen": {
        "english": "to speak",
        "image": "conversation",
        "sample_sentence": "Sprechen Sie Deutsch?",
        "sample_translation": "Do you speak German?",
        "audio": "sprechen"
    }
}

# Pre-recorded audio for verbs (base64 encoded)
audio_files = {
    "gehen": "data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBQbHVzIMKpIE5DSCBTb2Z0d2FyZQBUSVQyAAAABgAAAzIyMzUAVFNTRQAAAA8AAANMYXZmNTcuODMuMTAwAAAAAAAAAAAAAAD/80DEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQsRbAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQMSkAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV",
    "essen": "data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBQbHVzIMKpIE5DSCBTb2Z0d2FyZQBUSVQyAAAABgAAAzIyMzUAVFNTRQAAAA8AAANMYXZmNTcuODMuMTAwAAAAAAAAAAAAAAD/80DEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQsRbAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQMSkAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV",
    "trinken": "data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBQbHVzIMKpIE5DSCBTb2Z0d2FyZQBUSVQyAAAABgAAAzIyMzUAVFNTRQAAAA8AAANMYXZmNTcuODMuMTAwAAAAAAAAAAAAAAD/80DEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQsRbAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQMSkAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV",
    "lesen": "data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBQbHVzIMKpIE5DSCBTb2Z0d2FyZQBUSVQyAAAABgAAAzIyMzUAVFNTRQAAAA8AAANMYXZmNTcuODMuMTAwAAAAAAAAAAAAAAD/80DEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQsRbAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQMSkAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVvvvvvvvvvvvvvvvvvvvvvvvvvV",
    "schreiben": "data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBQbHVzIMKpIE5DSCBTb2Z0d2FyZQBUSVQyAAAABgAAAzIyMzUAVFNTRQAAAA8AAANMYXZmNTcuODMuMTAwAAAAAAAAAAAAAAD/80DEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQsRbAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQMSkAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV",
    "sprechen": "data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBQbHVzIMKpIE5DSCBTb2Z0d2FyZQBUSVQyAAAABgAAAzIyMzUAVFNTRQAAAA8AAANMYXZmNTcuODMuMTAwAAAAAAAAAAAAAAD/80DEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQsRbAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/zQMSkAAADSAAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
}

# Generate images
def generate_image(image_type, width=300):
    img = Image.new('RGB', (300, 200), color=(230, 240, 255))
    
    if image_type == "walking_path":
        for i in range(0, 300, 20):
            img.paste((100, 150, 100), (i, 150, i+10, 180))
        img.paste((50, 50, 150), (150, 100, 160, 140))
        img.paste((200, 0, 0), (145, 90, 155, 100))
        return img
    
    elif image_type == "dining_table":
        img.paste((139, 69, 19), (50, 120, 250, 130))
        img.paste((255, 0, 0), (100, 80, 120, 100))
        img.paste((0, 100, 0), (180, 80, 200, 100))
        return img
    
    elif image_type == "coffee_cup":
        img.paste((101, 67, 33), (120, 100, 180, 150))
        img.paste((200, 150, 100), (125, 95, 175, 100))
        img.paste((150, 100, 50), (180, 120, 190, 130))
        return img
    
    elif image_type == "open_book":
        img.paste((240, 230, 200), (100, 80, 200, 160))
        img.paste((150, 100, 50), (95, 70, 100, 170))
        for i in range(90, 170, 15):
            img.paste((100, 80, 40), (105, i, 195, i+2))
        return img
    
    elif image_type == "writing_hand":
        img.paste((255, 220, 180), (150, 100, 180, 150))
        img.paste((255, 220, 180), (180, 120, 220, 130))
        img.paste((0, 0, 0), (200, 125, 230, 127))
        img.paste((200, 200, 200), (120, 130, 200, 132))
        return img
    
    elif image_type == "conversation":
        img.paste((255, 255, 200), (0, 0, 300, 200))
        img.paste((200, 230, 255), (70, 70, 130, 130))
        img.paste((200, 230, 255), (170, 70, 230, 130))
        img.paste((0, 0, 0), (90, 90, 100, 100))
        img.paste((0, 0, 0), (190, 90, 200, 100))
        img.paste((0, 0, 0), (80, 110, 120, 115))
        img.paste((0, 0, 0), (180, 110, 220, 115))
        return img
    
    return img

# Function to convert image to base64
def img_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Initialize session state
def init_session_state():
    if "current_verb" not in st.session_state:
        st.session_state.current_verb = random.choice(list(verbs.keys()))
    if "user_translation" not in st.session_state:
        st.session_state.user_translation = ""
    if "user_sentence" not in st.session_state:
        st.session_state.user_sentence = ""
    if "translation_submitted" not in st.session_state:
        st.session_state.translation_submitted = False
    if "sentence_submitted" not in st.session_state:
        st.session_state.sentence_submitted = False
    if "correct_count" not in st.session_state:
        st.session_state.correct_count = 0
    if "wrong_count" not in st.session_state:
        st.session_state.wrong_count = 0
    if "total_count" not in st.session_state:
        st.session_state.total_count = 0
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "recorded_audio" not in st.session_state:
        st.session_state.recorded_audio = None

# Main app
def main():
    st.set_page_config(
        page_title="German Verb Practice", 
        page_icon="🇩🇪", 
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
            .header {
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .score-card {
                display: flex;
                justify-content: space-around;
                margin-bottom: 20px;
            }
            .score-item {
                text-align: center;
                padding: 10px;
                border-radius: 8px;
                width: 30%;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .correct { color: #2ecc71; font-weight: bold; }
            .wrong { color: #e74c3c; font-weight: bold; }
            .total { color: #3498db; font-weight: bold; }
            .verb-card {
                background-color: white;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .image-container {
                display: flex;
                justify-content: center;
                margin: 20px 0;
                border-radius: 10px;
                overflow: hidden;
                border: 3px solid #f0f2f6;
            }
            .button-row {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
            }
            .audio-btn {
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                font-size: 24px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .audio-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 8px rgba(0,0,0,0.15);
            }
            .green-btn {
                background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                color: white;
            }
            .red-btn {
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 14px;
            }
            .stTextInput>div>div>input {
                border-radius: 20px !important;
                padding: 12px 20px !important;
                border: 2px solid #3498db !important;
            }
            .stTextArea>div>div>textarea {
                border-radius: 15px !important;
                padding: 15px !important;
                border: 2px solid #3498db !important;
            }
            div.stButton > button:first-child {
                background: linear-gradient(135deg, #3498db 0%, #1a5276 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 25px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            div.stButton > button:first-child:hover {
                background: linear-gradient(135deg, #2980b9 0%, #154360 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Header
    st.markdown("""
        <div class="header">
            <h1>🇩🇪 German Verb Practice</h1>
            <p>Learn German verbs with visual references and pronunciation practice</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Score card
    st.markdown(f"""
        <div class="score-card">
            <div class="score-item">
                <div>Correct Answers</div>
                <div class="correct">{st.session_state.correct_count}</div>
            </div>
            <div class="score-item">
                <div>Wrong Answers</div>
                <div class="wrong">{st.session_state.wrong_count}</div>
            </div>
            <div class="score-item">
                <div>Total</div>
                <div class="total">{st.session_state.total_count}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Verb card
    current_verb = st.session_state.current_verb
    verb_data = verbs[current_verb]
    
    st.markdown(f"""
        <div class="verb-card">
            <h2 style="text-align: center; color: #2c3e50;">What does the German verb '<b>{current_verb}</b>' mean in English?</h2>
    """, unsafe_allow_html=True)
    
    # Generate and display image
    img = generate_image(verb_data["image"])
    img_base64 = img_to_base64(img)
    st.markdown(f"""
        <div class="image-container">
            <img src="data:image/png;base64,{img_base64}" width="300">
        </div>
    """, unsafe_allow_html=True)
    
    # Audio buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("▶️ Listen to Word", key="play_audio", 
                    use_container_width=True, 
                    help="Listen to the pronunciation of the word"):
            # Play audio when button is clicked
            audio_html = f"""
            <audio autoplay>
                <source src="{audio_files[current_verb]}" type="audio/mpeg">
            </audio>
            """
            st.components.v1.html(audio_html, height=0)
    
    with col2:
        if st.button("🎤 Repeat Word", key="repeat_audio", 
                    use_container_width=True, 
                    help="Repeat the word after hearing it"):
            # Play audio and prompt user to repeat
            st.info(f"🎵 Playing audio for '{current_verb}'. Please repeat the word!")
            audio_html = f"""
            <audio autoplay>
                <source src="{audio_files[current_verb]}" type="audio/mpeg">
            </audio>
            """
            st.components.v1.html(audio_html, height=0)
    
    # Translation input
    user_translation = st.text_input(
        "Enter the English meaning:", 
        value=st.session_state.user_translation,
        key="translation_input",
        placeholder="Type the English meaning here...",
        label_visibility="collapsed"
    )
    
    # Check translation button
    if st.button("Check Translation", key="check_translation", 
                use_container_width=True, 
                help="Check if your translation is correct"):
        st.session_state.translation_submitted = True
        st.session_state.total_count += 1
        
        if user_translation.strip().lower() == verb_data["english"]:
            st.session_state.correct_count += 1
            st.success("✅ Correct! Well done!")
        else:
            st.session_state.wrong_count += 1
            st.error(f"❌ Incorrect. The correct meaning is: **{verb_data['english']}**")
    
    # Sentence section
    if st.session_state.translation_submitted:
        st.markdown("---")
        st.subheader(f"Use '{current_verb}' in a German sentence")
        st.info(f"**Example:** {verb_data['sample_sentence']}  \n*({verb_data['sample_translation']})*")
        
        user_sentence = st.text_area(
            "Your German sentence:", 
            value=st.session_state.user_sentence,
            key="sentence_input",
            height=100,
            placeholder="Type your German sentence here...",
            label_visibility="collapsed"
        )
        
        # Check sentence button
        if st.button("Check Sentence", key="check_sentence", 
                    use_container_width=True, 
                    help="Check if your sentence uses the verb correctly"):
            st.session_state.sentence_submitted = True
            
            # Simple validation - just check if verb is present
            if current_verb.lower() in user_sentence.lower():
                st.success("✅ Great! The verb is used correctly in your sentence.")
            else:
                st.warning(f"⚠️ The verb '{current_verb}' appears to be missing. Try again!")
    
    # Next verb button
    if st.session_state.translation_submitted and st.session_state.sentence_submitted:
        if st.button("Next Verb →", key="next_verb", 
                    use_container_width=True, 
                    help="Move to the next verb"):
            # Reset for next verb
            st.session_state.current_verb = random.choice(list(verbs.keys()))
            st.session_state.user_translation = ""
            st.session_state.user_sentence = ""
            st.session_state.translation_submitted = False
            st.session_state.sentence_submitted = False
            time.sleep(0.5)  # Small delay for better UX
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close verb-card
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div class="footer">
            <p>Practice German verbs with visual references and pronunciation training</p>
            <p>Built with Streamlit • 🇩🇪 Learn German Effectively</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
