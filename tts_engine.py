import os
try:
    import pyttsx3
except Exception:
    pyttsx3 = None  # type: ignore


def generate_tts(text: str, output_path: str, rate: int | None = None, voice_id: str | None = None) -> None:
    """
    Synthesize `text` to `output_path` as a WAV file using pyttsx3.  If
    pyttsx3 is unavailable this function prints a warning and returns
    without creating audio.
    """
    if pyttsx3 is None:
        print(f"[TTS] pyttsx3 not installed; cannot generate speech for '{text}'")
        return
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


def speak(text: str, rate: int | None = None, voice_id: str | None = None) -> None:
    """
    Speak `text` directly through speakers.  If pyttsx3 is unavailable a
    warning is printed instead.
    """
    if pyttsx3 is None:
        print(f"[TTS] pyttsx3 not installed; cannot speak '{text}'")
        return
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