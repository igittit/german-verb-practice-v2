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

# Function to check German sentence using OpenAI
def check_german_sentence_with_openai(client, user_sentence, target_verb, difficulty_level="beginner"):
    """Use OpenAI to evaluate the German sentence for grammar, structure, and correctness"""
    
    prompt = f"""
    As a German language teacher, please evaluate this German sentence written by a {difficulty_level} level student:

    Student's sentence: "{user_sentence}"
    Target verb to use: "{target_verb}"

    Please provide your evaluation in the following JSON format:

    {{
        "is_grammatically_correct": true/false,
        "uses_target_verb_correctly": true/false,
        "overall_score": "excellent/good/fair/needs_improvement",
        "feedback": "Detailed feedback about grammar, verb usage, and suggestions for improvement",
        "corrected_sentence": "If there are errors, provide a corrected version, otherwise repeat the original",
        "english_translation": "English translation of the student's sentence (or corrected version)"
    }}

    Be encouraging but honest in your feedback. Point out specific grammar rules if there are mistakes.
    Consider the difficulty level when evaluating - be more lenient with beginners.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an experienced German language teacher. Provide constructive, encouraging feedback while being accurate about grammar and usage. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3  # Lower temperature for more consistent evaluation
        )
        
        # Parse the JSON response
        evaluation = json.loads(response.choices[0].message.content)
        return evaluation
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing sentence evaluation: {e}")
        return None
    except Exception as e:
        st.error(f"Error evaluating sentence: {e}")
        return None

# Function to generate pronunciation audio using OpenAI TTS
def generate_audio_with_openai(client, text, language="de"):
    """Generate audio pronunciation using OpenAI's TTS API"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",  # Male voice - you can also use: echo (male), fable (male), alloy, nova, shimmer
            input=text,
            speed=0.75  # Slower speed for better learning (25% slower than normal)
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
    if "sentence_evaluation" not in st.session_state:
        st.session_state.sentence_evaluation = None
    if "show_audio_buttons" not in st.session_state:
        st.session_state.show_audio_buttons = False
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
    # New session state variables to track audio generation
    if "user_audio_generated" not in st.session_state:
        st.session_state.user_audio_generated = False
    if "corrected_audio_generated" not in st.session_state:
        st.session_state.corrected_audio_generated = False
    if "current_user_audio" not in st.session_state:
        st.session_state.current_user_audio = None
    if "current_corrected_audio" not in st.session_state:
        st.session_state.current_corrected_audio = None

# Function to reset for new verb
def reset_for_new_verb():
    """Reset session state for a new verb while preserving scores"""
    keys_to_reset = [
        'current_verb_data', 'user_translation', 'user_sentence', 
        'translation_submitted', 'sentence_submitted', 'sentence_evaluation',
        'show_audio_buttons', 'user_audio_generated', 'corrected_audio_generated',
        'current_user_audio', 'current_corrected_audio'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

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
            .evaluation-card {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                border-left: 4px solid #3498db;
            }
            .excellent { border-left-color: #2ecc71 !important; }
            .good { border-left-color: #f39c12 !important; }
            .fair { border-left-color: #e67e22 !important; }
            .needs_improvement { border-left-color: #e74c3c !important; }
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
            reset_for_new_verb()
            st.rerun()
    
    # Initialize OpenAI client
    client = get_openai_client()
    if not client:
        return
    
    # Header
    st.markdown("""
        <div class="header">
            <h1>🇩🇪 AI-Powered German Verb Practice</h1>
            <p>Learn German verbs with AI-generated content and intelligent sentence evaluation</p>
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
    
    # Update session state with current input
    st.session_state.user_translation = user_translation
    
    # Check translation button
    if st.button("Check Translation", key="check_translation", use_container_width=True):
        if user_translation.strip():
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
        else:
            st.warning("Please enter an English translation first!")
    
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
        
        # Update session state with current input
        st.session_state.user_sentence = user_sentence
        
        # Check sentence button with AI evaluation
        if st.button("🤖 Check Sentence with AI", key="check_sentence", use_container_width=True):
            if user_sentence.strip():
                st.session_state.sentence_submitted = True
                
                with st.spinner("🧠 AI is evaluating your German sentence..."):
                    evaluation = check_german_sentence_with_openai(
                        client, 
                        user_sentence, 
                        verb_data['german_verb'], 
                        st.session_state.difficulty_level
                    )
                    
                    if evaluation:
                        st.session_state.sentence_evaluation = evaluation
                        st.session_state.show_audio_buttons = True
                        
                        # Display evaluation results
                        score_class = evaluation['overall_score'].replace(' ', '_')
                        
                        st.markdown(f"""
                            <div class="evaluation-card {score_class}">
                                <h3>📝 AI Evaluation Results</h3>
                                <p><strong>Overall Score:</strong> {evaluation['overall_score'].title()}</p>
                                <p><strong>Grammar:</strong> {'✅ Correct' if evaluation['is_grammatically_correct'] else '❌ Needs improvement'}</p>
                                <p><strong>Verb Usage:</strong> {'✅ Correct' if evaluation['uses_target_verb_correctly'] else '❌ Incorrect usage'}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed feedback
                        st.markdown("### 💡 Detailed Feedback")
                        st.write(evaluation['feedback'])
                        
                        # Show corrected sentence if different
                        if evaluation['corrected_sentence'].lower() != user_sentence.lower():
                            st.markdown("### ✏️ Suggested Correction")
                            st.info(f"**Corrected:** {evaluation['corrected_sentence']}")
                        
                        # Show English translation
                        st.markdown("### 🇬🇧 English Translation")
                        st.write(f"*{evaluation['english_translation']}*")
                    else:
                        st.error("Could not evaluate the sentence. Please try again.")
            else:
                st.warning("Please enter a German sentence first!")
                        
    # Show audio buttons if evaluation is complete
    if st.session_state.sentence_evaluation and st.session_state.show_audio_buttons:
        evaluation = st.session_state.sentence_evaluation
        user_sentence = st.session_state.user_sentence
        
        st.markdown("### 🔊 Listen to Pronunciations")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔊 Hear Your Sentence", key="user_sentence_audio", use_container_width=True):
                if not st.session_state.user_audio_generated:
                    with st.spinner("Generating pronunciation..."):
                        audio_data = generate_audio_with_openai(client, user_sentence)
                        if audio_data:
                            st.session_state.current_user_audio = audio_data
                            st.session_state.user_audio_generated = True
                        else:
                            st.error("Could not generate audio for your sentence.")
                
                # Display audio if available
                if st.session_state.current_user_audio:
                    st.audio(st.session_state.current_user_audio, format='audio/mp3')
        
        with col2:
            # Always show the corrected version button, even if sentences are the same
            sentence_to_play = evaluation['corrected_sentence'] if evaluation['corrected_sentence'].lower() != user_sentence.lower() else user_sentence
            button_text = "🔊 Hear Corrected Version" if evaluation['corrected_sentence'].lower() != user_sentence.lower() else "🔊 Hear Sentence Again"
            
            if st.button(button_text, key="corrected_sentence_audio", use_container_width=True):
                if not st.session_state.corrected_audio_generated:
                    with st.spinner("Generating pronunciation..."):
                        audio_data = generate_audio_with_openai(client, sentence_to_play)
                        if audio_data:
                            st.session_state.current_corrected_audio = audio_data
                            st.session_state.corrected_audio_generated = True
                        else:
                            st.error("Could not generate audio for the corrected sentence.")
                
                # Display audio if available
                if st.session_state.current_corrected_audio:
                    st.audio(st.session_state.current_corrected_audio, format='audio/mp3')
    
    # Next verb button - show only if both translation and sentence are submitted
    if st.session_state.translation_submitted and st.session_state.sentence_submitted:
        st.markdown("---")
        if st.button("🔄 Next Verb →", key="next_verb", use_container_width=True):
            reset_for_new_verb()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close verb-card
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 14px;">
            <p>🤖 AI-Powered German verb practice with intelligent sentence evaluation</p>
            <p>Built with Streamlit • 🇩🇪 Learn German Effectively</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
