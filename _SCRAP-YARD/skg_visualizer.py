# skg_visualizer.py
import os
import time
import math
import io
import json
import threading
from tkinter import *
from tkinter import ttk, simpledialog, messagebox
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageTk
import matplotlib.pyplot as plt
import numpy as np

import utils  # Replace import of main with utils

class SKGVisualizer(Tk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.queue = deque(maxlen=1000)  # Prevent runaway backlogs
        self.freeze = False
        self.bind("<f>", self.toggle_freeze)

        self.title("Pentacognon Sigil HLSF Visualizer")
        self.geometry("960x720")
        self.configure(bg="#f5f5f5")

        self.start_time = time.time()  # Store the time when processing starts

        self.build_layout()

    def build_layout(self):
        """Build the main layout of the visualizer."""
        self.build_status_bar()
        self.build_progress_panel()
        self.build_glyph_stream()
        self.build_scrollable_canvas()

    def build_status_bar(self):
        """Create the status bar for displaying status messages."""
        self.status_label = Label(self, text="Status: Ready", font=("Helvetica", 16), fg="black", bg="#f5f5f5")
        self.status_label.pack(pady=20)

    def build_progress_panel(self):
        """Create the progress bar and ETA display."""
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=600)
        self.progress.pack(pady=20)

        self.eta_label = Label(self, text="ETA: N/A", font=("Courier", 10), fg="#333", bg="#f5f5f5")
        self.eta_label.pack(pady=2)

    def build_glyph_stream(self):
        """Create the glyph stream display."""
        self.glyph_stream_frame = Frame(self, bg="#000000")
        self.glyph_stream_frame.pack(side="right", fill="y", padx=10)
        self.glyph_stream_labels = deque(maxlen=300)

    def build_scrollable_canvas(self):
        """Create a scrollable canvas for additional content."""
        self.canvas = Canvas(self, bg="#f5f5f5")
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#f5f5f5")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def toggle_freeze(self, event=None):
        self.freeze = not self.freeze
        print(f"[VISUALIZER] Freeze set to {self.freeze}")

    def update_progress(self, progress_value):
        if self.progress:
            self.progress["value"] = progress_value * 100  # progress_value should be between 0 and 1
        self.update_idletasks()

    def update_status(self, status_text):
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)
        else:
            print(f"[STATUS UPDATE] {status_text}")

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def update_eta(self, processed_tokens):
        total_tokens = self.engine.total_tokens
        if total_tokens > 0:
            remaining_tokens = total_tokens - processed_tokens
            elapsed = int(time.time() - self.start_time)  # Calculate elapsed time
            elapsed_display = self.format_time(elapsed)  # Format elapsed time as mm:ss

            if remaining_tokens > 0:
                avg_time_per_token = (time.time() - self.start_time) / processed_tokens if processed_tokens > 0 else 0
                eta_seconds = int(remaining_tokens * avg_time_per_token)
                eta_display = self.format_time(eta_seconds)  # Format ETA as mm:ss
            else:
                eta_display = "—"

            self.eta_label.config(
                text=f"ETA: {eta_display} | Elapsed: {elapsed_display} | Processed: {processed_tokens}/{total_tokens}"
            )
        else:
            self.eta_label.config(text="ETA: N/A")
        self.update_idletasks()

    def stream_glyph(self, glyph, weight=1):
        if self.freeze:
            return

        display = f"{glyph}" if weight <= 1 else f"{glyph}{weight}"
        color = self.get_glyph_display_color(weight)

        label = Label(self.glyph_stream_frame, text=display, font=("Courier", 14),
                      bg="#000000", fg=color, anchor="w", width=4)
        label.pack(anchor="w")

        self.glyph_stream_labels.append(label)

        if len(self.glyph_stream_labels) >= 300:
            oldest = self.glyph_stream_labels.popleft()
            oldest.destroy()

    def get_glyph_display_color(self, weight):
        """Determine the display color for a glyph based on its weight."""
        if weight <= 1:
            return "#66ff66"
        elif weight >= 5:
            return "#ff4444"
        else:
            return "#ffaa00"

    def initialize_proto_glyphs(self, glyph_list):
        print(f"[VISUALIZER] Initializing proto-glyphs: {glyph_list}")