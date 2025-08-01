import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("🎙️ Say something...")
    audio = r.listen(source, timeout=5, phrase_time_limit=5)
    print("✅ Got audio!")

    try:
        print("You said:", r.recognize_google(audio))
    except Exception as e:
        print("❌ Recognition error:", e)
