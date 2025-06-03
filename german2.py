import random

# Dictionary of German verbs with their English meanings and sample sentences
verbs = {
    "gehen": {
        "english": "to go",
        "sample_sentence": "Ich gehe ins Kino.",
        "sample_translation": "I go to the cinema."
    },
    "essen": {
        "english": "to eat",
        "sample_sentence": "Wir essen Pizza zum Abendessen.",
        "sample_translation": "We eat pizza for dinner."
    },
    "trinken": {
        "english": "to drink",
        "sample_sentence": "Er trinkt einen Kaffee am Morgen.",
        "sample_translation": "He drinks coffee in the morning."
    },
    "lesen": {
        "english": "to read",
        "sample_sentence": "Sie liest ein interessantes Buch.",
        "sample_translation": "She reads an interesting book."
    },
    "schreiben": {
        "english": "to write",
        "sample_sentence": "Die Schüler schreiben einen Aufsatz.",
        "sample_translation": "The students write an essay."
    },
    "verstehen": {
        "english": "to understand",
        "sample_sentence": "Verstehst du die Frage?",
        "sample_translation": "Do you understand the question?"
    },
    "sprechen": {
        "english": "to speak",
        "sample_sentence": "Sprechen Sie Deutsch?",
        "sample_translation": "Do you speak German?"
    },
    "kommen": {
        "english": "to come",
        "sample_sentence": "Wann kommst du nach Hause?",
        "sample_translation": "When are you coming home?"
    },
    "machen": {
        "english": "to do/make",
        "sample_sentence": "Was machst du am Wochenende?",
        "sample_translation": "What are you doing on the weekend?"
    },
    "sehen": {
        "english": "to see",
        "sample_sentence": "Ich sehe einen Vogel im Garten.",
        "sample_translation": "I see a bird in the garden."
    }
}

def practice_verb():
    # Select a random verb
    german_verb, verb_data = random.choice(list(verbs.items()))
    
    print(f"\nGerman verb: {german_verb}")
    
    # Ask for English meaning
    user_translation = input("What is the English meaning of this verb? ").strip().lower()
    
    # Check translation
    correct_translation = verb_data["english"]
    translation_correct = user_translation == correct_translation
    
    if translation_correct:
        print("✅ Correct! Well done!")
    else:
        print(f"❌ Almost! The correct translation is: '{correct_translation}'")
    
    # Ask for sentence usage
    print(f"\nNow use '{german_verb}' in a German sentence.")
    print(f"Example: {verb_data['sample_sentence']} ({verb_data['sample_translation']})")
    user_sentence = input("Your sentence: ").strip()
    
    # Basic check if verb is in the sentence
    if german_verb.lower() in user_sentence.lower():
        # Check for basic conjugation (very simple check)
        verb_forms = [
            german_verb,  # infinitive
            german_verb[:-2] + "e",  # ich form for regular -en verbs
            german_verb[:-2] + "st",  # du form
            german_verb[:-2] + "t",   # er/sie/es form
            german_verb[:-1]          # wir/sie/Sie form (remove -n)
        ]
        
        # Check if any form of the verb appears in the sentence
        if any(form in user_sentence.lower() for form in verb_forms):
            print("✅ Great job! Your sentence looks correct!")
            print(f"Example usage: {verb_data['sample_sentence']}")
        else:
            print("⚠️ Your sentence contains the verb, but the conjugation might be off.")
            print(f"Example conjugation: {verb_data['sample_sentence']}")
    else:
        print("❌ The verb doesn't appear in your sentence. Try again!")
        print(f"Remember to use '{german_verb}' in your sentence.")
        print(f"Example: {verb_data['sample_sentence']}")

def main():
    print("German Verb Practice")
    print("--------------------")
    print("For each verb, you'll need to:")
    print("1. Provide the English meaning")
    print("2. Use it in a German sentence\n")
    
    while True:
        practice_verb()
        
        continue_practice = input("\nPractice another verb? (y/n): ").strip().lower()
        if continue_practice != 'y':
            print("\nVielen Dank und bis zum nächsten Mal!")
            break

if __name__ == "__main__":
    main()
