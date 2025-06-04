# token_audio_manager.py
import os
import subprocess
import pyttsx3
import threading
import json
import logging

class TokenAudioManager:
    def __init__(self, audio_dir="audio_tokens", tts_fallback=True, save_tts=True, voice_profile_path="sigil_voice_profiles.json", engine=None):
        self.audio_dir = audio_dir
        self.tts_fallback = tts_fallback
        self.save_tts = save_tts
        self.tts_engine = pyttsx3.init()
        self.voice_profiles = self._load_voice_profiles(voice_profile_path)
        self.engine = engine  # Initialize the engine attribute

        self.tts_engine.setProperty("rate", 160)  # Default fallback
        os.makedirs(self.audio_dir, exist_ok=True)

    def _load_voice_profiles(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"[⚠️] Failed to load voice profiles: {e}")
            return {}

    def get_audio_path(self, token):
        return os.path.join(self.audio_dir, f"{token}.wav")

    def play_token(self, token, glyph=None, ui_callback=None):
        """
        Plays or speaks the given token. If audio exists, plays it.
        If missing and tts_fallback is enabled, uses TTS (and saves if enabled).
        Glyph affects voice style if profile exists.
        """
        if self.engine is None:
            logging.error("[❌] Engine is not initialized. Cannot proceed with gate decisions.")
            if ui_callback:
                ui_callback(token, allowed=False)
            return

        path = self.get_audio_path(token)

        def run():
            # Check the "react_to_audio" gate
            if not self.engine.gate_decision("react_to_audio", token):
                logging.info(f"[🧭] Gate blocked: React to audio ({token})")
                if ui_callback:
                    ui_callback(token, allowed=False)
                return

            if os.path.exists(path):
                self._play_file(path)
                logging.info(f"[🔊] Played: {token}")
            elif self.tts_fallback:
                # Check the "speak_token" gate
                if not self.engine.gate_decision("speak_token", token):
                    logging.info(f"[🧭] Gate blocked: Speak token ({token})")
                    if ui_callback:
                        ui_callback(token, allowed=False)
                    return

                logging.info(f"[🌀] Speaking: {token}")
                self._speak_token(token, glyph=glyph, save_path=path if self.save_tts else None)
            else:
                logging.warning(f"[❌] Skipped (no audio, no fallback): {token}")

            if ui_callback:
                ui_callback(token, allowed=True)

        threading.Thread(target=run, daemon=True).start()

    def _play_file(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            logging.error(f"[ERROR] Audio playback failed: {e}")

    def _speak_token(self, token, glyph=None, save_path=None):
        try:
            if glyph and glyph in self.voice_profiles:
                profile = self.voice_profiles[glyph]
                self.tts_engine.setProperty("rate", profile.get("rate", 160))
                self.tts_engine.setProperty("pitch", profile.get("pitch", 90))  # Note: pitch is symbolic only

                # Gate-triggered voice profile shifts
                if self.engine.gate_decision("refine_voice", glyph):
                    logging.info(f"[🎙️] Refining voice for glyph: {glyph}")
                    refined_rate = profile.get("refined_rate", profile.get("rate", 160))
                    refined_pitch = profile.get("refined_pitch", profile.get("pitch", 90))
                    self.tts_engine.setProperty("rate", refined_rate)
                    self.tts_engine.setProperty("pitch", refined_pitch)
            else:
                self.tts_engine.setProperty("rate", 160)

            if save_path:
                self.tts_engine.save_to_file(token, save_path)
            else:
                self.tts_engine.say(token)

            self.tts_engine.runAndWait()
        except Exception as e:
            logging.error(f"[ERROR] TTS failed for '{token}': {e}")

    def generate_audio_for_all(self, tokens, glyph_map=None):
        """
        Generate and save audio files for all given tokens.
        """
        for token in tokens:
            path = self.get_audio_path(token)
            if not os.path.exists(path):
                glyph = glyph_map.get(token) if glyph_map else None
                self._speak_token(token, glyph=glyph, save_path=path)
                logging.info(f"[🎙️] Generated: {token}")

    def list_missing_audio(self, tokens):
        return [t for t in tokens if not os.path.exists(self.get_audio_path(t))]
