import speech_recognition as sr


def transcribe_speech(timeout=5, phrase_time_limit=5):
    """Capture audio from the default microphone and return recognized text."""
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
