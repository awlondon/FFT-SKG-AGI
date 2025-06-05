import os
import pyttsx3

def generate_tts(text, output_path, rate=None, voice_id=None):
    """Synthesize `text` to `output_path` as a WAV file."""
    try:
        print(f"[TTS] Synthesizing audio for: '{text}' → {output_path}")
        engine = pyttsx3.init()

        # Set speech rate
        rate = rate or int(os.getenv("TTS_RATE", "160"))
        engine.setProperty("rate", rate)

        # Set voice if specified
        voice_id = voice_id or os.getenv("TTS_VOICE")
        if voice_id:
            for voice in engine.getProperty("voices"):
                if voice.id == voice_id:
                    engine.setProperty("voice", voice.id)
                    break

        engine.save_to_file(text, output_path)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error generating speech for '{text}': {e}")

def speak(text, rate=None, voice_id=None):
    """Speak `text` directly through speakers."""
    try:
        engine = pyttsx3.init()
        rate = rate or int(os.getenv("TTS_RATE", "160"))
        engine.setProperty("rate", rate)

        voice_id = voice_id or os.getenv("TTS_VOICE")
        if voice_id:
            for voice in engine.getProperty("voices"):
                if voice.id == voice_id:
                    engine.setProperty("voice", voice.id)
                    break

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error speaking '{text}': {e}")
