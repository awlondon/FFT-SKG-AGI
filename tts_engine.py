import pyttsx3

# Simple offline TTS using pyttsx3 for now
def generate_tts(text, output_path):
    try:
        print(f"[TTS] Synthesizing audio for: '{text}' → {output_path}")
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error generating speech for '{text}': {e}")
