import streamlit as st
import random

# Dictionary of German verbs
verbs = {
    "gehen": {"english": "to go", "sample_sentence": "Ich gehe ins Kino.", "sample_translation": "I go to the cinema."},
    "essen": {"english": "to eat", "sample_sentence": "Wir essen Pizza zum Abendessen.", "sample_translation": "We eat pizza for dinner."},
    "trinken": {"english": "to drink", "sample_sentence": "Er trinkt einen Kaffee am Morgen.", "sample_translation": "He drinks coffee in the morning."},
    "lesen": {"english": "to read", "sample_sentence": "Sie liest ein interessantes Buch.", "sample_translation": "She reads an interesting book."},
    "schreiben": {"english": "to write", "sample_sentence": "Die Schüler schreiben einen Aufsatz.", "sample_translation": "The students write an essay."},
    "verstehen": {"english": "to understand", "sample_sentence": "Verstehst du die Frage?", "sample_translation": "Do you understand the question?"},
    "sprechen": {"english": "to speak", "sample_sentence": "Sprechen Sie Deutsch?", "sample_translation": "Do you speak German?"},
    "kommen": {"english": "to come", "sample_sentence": "Wann kommst du nach Hause?", "sample_translation": "When are you coming home?"},
    "machen": {"english": "to do/make", "sample_sentence": "Was machst du am Wochenende?", "sample_translation": "What are you doing on the weekend?"},
    "sehen": {"english": "to see", "sample_sentence": "Ich sehe einen Vogel im Garten.", "sample_translation": "I see a bird in the garden."}
}

# Initialize session
if "verb" not in st.session_state:
    st.session_state.verb = random.choice(list(verbs.keys()))

verb = st.session_state.verb
verb_data = verbs[verb]

st.title("🇩🇪 German Verb Practice")
st.markdown(f"### Your verb is: **{verb}**")

# Step 1: English translation
user_translation = st.text_input("What is the English meaning of this verb?")

if user_translation:
    if user_translation.lower().strip() == verb_data["english"]:
        st.success("✅ Correct! Well done!")
    else:
        st.error(f"❌ Almost! The correct translation is: '{verb_data['english']}'")

# Step 2: Use the verb in a sentence
st.markdown(f"Now use **'{verb}'** in a German sentence.")
st.caption(f"💡 Example: _{verb_data['sample_sentence']}_ ({verb_data['sample_translation']})")
user_sentence = st.text_area("Your German sentence:")

if user_sentence:
    if verb.lower() in user_sentence.lower():
        # Basic conjugation check (simplified)
        stem = verb[:-2]
        forms = [verb, stem + "e", stem + "st", stem + "t", verb[:-1]]
        if any(f in user_sentence.lower() for f in forms):
            st.success("✅ Great job! Your sentence looks correct!")
        else:
            st.warning("⚠️ The verb is there, but the conjugation might be off.")
    else:
        st.error("❌ The verb isn't found in your sentence. Try again!")

# New verb button
if st.button("Practice another verb"):
    new_verb = random.choice([v for v in verbs if v != verb])
    st.session_state.verb = new_verb
    st.experimental_rerun()
