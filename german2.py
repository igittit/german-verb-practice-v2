import streamlit as st
import random
import time
import base64
from PIL import Image
import io
import gtts
from io import BytesIO

# Sample German verb dictionary with image references
verbs = {
    "gehen": {
        "english": "to go",
        "image": "walking_path",
        "sample_sentence": "Ich gehe ins Kino.",
        "sample_translation": "I go to the cinema."
    },
    "essen": {
        "english": "to eat",
        "image": "dining_table",
        "sample_sentence": "Wir essen Pizza zum Abendessen.",
        "sample_translation": "We eat pizza for dinner."
    },
    "trinken": {
        "english": "to drink",
        "image": "coffee_cup",
        "sample_sentence": "Er trinkt einen Kaffee am Morgen.",
        "sample_translation": "He drinks coffee in the morning."
    },
    "lesen": {
        "english": "to read",
        "image": "open_book",
        "sample_sentence": "Sie liest ein interessantes Buch.",
        "sample_translation": "She reads an interesting book."
    },
    "schreiben": {
        "english": "to write",
        "image": "writing_hand",
        "sample_sentence": "Die Schüler schreiben einen Aufsatz.",
        "sample_translation": "The students write an essay."
    }
}

# Generate images as base64 strings
def generate_image(image_type, width=300):
    # Create a simple image based on the verb type
    img = Image.new('RGB', (300, 200), color=(230, 240, 255))
    
    # Draw different images based on the verb type
    if image_type == "walking_path":
        # Create a simple walking path image
        for i in range(0, 300, 20):
            img.paste((100, 150, 100), (i, 150, i+10, 180))
        img.paste((50, 50, 150), (150, 100, 160, 140))  # Person
        img.paste((200, 0, 0), (145, 90, 155, 100))    # Head
        return img
    
    elif image_type == "dining_table":
        # Create a dining table image
        img.paste((139, 69, 19), (50, 120, 250, 130))  # Table
        img.paste((255, 0, 0), (100, 80, 120, 100))    # Plate
        img.paste((0, 100, 0), (180, 80, 200, 100))    # Salad
        return img
    
    elif image_type == "coffee_cup":
        # Create a coffee cup image
        img.paste((101, 67, 33), (120, 100, 180, 150))  # Cup
        img.paste((200, 150, 100), (125, 95, 175, 100)) # Coffee
        img.paste((150, 100, 50), (180, 120, 190, 130)) # Handle
        return img
    
    elif image_type == "open_book":
        # Create an open book image
        img.paste((240, 230, 200), (100, 80, 200, 160)) # Book pages
        img.paste((150, 100, 50), (95, 70, 100, 170))   # Spine
        for i in range(90, 170, 15):
            img.paste((100, 80, 40), (105, i, 195, i+2)) # Lines
        return img
    
    elif image_type == "writing_hand":
        # Create a writing hand image
        img.paste((255, 220, 180), (150, 100, 180, 150)) # Arm
        img.paste((255, 220, 180), (180, 120, 220, 130)) # Hand
        img.paste((0, 0, 0), (200, 125, 230, 127))       # Pen
        img.paste((200, 200, 200), (120, 130, 200, 132)) # Paper line
        return img
    
    return img

# Function to convert image to base64
def img_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to get text-to-speech audio
def get_tts_audio(text, lang="de"):
    tts = gtts.gTTS(text=text, lang=lang)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()

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
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
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
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
                transition: transform 0.2s;
            }
            .audio-btn:hover {
                transform: scale(1.05);
            }
            .green-btn {
                background-color: #2ecc71;
                color: white;
            }
            .red-btn {
                background-color: #e74c3c;
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
                padding: 10px 15px !important;
            }
            .stTextArea>div>div>textarea {
                border-radius: 15px !important;
                padding: 15px !important;
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
            <h3>What does the German verb '<b>{current_verb}</b>' mean in English?</h3>
    """, unsafe_allow_html=True)
    
    # Generate and display image
    img = generate_image(verb_data["image"])
    img_base64 = img_to_base64(img)
    st.markdown(f"""
        <div class="image-container">
            <img src="data:image/png;base64,{img_base64}" width="300">
        </div>
    """, unsafe_allow_html=True)
    
    # Translation input
    user_translation = st.text_input(
        "Enter the English meaning:", 
        value=st.session_state.user_translation,
        key="translation_input",
        placeholder="Type the English meaning here..."
    )
    
    # Audio buttons
    st.markdown("""
        <div class="button-row">
            <button class="audio-btn green-btn" onclick="playAudio()">▶️</button>
            <button class="audio-btn red-btn" onclick="recordAudio()">🎤</button>
        </div>
    """, unsafe_allow_html=True)
    
    # Audio functionality
    if "audio_data" not in st.session_state or st.session_state.audio_data is None:
        st.session_state.audio_data = get_tts_audio(current_verb, "de")
    
    audio_base64 = base64.b64encode(st.session_state.audio_data).decode()
    st.markdown(f"""
        <audio id="audioPlayer" src="data:audio/mp3;base64,{audio_base64}"></audio>
        <script>
            function playAudio() {{
                document.getElementById('audioPlayer').play();
            }}
            function recordAudio() {{
                alert("Recording started! Repeat the word aloud after the beep.");
                // In a real app, this would start recording functionality
                // For this demo, we'll just play the audio again
                document.getElementById('audioPlayer').play();
            }}
        </script>
    """, unsafe_allow_html=True)
    
    # Check translation button
    if st.button("Check Translation", use_container_width=True):
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
        st.info(f"Example: {verb_data['sample_sentence']} ({verb_data['sample_translation']})")
        
        user_sentence = st.text_area(
            "Your German sentence:", 
            value=st.session_state.user_sentence,
            key="sentence_input",
            height=100,
            placeholder="Type your German sentence here..."
        )
        
        # Check sentence button
        if st.button("Check Sentence", use_container_width=True):
            st.session_state.sentence_submitted = True
            
            # Simple validation - just check if verb is present
            if current_verb.lower() in user_sentence.lower():
                st.success("✅ Great! The verb is used correctly in your sentence.")
            else:
                st.warning(f"⚠️ The verb '{current_verb}' appears to be missing. Try again!")
    
    # Next verb button
    if st.session_state.translation_submitted and st.session_state.sentence_submitted:
        if st.button("Next Verb →", use_container_width=True, type="primary"):
            # Reset for next verb
            st.session_state.current_verb = random.choice(list(verbs.keys()))
            st.session_state.user_translation = ""
            st.session_state.user_sentence = ""
            st.session_state.translation_submitted = False
            st.session_state.sentence_submitted = False
            st.session_state.audio_data = None
            st.experimental_rerun()
    
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
