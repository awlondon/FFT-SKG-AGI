try:
    import speech_recognition as sr  # type: ignore
except Exception:
    sr = None  # type: ignore


def transcribe_speech(timeout: int = 5, phrase_time_limit: int = 5) -> str:
    """
    Capture audio from the default microphone and return recognized text.
    If speech recognition is not available an empty string is returned and
    a warning printed.
    """
    if sr is None:
        print("[STT] speech_recognition not installed; skipping transcription")
        return ""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("[STT] Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = recognizer.recognize_google(audio)
            print(f"[STT] Transcribed: {text}")
            return text
        except sr.RequestError:
            print("[STT] API unavailable, trying offline recognition")
            try:
                text = recognizer.recognize_sphinx(audio)
                print(f"[STT] Transcribed (Sphinx): {text}")
                return text
            except Exception as e:
                print(f"[STT] Offline recognition failed: {e}")
        except sr.UnknownValueError:
            print("[STT] Unable to recognize speech")
    except Exception as e:
        print(f"[STT] Error while capturing audio: {e}")
    return ""