# Add these imports at the top of your file
import time
import json

def enhanced_pronunciation_practice_section(client, target_sentence, difficulty_level):
    """Enhanced pronunciation practice with multiple recording options"""
    
    st.markdown("---")
    st.markdown("### 🎤 Pronunciation Practice")
    
    # Show target sentence prominently
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 15px 0;
    ">
        <h3 style="margin: 0 0 10px 0;">🎯 Practice Saying:</h3>
        <h2 style="margin: 0; font-family: Georgia, serif;">{target_sentence}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Play target audio if available
    if st.session_state.get('current_corrected_audio'):
        st.markdown("**🔊 Listen first:**")
        st.audio(st.session_state.current_corrected_audio, format='audio/mp3')
    
    # Recording options tabs
    tab1, tab2 = st.tabs(["📱 Quick Record", "💻 Desktop Recording"])
    
    with tab1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <strong>📱 Mobile Users:</strong> The file uploader below will open your device's recorder automatically!
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_audio = st.file_uploader(
            "🎙️ Tap to Record Your Pronunciation",
            type=['wav', 'mp3', 'm4a', 'ogg', 'flac', 'aac', '3gp', 'webm'],
            help="On mobile: Tap to record directly! On desktop: Upload a pre-recorded file.",
            key="pronunciation_upload"
        )
    
    with tab2:
        st.markdown("**For desktop users, try these quick recording options:**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🌐 Online Recorders:**
            - [Vocaroo](https://vocaroo.com) - Simple & fast
            - [Online Voice Recorder](https://online-voice-recorder.com)
            - [Rev Voice Recorder](https://www.rev.com/onlinevoicerecorder)
            """)
        
        with col2:
            st.markdown("""
            **💻 Desktop Apps:**
            - **Windows:** Voice Recorder app
            - **Mac:** QuickTime Player → New Audio Recording
            - **Any OS:** Audacity (free download)
            """)
        
        # Also show file uploader in desktop tab
        uploaded_audio_desktop = st.file_uploader(
            "Upload your recorded file:",
            type=['wav', 'mp3', 'm4a', 'ogg', 'flac'],
            key="desktop_pronunciation_upload"
        )
        
        # Use whichever upload was used
        if uploaded_audio_desktop:
            uploaded_audio = uploaded_audio_desktop
    
    # Process uploaded audio
    if uploaded_audio is not None:
        return process_pronunciation_audio(client, uploaded_audio, target_sentence, difficulty_level)
    
    return None

def process_pronunciation_audio(client, uploaded_audio, target_sentence, difficulty_level):
    """Process the uploaded pronunciation audio"""
    
    st.success("✅ Audio uploaded successfully!")
    
    # Show file info
    file_size_mb = len(uploaded_audio.getvalue()) / (1024 * 1024)
    st.caption(f"📄 {uploaded_audio.name} • {file_size_mb:.1f} MB • {uploaded_audio.type}")
    
    # Audio player
    st.markdown("**🎧 Your recording:**")
    st.audio(uploaded_audio)
    
    # Analysis section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analyze_button = st.button(
            "🤖 Analyze My Pronunciation", 
            key="analyze_pronunciation_btn", 
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.button("🔄 Record Again", key="record_again_btn", use_container_width=True):
            st.rerun()
    
    if analyze_button:
        return analyze_pronunciation_with_progress(client, uploaded_audio, target_sentence, difficulty_level)
    
    return None

def analyze_pronunciation_with_progress(client, uploaded_audio, target_sentence, difficulty_level):
    """Analyze pronunciation with progress indicators"""
    
    # Create progress tracking
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Transcribe audio
            status_text.text("🎧 Listening to your pronunciation...")
            progress_bar.progress(25)
            
            transcription = transcribe_audio_with_whisper(client, uploaded_audio)
            
            if not transcription:
                st.error("❌ Could not understand the audio. Please try recording again with clearer speech.")
                return None
            
            # Step 2: Show transcription
            status_text.text("📝 Processing what you said...")
            progress_bar.progress(50)
            
            st.markdown("### 📝 What the AI heard:")
            st.info(f'"{transcription}"')
            
            # Step 3: Analyze pronunciation
            status_text.text("🧠 Analyzing pronunciation accuracy...")
            progress_bar.progress(75)
            
            analysis = analyze_pronunciation_with_openai(
                client, target_sentence, transcription, difficulty_level
            )
            
            if not analysis:
                st.error("❌ Could not analyze pronunciation. Please try again.")
                return None
            
            # Step 4: Show results
            status_text.text("✅ Analysis complete!")
            progress_bar.progress(100)
            
            # Clear progress indicators
            time.sleep(1)
            progress_container.empty()
            
            # Display results
            display_pronunciation_results(analysis, target_sentence, transcription)
            
            return analysis
            
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
            progress_container.empty()
            return None

def transcribe_audio_with_whisper(client, uploaded_audio):
    """Transcribe audio using OpenAI Whisper"""
    try:
        # Reset file pointer to beginning
        uploaded_audio.seek(0)
        
        # Create the transcription
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=uploaded_audio,
            response_format="text"
        )
        
        return transcription.strip() if transcription else None
        
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def analyze_pronunciation_with_openai(client, target_sentence, transcription, difficulty_level):
    """Analyze pronunciation using OpenAI"""
    try:
        prompt = f"""
        Analyze this pronunciation attempt:
        
        Target sentence: "{target_sentence}"
        What the user said: "{transcription}"
        Difficulty level: {difficulty_level}
        
        Please provide a JSON response with:
        - pronunciation_score: "excellent", "good", "fair", or "needs_improvement"
        - accuracy_percentage: number from 0-100
        - words_correct: list of words pronounced correctly
        - words_incorrect: list of words that need improvement
        - overall_feedback: encouraging feedback message
        - specific_feedback: detailed analysis
        - suggestions: specific tips for improvement
        
        Be encouraging and constructive in your feedback.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # Parse the JSON response
        analysis_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                # If no JSON found, create a basic response
                return create_basic_analysis(target_sentence, transcription)
                
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic response
            return create_basic_analysis(target_sentence, transcription)
            
    except Exception as e:
        st.error(f"Error analyzing pronunciation: {str(e)}")
        return None

def create_basic_analysis(target_sentence, transcription):
    """Create a basic analysis when AI analysis fails"""
    target_words = target_sentence.lower().split()
    user_words = transcription.lower().split()
    
    # Simple word matching
    correct_words = []
    incorrect_words = []
    
    for word in target_words:
        if word in user_words:
            correct_words.append(word)
        else:
            incorrect_words.append(word)
    
    accuracy = int((len(correct_words) / len(target_words)) * 100) if target_words else 0
    
    if accuracy >= 90:
        score = "excellent"
    elif accuracy >= 75:
        score = "good"
    elif accuracy >= 50:
        score = "fair"
    else:
        score = "needs_improvement"
    
    return {
        "pronunciation_score": score,
        "accuracy_percentage": accuracy,
        "words_correct": correct_words,
        "words_incorrect": incorrect_words,
        "overall_feedback": f"You got {accuracy}% of the words right! Keep practicing!",
        "specific_feedback": "Basic word matching analysis performed.",
        "suggestions": "Try to speak more clearly and match the target sentence closely."
    }

def display_pronunciation_results(analysis, target_sentence, user_transcription):
    """Display pronunciation analysis results in an attractive format"""
    
    # Main score display
    score_colors = {
        'excellent': '#2ecc71',
        'good': '#f39c12', 
        'fair': '#e67e22',
        'needs_improvement': '#e74c3c'
    }
    
    score = analysis['pronunciation_score']
    color = score_colors.get(score, '#3498db')
    accuracy = analysis.get('accuracy_percentage', 'N/A')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0 0 10px 0; font-size: 2.5em;">
            {'🎉' if score == 'excellent' else '👏' if score == 'good' else '💪' if score == 'fair' else '🎯'}
        </h1>
        <h2 style="margin: 0 0 10px 0;">{score.replace('_', ' ').title()}</h2>
        <p style="margin: 0; font-size: 1.2em; opacity: 0.9;">
            Accuracy: {accuracy}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sentence comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Target Sentence")
        st.info(target_sentence)
    
    with col2:
        st.markdown("#### 🗣️ What You Said")
        st.info(user_transcription)
    
    # Word-by-word analysis
    if analysis.get('words_correct') or analysis.get('words_incorrect'):
        st.markdown("### 📊 Word Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if analysis.get('words_correct'):
                st.markdown("**✅ Pronounced Well:**")
                for word in analysis['words_correct'][:5]:  # Limit to 5 words
                    st.markdown(f"<span style='background: #d5edda; color: #155724; padding: 4px 8px; border-radius: 12px; margin: 2px; display: inline-block;'>{word}</span>", unsafe_allow_html=True)
        
        with col2:
            if analysis.get('words_incorrect'):
                st.markdown("**🎯 Practice These:**")
                for word in analysis['words_incorrect'][:5]:  # Limit to 5 words
                    st.markdown(f"<span style='background: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 12px; margin: 2px; display: inline-block;'>{word}</span>", unsafe_allow_html=True)
    
    # Feedback sections
    if analysis.get('overall_feedback'):
        st.markdown("### 💬 Feedback")
        st.success(analysis['overall_feedback'])
    
    # Expandable detailed sections
    col1, col2 = st.columns(2)
    
    with col1:
        if analysis.get('specific_feedback'):
            with st.expander("🔍 Detailed Analysis"):
                st.write(analysis['specific_feedback'])
    
    with col2:
        if analysis.get('suggestions'):
            with st.expander("💡 Practice Tips"):
                st.write(analysis['suggestions'])
    
    # Action buttons
    st.markdown("### What's Next?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Try Again", key="try_pronunciation_again", use_container_width=True):
            # Reset pronunciation state
            for key in ['pronunciation_analysis', 'show_recording_interface']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("➡️ Next Verb", key="next_verb_from_pronunciation", use_container_width=True):
            reset_for_new_verb()
            st.rerun()
    
    with col3:
        if st.button("📚 More Practice", key="more_practice", use_container_width=True):
            st.balloons()
            st.success("Keep up the great work! 🌟")

def reset_for_new_verb():
    """Reset session state for a new verb"""
    keys_to_reset = [
        'current_verb', 'current_correction', 'current_corrected_audio',
        'pronunciation_analysis', 'show_recording_interface', 'pronunciation_mode',
        'target_pronunciation_sentence'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
