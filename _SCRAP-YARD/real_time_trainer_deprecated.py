import tkinter as tk
from tkinter import Canvas, Text
import cv2
import pyaudio
import threading
import numpy as np
from PIL import Image, ImageTk
import time
import os
from audio_streamer import AudioStreamer
from video_streamer import VideoStreamer
from live_token_mapper import TokenMapper
from glyph_ticker_overlay import GlyphTickerOverlay
from speech_output import SpeechSynth
from speech_logger import log_speech_event
from agency_engine import should_output
from prosody_logger import log_prosody
from symbolic_context_logger import log_token_context
import logging

class RealTimeTrainer:
    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("Real-Time Trainer")

        # UI Components
        self.camera_label = tk.Label(self.root)
        self.camera_label.pack()

        self.audio_canvas = Canvas(self.root, width=400, height=100, bg="black")
        self.audio_canvas.pack()

        self.text_input = Text(self.root, height=2, width=50)
        self.text_input.pack()

        self.output_canvas = Canvas(self.root, width=800, height=400, bg="white")
        self.output_canvas.pack()

        # Threads for capturing inputs
        self.stop_threads = False
        threading.Thread(target=self.capture_webcam, daemon=True).start()
        threading.Thread(target=self.capture_audio, daemon=True).start()
        threading.Thread(target=self.tokenize_inputs, daemon=True).start()

        # Update output stream
        self.update_output_stream()

        # Avatar and Speech Output
        self.audio = AudioStreamer()
        self.video = VideoStreamer()
        self.token_mapper = TokenMapper()
        self.visualizer = GlyphTickerOverlay(parent=self.root)
        self.avatar = engine.avatar_window if engine and hasattr(engine, 'avatar_window') else None
        if not self.avatar:
            logging.error("AvatarWindow instance is missing. Ensure it is initialized in main.py.")
        self.speaker = SpeechSynth()

        threading.Thread(target=self.avatar.show, daemon=True).start()

    def capture_webcam(self):
        cap = cv2.VideoCapture(0)
        while not self.stop_threads:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.camera_label.config(image=img)
                self.camera_label.image = img
                self.current_frame = frame
                self.on_frame(frame)
            self.root.update_idletasks()
        cap.release()

    def capture_audio(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        while not self.stop_threads:
            data = np.frombuffer(stream.read(1024), dtype=np.int16)
            self.audio_canvas.delete("all")
            for i in range(0, len(data), 10):
                x = i // 10
                y = 50 + (data[i] // 500)
                self.audio_canvas.create_line(x, 50, x, y, fill="green")
            self.current_audio = data
            self.root.update_idletasks()
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def tokenize_inputs(self):
        while not self.stop_threads:
            if hasattr(self, 'current_frame'):
                image_token = self.process_image(self.current_frame)
                self.process_token(image_token)
            if hasattr(self, 'current_audio'):
                audio_token = self.process_audio(self.current_audio)
                self.process_token(audio_token)
            text_token = self.text_input.get("1.0", tk.END).strip()
            if text_token:
                self.process_token(text_token)
                self.text_input.delete("1.0", tk.END)
                self.on_transcript(text_token)

    def process_image(self, frame):
        # Convert frame to a token (e.g., save as image file)
        token = f"image_{int(time.time())}.png"
        path = os.path.join(self.engine.base_dir, "tokens", token)
        Image.fromarray(frame).save(path)
        return token

    def process_audio(self, audio_data):
        # Convert audio data to a token (e.g., save as waveform file)
        token = f"audio_{int(time.time())}.wav"
        path = os.path.join(self.engine.base_dir, "tokens", token)
        with open(path, "wb") as f:
            f.write(audio_data.tobytes())
        return token

    def process_token(self, token):
        token_id = self.engine.create_token_with_thought_loop(token)
        glyph = self.engine.get_glyph_for_token(token_id)
        fft = self.engine.generate_fft_for_glyph_symbol(glyph)
        self.engine.append_to_output_stream(token_id)

        # Extract prosody features (placeholder values)
        pitch = 275  # Example pitch in Hz
        intensity = 0.85  # Example intensity (normalized)
        duration = 0.6  # Example duration in seconds

        # Log prosody and symbolic context
        log_prosody(token_id, token, pitch, intensity, duration)
        log_token_context(token_id)

    def update_output_stream(self):
        # Update the output canvas with recent glyphs and FFTs
        self.output_canvas.delete("all")
        recent_tokens = list(self.engine.input_token_ids)[-10:]  # Show last 10 tokens
        for i, token_id in enumerate(recent_tokens):
            glyph = self.engine.get_glyph_for_token(token_id)
            fft_path = os.path.join(self.engine.base_dir, "glyphs", "fft", f"{glyph}.fft.png")
            if os.path.exists(fft_path):
                img = ImageTk.PhotoImage(Image.open(fft_path))
                self.output_canvas.create_image(50 + i * 100, 200, image=img)
                self.output_canvas.image = img
        self.root.after(100, self.update_output_stream)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        self.stop_threads = True
        self.root.destroy()

    def on_transcript(self, text):
        print(f"[🗣️] {text}")
        for word in text.split():
            sigil = "🜐"  # Example sigil assignment
            token_id = self.token_mapper.process_text(word)
            self.visualizer.add_token(word, sigil, highlight=True)

            # Retrieve active glyphs and decide on output
            walked_glyphs = self.token_mapper.get_active_slots(token_id)
            if should_output(token_id, walked_glyphs):
                self.avatar.react_to_expression()
                self.speaker.speak(word, token_id)  # Save audio for the token

                # Log speech event with prosodic features
                log_speech_event(
                    token_id=token_id,
                    text=word,
                    reason="slot convergence",
                    glyphs=walked_glyphs,
                    audio_path=f"speech_audio/{token_id}.wav",
                    start_time=0.0,  # Replace with actual start time
                    end_time=1.0    # Replace with actual end time
                )
            else:
                self.avatar.react_to_silence()

    def on_frame(self, frame):
        self.token_mapper.process_frame(frame)
