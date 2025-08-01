import os
import json
import queue
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Optional

class SKGGUI:
    """Simple Tkinter interface for SKGEngine."""

    def __init__(self, engine) -> None:
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("SKG Interface")

        self.update_queue: queue.Queue = queue.Queue()
        self.images: dict[str, ImageTk.PhotoImage] = {}

        # Layout frames for four panels
        self.video_frame = tk.Frame(self.root)
        self.video_frame.grid(row=0, column=0, padx=5, pady=5)

        self.console_frame = tk.Frame(self.root)
        self.console_frame.grid(row=0, column=1, padx=5, pady=5)

        self.fft_frame = tk.Frame(self.root)
        self.fft_frame.grid(row=1, column=0, padx=5, pady=5)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=1, column=1, padx=5, pady=5)

        # Video panel
        self.video_label = tk.Label(self.video_frame, text="Video", width=256, height=256)
        self.video_label.pack()

        # Console text output
        self.console_text = tk.Text(self.console_frame, width=40, height=15)
        self.console_text.pack()

        # FFT panels inside fft_frame
        self.avatar_label = tk.Label(self.fft_frame, text="Glyph", width=256, height=256)
        self.avatar_label.grid(row=0, column=0, padx=5, pady=5)

        self.audio_fft_label = tk.Label(self.fft_frame, text="Audio FFT", width=256, height=256)
        self.audio_fft_label.grid(row=0, column=1, padx=5, pady=5)

        self.image_fft_label = tk.Label(self.fft_frame, text="Image FFT", width=256, height=256)
        self.image_fft_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Memory browser and toggles inside control_frame
        self.memory_list = tk.Listbox(self.control_frame, height=15)
        self.memory_list.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        self.memory_list.bind("<<ListboxSelect>>", self.on_memory_select)

        self.toggle_frame = tk.Frame(self.control_frame)
        self.toggle_frame.grid(row=0, column=1, sticky="n", padx=5, pady=5)

        self.detail_text = tk.Text(self.control_frame, width=40, height=15)
        self.detail_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.speech_var = tk.BooleanVar(value=getattr(engine, "speech_enabled", True))
        self.gesture_var = tk.BooleanVar(value=getattr(engine, "gesture_enabled", True))
        self.recursion_var = tk.BooleanVar(value=getattr(engine, "recursion_enabled", True))

        for label, var in [
            ("Autonomous Speech", self.speech_var),
            ("Gesture", self.gesture_var),
            ("Recursion", self.recursion_var),
        ]:
            chk = tk.Checkbutton(self.toggle_frame, text=label, variable=var, command=self.apply_toggles)
            chk.pack(anchor="w")

        self.update_memory_list()

    def apply_toggles(self) -> None:
        self.engine.speech_enabled = self.speech_var.get()
        self.engine.gesture_enabled = self.gesture_var.get()
        self.engine.recursion_enabled = self.recursion_var.get()

    def run(self) -> None:
        self.root.after(200, self.process_queue)
        self.root.mainloop()

    def process_queue(self) -> None:
        while not self.update_queue.empty():
            glyph = self.update_queue.get()
            self._update_display(glyph)
        self.root.after(200, self.process_queue)

    def update_from_token(self, glyph: dict) -> None:
        self.update_queue.put(glyph)

    def _update_display(self, glyph: dict) -> None:
        visual = glyph.get("modalities", {}).get("visual", {})
        audio_mod = glyph.get("modalities", {}).get("audio", {})
        glyph_path = visual.get("symbolic_image")
        audio_fft = audio_mod.get("fft_audio")
        img_fft = visual.get("fft_from_image") or visual.get("fft_visual")

        self._set_image(self.avatar_label, glyph_path, "avatar")
        self._set_image(self.audio_fft_label, audio_fft, "audio")
        self._set_image(self.image_fft_label, img_fft, "imgfft")
        self.update_memory_list()

    def _set_image(self, label: tk.Label, path: Optional[str], key: str) -> None:
        if path and os.path.exists(path):
            try:
                img = Image.open(path).resize((256, 256))
                photo = ImageTk.PhotoImage(img)
                label.config(image=photo, text="")
                self.images[key] = photo
            except Exception:
                label.config(text="(image error)", image="")
        else:
            label.config(text="No image", image="")

    def update_memory_list(self) -> None:
        self.memory_list.delete(0, tk.END)
        for token in sorted(self.engine.token_map.keys()):
            self.memory_list.insert(tk.END, token)

    def on_memory_select(self, event) -> None:
        sel = self.memory_list.curselection()
        if not sel:
            return
        token = self.memory_list.get(sel[0])
        glyph = self.engine.token_map.get(token, {})
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert("1.0", json.dumps(glyph, indent=2))

    def update_video(self, path: str) -> None:
        """Display the latest webcam frame."""
        if path and os.path.exists(path):
            try:
                img = Image.open(path).resize((256, 256))
                photo = ImageTk.PhotoImage(img)
                self.video_label.config(image=photo, text="")
                self.images["video"] = photo
            except Exception:
                self.video_label.config(text="(image error)", image="")
        else:
            self.video_label.config(text="No image", image="")

    def append_message(self, msg: str) -> None:
        """Append a message to the console text area."""
        self.console_text.insert(tk.END, msg + "\n")
        self.console_text.see(tk.END)


