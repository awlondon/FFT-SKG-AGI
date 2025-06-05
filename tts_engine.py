import pyttsx3

# Simple offline TTS using pyttsx3 for now

def generate_tts(text, output_path):
    """Synthesize ``text`` to ``output_path`` as a WAV file."""
    try:
        print(f"[TTS] Synthesizing audio for: '{text}' → {output_path}")
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error generating speech for '{text}': {e}")


def speak(text):
    """Speak ``text`` directly through the speakers (no file output)."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error speaking '{text}': {e}")
