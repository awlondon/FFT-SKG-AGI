import os
from datetime import datetime

try:
    import speech_recognition as sr  # type: ignore
except Exception:
    sr = None  # type: ignore

try:
    from fft_generator import generate_fft_from_audio
except Exception:
    generate_fft_from_audio = None  # type: ignore


def transcribe_speech(timeout: int = 5, phrase_time_limit: int = 5) -> tuple[str, str | None]:
    """
    Capture audio from the microphone, save it to ``modalities/audio_input`` and
    return a tuple ``(transcript, audio_path)``.  ``audio_path`` may be ``None``
    if recording fails.  If speech recognition is unavailable the transcript is
    an empty string and only the raw audio (if any) is returned.
    """
    if sr is None:
        print("[STT] speech_recognition not installed; skipping transcription")
        return "", None

    recognizer = sr.Recognizer()
    audio_path: str | None = None

    try:
        with sr.Microphone() as source:
            print("[STT] Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        # Save the captured audio before attempting transcription
        try:
            os.makedirs("modalities/audio_input", exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.join("modalities/audio_input", f"mic_{timestamp}.wav")
            with open(audio_path, "wb") as f:
                f.write(audio.get_wav_data())
        except Exception as e:
            print(f"[STT] Failed to save microphone audio: {e}")

        # Generate FFT data and image for the captured file
        if audio_path and generate_fft_from_audio:
            try:
                os.makedirs("modalities/fft_audio", exist_ok=True)
                os.makedirs("modalities/fft_visual", exist_ok=True)
                base = os.path.splitext(os.path.basename(audio_path))[0]
                fft_data_path = os.path.join("modalities/fft_audio", f"{base}.npy")
                fft_image_path = os.path.join("modalities/fft_visual", f"{base}.png")
                generate_fft_from_audio(audio_path, fft_data_path, fft_image_path)
            except Exception as e:
                print(f"[STT] Error generating FFT: {e}")

        # Perform transcription
        try:
            text = recognizer.recognize_google(audio)
            print(f"[STT] Transcribed: {text}")
            return text, audio_path
        except sr.RequestError:
            print("[STT] API unavailable, trying offline recognition")
            try:
                text = recognizer.recognize_sphinx(audio)
                print(f"[STT] Transcribed (Sphinx): {text}")
                return text, audio_path
            except Exception as e:
                print(f"[STT] Offline recognition failed: {e}")
        except sr.UnknownValueError:
            print("[STT] Unable to recognize speech")
    except Exception as e:
        print(f"[STT] Error while capturing audio: {e}")

    return "", audio_path
