import streamlit as st
import random
import base64
from PIL import Image
from io import BytesIO
import json
import time
import openai
from openai import OpenAI
import requests

# OpenAI Configuration
def get_openai_client():
    try:
        # Try to get API key from Streamlit secrets first
        api_key = st.secrets.get("OPENAI_API_KEY", None)
        if not api_key:
            # Fallback to user input if not in secrets
            api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
            if not api_key:
                st.error("Please provide your OpenAI API key to use this app.")
                st.stop()
        
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {e}")
        return None

# Function to generate German verb data using OpenAI
def generate_verb_with_openai(client, difficulty_level="beginner"):
    """Generate a German verb with translations, example sentences, and image description using OpenAI"""
    
    prompt = f"""
    Generate a random German verb suitable for {difficulty_level} level learners. 
    Provide the response in the following JSON format:

    {{
        "german_verb": "the German verb",
        "english_translation": "the English translation (include 'to' for infinitive)",
        "sample_sentence_german": "a simple German sentence using this verb",
        "sample_sentence_english": "English translation of the German sentence",
        "verb_category": "category like 'movement', 'daily_activities', 'communication', etc."
    }}

    Make sure the verb is commonly used and appropriate for language learning.
    Keep sentences simple and practical.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a German language teacher creating educational content. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Parse the JSON response
        verb_data = json.loads(response.choices[0].message.content)
        return verb_data
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing OpenAI response: {e}")
        return None
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None

# Function to generate pronunciation audio using OpenAI TTS
def generate_audio_with_openai(client, text, language="de"):
    """Generate audio pronunciation using OpenAI's TTS API"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # You can use: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            speed=0.9  # Slightly slower for learning
        )
        
        # Convert to base64 for embedding in HTML
        audio_data = response.content
        audio_base64 = base64.b64encode(audio_data).decode()
        return f"data:audio/mpeg;base64,{audio_base64}"
        
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

# Initialize session state
def init_session_state():
    if "current_verb_data" not in st.session_state:
        st.session_state.current_verb_data = None
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
    if "difficulty_level" not in st.session_state:
        st.session_state.difficulty_level = "beginner"
    if "loading" not in st.session_state:
        st.session_state.loading = False

# Main app
def main():
    st.set_page_config(
        page_title="AI-Powered German Verb Practice", 
        page_icon="🇩🇪", 
        layout="centered",
        initial_sidebar_state="expanded"
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
            .loading {
                text-align: center;
                color: #3498db;
                font-size: 18px;
                margin: 20px 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Difficulty level selection
        difficulty = st.selectbox(
            "Select Difficulty Level:",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(st.session_state.difficulty_level)
        )
        st.session_state.difficulty_level = difficulty
        
        st.markdown("---")
        st.markdown("### 🔑 API Setup")
        st.markdown("You need an OpenAI API key to use this app.")
        st.markdown("[Get your API key here](https://platform.openai.com/api-keys)")
        
        if st.button("🔄 Generate New Verb", use_container_width=True):
            st.session_state.current_verb_data = None
            st.session_state.translation_submitted = False
            st.session_state.sentence_submitted = False
            st.session_state.user_translation = ""
            st.session_state.user_sentence = ""
    
    # Initialize OpenAI client
    client = get_openai_client()
    if not client:
        return
    
    # Header
    st.markdown("""
        <div class="header">
            <h1>🇩🇪 AI-Powered German Verb Practice</h1>
            <p>Learn German verbs with AI-generated content and pronunciation</p>
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
    
    # Generate verb data if not exists
    if st.session_state.current_verb_data is None:
        with st.spinner("🤖 Generating new German verb with AI..."):
            verb_data = generate_verb_with_openai(client, st.session_state.difficulty_level)
            if verb_data:
                st.session_state.current_verb_data = verb_data
            else:
                st.error("Failed to generate verb data. Please try again.")
                return
    
    verb_data = st.session_state.current_verb_data
    
    # Verb card
    st.markdown(f"""
        <div class="verb-card">
            <h2 style="text-align: center; color: #2c3e50;">What does the German verb '<b>{verb_data['german_verb']}</b>' mean in English?</h2>
            <p style="text-align: center; color: #7f8c8d;">Category: {verb_data.get('verb_category', 'General')}</p>
    """, unsafe_allow_html=True)
    
    # Audio buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔊 Listen to Pronunciation", key="play_audio", use_container_width=True):
            with st.spinner("Generating pronunciation..."):
                audio_data = generate_audio_with_openai(client, verb_data['german_verb'])
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
                else:
                    st.error("Could not generate audio pronunciation.")
    
    with col2:
        if st.button("🗣️ Listen to Sentence", key="sentence_audio", use_container_width=True):
            with st.spinner("Generating sentence pronunciation..."):
                audio_data = generate_audio_with_openai(client, verb_data['sample_sentence_german'])
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
                else:
                    st.error("Could not generate sentence audio.")
    
    # Translation input
    user_translation = st.text_input(
        "Enter the English meaning:", 
        value=st.session_state.user_translation,
        key="translation_input",
        placeholder="Type the English meaning here...",
        label_visibility="collapsed"
    )
    
    # Check translation button
    if st.button("Check Translation", key="check_translation", use_container_width=True):
        st.session_state.translation_submitted = True
        st.session_state.total_count += 1
        
        # More flexible matching
        correct_answer = verb_data["english_translation"].lower().strip()
        user_answer = user_translation.lower().strip()
        
        # Check for partial matches (remove "to" for comparison)
        correct_clean = correct_answer.replace("to ", "").strip()
        user_clean = user_answer.replace("to ", "").strip()
        
        if user_clean == correct_clean or user_answer == correct_answer:
            st.session_state.correct_count += 1
            st.success("✅ Correct! Well done!")
        else:
            st.session_state.wrong_count += 1
            st.error(f"❌ Incorrect. The correct meaning is: **{verb_data['english_translation']}**")
    
    # Sentence section
    if st.session_state.translation_submitted:
        st.markdown("---")
        st.subheader(f"Use '{verb_data['german_verb']}' in a German sentence")
        st.info(f"**Example:** {verb_data['sample_sentence_german']}  \n*({verb_data['sample_sentence_english']})*")
        
        user_sentence = st.text_area(
            "Your German sentence:", 
            value=st.session_state.user_sentence,
            key="sentence_input",
            height=100,
            placeholder="Type your German sentence here...",
            label_visibility="collapsed"
        )
        
        # Check sentence button
        if st.button("Check Sentence", key="check_sentence", use_container_width=True):
            st.session_state.sentence_submitted = True
            
            # Simple validation - check if verb is present
            if verb_data['german_verb'].lower() in user_sentence.lower():
                st.success("✅ Great! The verb is used correctly in your sentence.")
                
                # Optional: Generate pronunciation for user's sentence
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("🔊 Hear Your Sentence", key="user_sentence_audio"):
                        with st.spinner("Generating pronunciation..."):
                            audio_data = generate_audio_with_openai(client, user_sentence)
                            if audio_data:
                                st.audio(audio_data, format='audio/mp3')
            else:
                st.warning(f"⚠️ The verb '{verb_data['german_verb']}' appears to be missing. Try again!")
    
    # Next verb button
    if st.session_state.translation_submitted and st.session_state.sentence_submitted:
        if st.button("Next Verb →", key="next_verb", use_container_width=True):
            # Reset for next verb
            st.session_state.current_verb_data = None
            st.session_state.user_translation = ""
            st.session_state.user_sentence = ""
            st.session_state.translation_submitted = False
            st.session_state.sentence_submitted = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close verb-card
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 14px;">
            <p>🤖 AI-Powered German verb practice with OpenAI integration</p>
            <p>Built with Streamlit • 🇩🇪 Learn German Effectively</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
