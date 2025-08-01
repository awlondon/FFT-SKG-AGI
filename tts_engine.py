import os
import threading

try:
    import pyttsx3
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None  # type: ignore


_tts_lock = threading.Lock()


def generate_tts(text: str, output_path: str, rate: int | None = None, voice_id: str | None = None) -> None:
    """Synthesize ``text`` to ``output_path`` using pyttsx3."""
    if pyttsx3 is None:
        print(f"[TTS] pyttsx3 not installed; cannot generate speech for '{text}'")
        return
    try:
        print(f"[TTS] Synthesizing audio for: '{text}' -> {output_path}")
        engine = pyttsx3.init()
        rate = rate or int(os.getenv("TTS_RATE", "160"))
        engine.setProperty("rate", rate)
        voice_id = voice_id or os.getenv("TTS_VOICE")
        if voice_id:
            for voice in engine.getProperty("voices"):
                if voice.id == voice_id:
                    engine.setProperty("voice", voice.id)
                    break
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    except Exception as e:  # pragma: no cover - runtime guard
        print(f"[TTS] Error generating speech for '{text}': {e}")


def speak(text: str, rate: int | None = None, voice_id: str | None = None) -> None:
    """Speak ``text`` synchronously using pyttsx3."""
    if pyttsx3 is None:
        print(f"[TTS] pyttsx3 not installed; cannot speak '{text}'")
        return
    with _tts_lock:
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
        except Exception as e:  # pragma: no cover - runtime guard
            print(f"[TTS] Error speaking '{text}': {e}")
