
import os
import json
import tkinter as tk
from tkinter import ttk
import subprocess
import platform
from phrase_fft_utils import load_fft_images_for_phrase

class PhraseLogViewer:
    def __init__(self, parent_frame, phrase_log_path="phrase_candidates.jsonl", phrase_audio_dir="phrase_audio"):
        self.frame = tk.Frame(parent_frame, bg="black")
        self.phrase_log_path = phrase_log_path
        self.phrase_audio_dir = phrase_audio_dir
        self.entries = []

        title = tk.Label(self.frame, text="Phrase Memory", fg="white", bg="black", font=("Consolas", 12, "bold"))
        title.pack(anchor="w", padx=8, pady=(6, 2))

        self.canvas = tk.Canvas(self.frame, bg="black", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="black")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.frame.pack(fill="both", expand=True)

        self.load_phrases()

    def load_phrases(self):
        if not os.path.exists(self.phrase_log_path):
            return

        with open(self.phrase_log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    self.display_phrase_entry(entry)
                except json.JSONDecodeError:
                    continue

    def display_phrase_entry(self, entry):
        phrase_tokens = entry.get("tokens", [])
        phrase_text = " ".join(phrase_tokens)
        weight = entry.get("weight", 0)
        sigil = entry.get("sigil_context", "□")

        row = tk.Frame(self.scrollable_frame, bg="black", pady=4)
        row.pack(fill="x", anchor="w")

        label = tk.Label(row, text=f"{sigil}  {phrase_text}", fg="white", bg="black", font=("Consolas", 10))
        label.pack(side="left", padx=8)

        weight_bar = tk.Canvas(row, width=80, height=5, bg="#222", highlightthickness=0)
        fill_width = int(min(1.0, weight / 3.0) * 80)
        weight_bar.create_rectangle(0, 0, fill_width, 5, fill="#44ff44", width=0)
        weight_bar.pack(side="right", padx=6)

        audio_file = os.path.join(self.phrase_audio_dir, f"{'_'.join(phrase_tokens)}.mp3")
        if os.path.exists(audio_file):
            play_btn = tk.Button(row, text="▶", command=lambda p=audio_file: self.play_audio(p), bg="black", fg="white")
            play_btn.pack(side="right", padx=6)

        # Add FFT visual trail
        fft_frame = tk.Frame(self.scrollable_frame, bg="black")
        fft_frame.pack(fill="x", anchor="w", padx=12)
        fft_images = load_fft_images_for_phrase(phrase_tokens)
        for img in fft_images:
            if img:
                label = tk.Label(fft_frame, image=img, bg="black")
                label.image = img  # Keep reference
                label.pack(side="left", padx=2)

    def play_audio(self, filepath):
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":
                subprocess.call(["open", filepath])
            else:
                subprocess.call(["xdg-open", filepath])
        except Exception as e:
            print(f"Error playing file: {filepath}", e)
