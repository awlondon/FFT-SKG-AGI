# emergent_token_stream.py
import tkinter as tk
import os
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

import pyttsx3
from pydub import AudioSegment
from pydub.playback import play

class EmergentTokenStream(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.text_widget = tk.Text(self, height=10, bg="black", fg="white",
                                   font=("Consolas", 10), wrap="word", cursor="arrow")
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.configure(state="disabled")

        # TTS engine (optional)
        self.tts_engine = pyttsx3.init()

        # Bind tag click globally
        self.text_widget.tag_bind("clickable", "<Button-1>", self.on_token_click)

        # Track token positions
        self.token_positions = {}  # tag_name -> token_text

        # Playback queue
        self.is_playing = False

    def add_token(self, token_id, metadata=None):
        """Add a token by reading its text, and make it interactive."""
        try:
            token_file = os.path.join("tokens", f"{token_id}.txt")
            with open(token_file, "r", encoding="utf-8") as f:
                token_text = f.read().strip()

            display_text = f"[C] {token_text}\n"

            if metadata:
                display_text = f"[🧠 w={metadata.get('weight', 1.0)}, slot={metadata.get('slot', '∅')}] {token_text}\n"

            self.text_widget.configure(state="normal")

            # Insert the token and tag it
            start_index = self.text_widget.index("end-1c")
            self.text_widget.insert("end", display_text)
            end_index = self.text_widget.index("end-1c")

            tag_name = f"token_{token_id}"
            self.text_widget.tag_add(tag_name, start_index, end_index)
            self.text_widget.tag_config(tag_name, foreground="#66ffcc", underline=True)
            self.text_widget.tag_bind(tag_name, "<Enter>", lambda e: self.text_widget.config(cursor="hand2"))
            self.text_widget.tag_bind(tag_name, "<Leave>", lambda e: self.text_widget.config(cursor="arrow"))
            self.text_widget.tag_bind(tag_name, "<Button-1>", lambda e, text=token_text: self.play_audio_or_speak(text))

            # Update token positions
            self.token_positions[tag_name] = token_text

            self.text_widget.configure(state="disabled")
            self.text_widget.see("end")
        except FileNotFoundError:
            logging.error(f"Token file not found: {token_file}")
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", f"[Error] Token {token_id} not found.\n", "error")
            self.text_widget.tag_config("error", foreground="red")
            self.text_widget.configure(state="disabled")
        except Exception as e:
            logging.error(f"Error reading token file: {e}", exc_info=True)

    def on_token_click(self, event):
        index = self.text_widget.index(f"@{event.x},{event.y}")
        tags = self.text_widget.tag_names(index)
        for tag in tags:
            if tag.startswith("token_"):
                token_text = self.token_positions.get(tag, None)
                if token_text:
                    self.play_audio_or_speak(token_text)
                break

    def play_audio_or_speak(self, token_text):
        """Play audio for a token or use TTS as a fallback."""
        if self.is_playing:
            logging.info("Playback in progress. Ignoring new request.")
            return

        self.is_playing = True
        audio_path = os.path.join("audio_tokens", f"{token_text}.mp3")
        if os.path.exists(audio_path):
            try:
                audio = AudioSegment.from_file(audio_path)
                play(audio)
                logging.info(f"Playing: {audio_path}")
            except Exception as e:
                logging.error(f"Audio playback failed: {e}")
                self.speak_token_text(token_text)
        else:
            logging.warning(f"No audio found for token: {token_text}")
            self.speak_token_text(token_text)
        self.is_playing = False

    def speak_token_text(self, token_text):
        """Speak the token text using TTS."""
        self.tts_engine.say(token_text)
        self.tts_engine.runAndWait()

    def update_loop(self):
        """Update the UI loop with animations or other periodic tasks."""
        try:
            # Example: Fade tokens over time (not implemented yet)
            pass
        except Exception as e:
            logging.error("Error in update_loop:", exc_info=True)
        finally:
            self.after(100, self.update_loop)
