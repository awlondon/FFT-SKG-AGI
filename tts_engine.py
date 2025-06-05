try:
    import pyttsx3
except Exception:
    pyttsx3 = None

# Simple offline TTS using pyttsx3 for now
def generate_tts(text, output_path):
    if not pyttsx3:
        print("[TTS] pyttsx3 not available. Skipping TTS generation.")
        return
    try:
        print(f"[TTS] Synthesizing audio for: '{text}' → {output_path}")
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error generating speech for '{text}': {e}")
