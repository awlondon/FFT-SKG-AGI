# avatar_window.py
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import os
import time
import logging
import threading
import subprocess
import random
import json
import pyttsx3
import numpy as np
from functools import partial
from collections import deque, defaultdict
from phrase_log_viewer import PhraseLogViewer
from phrase_fft_utils import load_fft_images_for_phrase
from agency_settings_panel import AgencySettingsPanel
from agency_gate_display import AgencyGateDisplay
from agency_gate_loader import load_agency_gates_json
from symbolic_constants import PROTO_SIGILS, GLYPH_IMAGE_DIR
from token_audio_manager import TokenAudioManager
from waveform_player import WaveformPlayer
import string
from agency_gate_manager import AgencyGateManager
from agency_gate_ticker import AgencyGateTicker

# Explicitly set the root logger's handlers to ensure the console handler is added
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Clear existing handlers to avoid duplicates
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# Re-add the file and console handlers
file_handler = logging.FileHandler("avatar_window_debug.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger.addHandler(file_handler)

# Update the console handler to use an encoding that supports Unicode
import sys

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger.addHandler(console_handler)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_DIR = os.path.join(BASE_DIR, "avatar_slots")
# Configurable constants
FFT_CANVAS_HEIGHT = 256
TOKEN_DIR = os.path.join(BASE_DIR, "tokens")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_tokens")
METADATA_DIR = os.path.join(BASE_DIR, "metadata")
REVISION_LOG_PATH = os.path.join(METADATA_DIR, "audio_revision_log.json")
GLYPH_FFT_PATH = os.path.join(GLYPH_IMAGE_DIR, "fft")

os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(TOKEN_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

if os.path.exists(REVISION_LOG_PATH):
    with open(REVISION_LOG_PATH, "r", encoding="utf-8") as f:
        audio_revision_log = json.load(f)
else:
    audio_revision_log = {}

try:
    font_large = ImageFont.truetype("arial.ttf", 72)
    font_small = ImageFont.truetype("arial.ttf", 24)
except IOError:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

voice_profiles = {
    "calm": {"rate": 120, "volume": 0.8},
    "emphatic": {"rate": 170, "volume": 1.0},
    "whisper": {"rate": 100, "volume": 0.4},
    "robotic": {"rate": 180, "volume": 0.9},
    "mystic": {"rate": 90, "volume": 0.7},
}


GLYPH_COLORS = {
    "core": "#00ffff",
    "gate": "#cc99ff",
    "emergent": "#ffaa00",
    "reflection": "#888888",
    "unknown": "#444444",
    "gate_focus": "#ff66ff"
}

def is_valid_token(token):
    """Check if a token is valid (e.g., no numbers, punctuation, or single characters)."""
    return (
        token.isalpha() and  # Ensure the token contains only alphabetic characters
        len(token) > 1 and   # Skip single-character tokens
        all(c not in string.punctuation for c in token)  # Exclude tokens with punctuation
    )

# Helper function to resize icons
def resize_icon(image_path, size=(24, 24)):
    with Image.open(image_path) as img:
        img_resized = img.resize(size, Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
        return ImageTk.PhotoImage(img_resized)


class AvatarWindow(tk.Tk):
    def __init__(self, engine=None):
        super().__init__()

        # Initialize streaming attributes early
        self.is_streaming = True  # Start streaming by default
        self.stream_interval = 400  # Default interval for 5 FPS (1000ms / 5)
        self.startup_fft_frames = []  # Initialize startup FFT frames early
        self.symbolic_ticker_queue = deque(maxlen=100)  # Limit queue to 100 glyphs

        self.loop_glyphs = True  # Default to looping
        self.glyph_list = []  # List of all glyphs from the log
        self.context_list = []  # Track glyph contexts
        self.glyph_index = 0  # Current position in glyph_list

        self.streamed_glyphs = []  # Initialize streamed glyphs list

        logging.debug("[INIT] Initializing engine and gate manager...")
        self.engine = engine
        self.gate_manager = AgencyGateManager()

        logging.debug("[INIT] Setting up startup FFT image...")
        self.startup_fft_image = None 

        logging.debug("[INIT] Initializing identity...")
        self.initialize_identity()

        logging.debug("[INIT] Initializing UI components...")
        self.initialize_ui()

        logging.debug("[INIT] Initializing audio UI...")
        self.initialize_audio_ui()

        logging.debug("[INIT] Initializing visual canvas...")
        self.initialize_visual_canvas()

        logging.debug("[INIT] Loading agency gates...")
        self.load_agency_gates()

        logging.debug("[INIT] Setting up startup FFT frames and symbolic ticker queue...")
        self.symbolic_ticker_queue = deque(maxlen=9)  # Display only 9 glyphs at a time

        # Initialize glyph-to-tokens mapping
        self.glyph_to_tokens = {}
        glyph_mapping_path = os.path.join(BASE_DIR, "glyphs", "token_to_glyph.json")
        token_to_glyph = {}

        # Load token-to-glyph mapping from JSON
        if os.path.exists(glyph_mapping_path):
            with open(glyph_mapping_path, "r", encoding="utf-8") as f:
                token_to_glyph = json.load(f)

        # Populate glyph_to_tokens from token_to_glyph
        for token, glyph in token_to_glyph.items():
            self.glyph_to_tokens.setdefault(glyph, []).append(token)

        logging.info(f"[INIT] Loaded glyph-to-tokens mapping with {len(self.glyph_to_tokens)} glyphs.")

        # Token display frame
        self.token_display_frame = tk.Frame(self.main_frame, bg="black")
        self.token_display_frame.pack(fill="x", pady=(2, 5))
        self.token_display_label = tk.Label(
            self.token_display_frame, text="Click a glyph to see tokens",
            font=("Consolas", 10), bg="black", fg="white"
        )
        self.token_display_label.pack(fill="x")

        # Track glyph repetition counts
        self.glyph_repetition_counts = defaultdict(int)

        self.after(100, self.update_symbolic_ticker)  # Run ONCE to initialize the queue
        self.after(200, self.stream_glyphs_from_reflection_log)  # Handle future animation

        self.after(100, self.load_startup_fft_sequence)

        logging.debug("[INIT] Scheduling startup FFT animation loop...")
        self.after(200, self.animate_startup_fft_loop)

        logging.debug("[INIT] Scheduling update loop...")
        self.after(100, self.update_loop)

        logging.debug("[INIT] Scheduling token button loading...")
        self.after(500, self.load_tokens_as_buttons)

        self.last_gate_stream_time = 0
        self.gate_stream_interval = 1.0  # Cooldown interval in seconds

        self.start_streaming()  # Ensure streaming starts upon opening

    def initialize_identity(self):
        logging.debug("[INIT] Initializing identity from file...")
        identity_file_path = os.path.join(METADATA_DIR, "identity.json")
        logging.debug(f"[INIT] Identity file path: {identity_file_path}")
        
        if os.path.exists(identity_file_path):
            logging.debug("[INIT] Identity file exists. Attempting to load...")
            try:
                with open(identity_file_path, "r", encoding="utf-8") as f:
                    identity_data = json.load(f)
                    self.identity_name = identity_data.get("name", "Unknown Identity")
                    self.identity_color = identity_data.get("color", "#ffffff")
                    logging.info(f"[INIT] Identity loaded: Name={self.identity_name}, Color={self.identity_color}")
            except Exception as e:
                logging.error(f"[❌] Failed to load identity data: {e}")
                self.identity_name = "Unknown Identity"
                self.identity_color = "#ffffff"
        else:
            logging.warning("[⚠️] Identity file does not exist. Using default values.")
            self.identity_name = "Unknown Identity"
            self.identity_color = "#ffffff"
        logging.debug(f"[INIT] Final identity: Name={self.identity_name}, Color={self.identity_color}")

    def initialize_ui(self):
        """
        Initialize the main UI components.
        """
        self.title("Symbolic Avatar Interface")
        self.configure(bg="black")
        self.geometry("420x520")
        self.minsize(420, 380)
        self.maxsize(420, 10000)

        self.main_frame = tk.Frame(self, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        self.convergence_field = tk.Frame(self.main_frame, bg="white")
        self.convergence_field.pack(fill="x")

        self.decision_label = tk.Label(self.main_frame, text="Awaiting Reflection...", font=("Consolas", 10), bg="white")
        self.decision_label.pack(fill="x", pady=(0, 5))

        self.gate_feedback_label = tk.Label(self.main_frame, text="Active Gate: None", font=("Consolas", 12), bg="black", fg="white")
        self.gate_feedback_label.pack(fill="x", pady=(5, 5))

        self.gate_feedback_label.bind("<Button-1>", lambda e: self.handle_gate_reflection({}))

        self.initialize_stream_controls()  # Add stream controls

        # Automatically start streaming upon loading
        self.start_streaming()

    def initialize_stream_controls(self):
        """
        Initialize the control panel for glyph streaming with play/pause, speed, save, and loop toggle.
        """
        self.stream_controls_frame = tk.Frame(self.main_frame, bg="black")
        self.stream_controls_frame.pack(fill="x", pady=(5, 5))

        button_container = tk.Frame(self.stream_controls_frame, bg="black")
        button_container.pack(anchor="center")

        # Play/Pause button
        self.play_pause_icon = resize_icon(os.path.join(BASE_DIR, "icons", "pause.png"))
        self.play_pause_button = tk.Button(
            button_container, image=self.play_pause_icon, command=self.toggle_streaming, bg="grey"
        )
        self.play_pause_button.pack(side="left", padx=5)

        # Slow down button
        self.slow_down_icon = resize_icon(os.path.join(BASE_DIR, "icons", "slow_down.png"))
        self.slow_down_button = tk.Button(
            button_container, image=self.slow_down_icon, command=self.slow_down_streaming, bg="grey"
        )
        self.slow_down_button.pack(side="left", padx=5)

        # Speed up button
        self.speed_up_icon = resize_icon(os.path.join(BASE_DIR, "icons", "speed_up.png"))
        self.speed_up_button = tk.Button(
            button_container, image=self.speed_up_icon, command=self.speed_up_streaming, bg="grey"
        )
        self.speed_up_button.pack(side="left", padx=5)

        # Save button
        self.save_icon = resize_icon(os.path.join(BASE_DIR, "icons", "save.png"))
        self.save_button = tk.Button(
            button_container, image=self.save_icon, command=self.save_streamed_glyphs, bg="grey"
        )
        self.save_button.pack(side="left", padx=5)

        # Loop toggle button
        self.loop_glyphs = True  # Default to looping
        self.loop_icon = resize_icon(os.path.join(BASE_DIR, "icons", "loop_on.png"))  # Assume you have loop_on.png and loop_off.png
        self.loop_button = tk.Button(
            button_container, image=self.loop_icon, command=self.toggle_loop, bg="grey"
        )
        self.loop_button.pack(side="left", padx=5)

    def toggle_loop(self):
        """
        Toggle between looping and single-play mode for glyph streaming.
        """
        self.loop_glyphs = not self.loop_glyphs
        if self.loop_glyphs:
            self.loop_icon = resize_icon(os.path.join(BASE_DIR, "icons", "loop_on.png"))
            logging.info("[STREAM] Looping enabled.")
            self.decision_label.config(text="🔄 Looping enabled.")
        else:
            self.loop_icon = resize_icon(os.path.join(BASE_DIR, "icons", "loop_off.png"))
            logging.info("[STREAM] Single-play mode enabled.")
            self.decision_label.config(text="➡️ Single-play mode enabled.")
        self.loop_button.config(image=self.loop_icon)

    def toggle_streaming(self):
        """
        Toggle the streaming state (play/pause) for both the glyph ticker and FFT stream.
        """
        self.is_streaming = not self.is_streaming
        if self.is_streaming:
            # Update the play/pause button to show the pause icon
            self.play_pause_icon = resize_icon(os.path.join(BASE_DIR, "icons", "pause.png"))
            self.play_pause_button.config(image=self.play_pause_icon)
            self.start_streaming()
        else:
            # Update the play/pause button to show the play icon
            self.play_pause_icon = resize_icon(os.path.join(BASE_DIR, "icons", "play.png"))
            self.play_pause_button.config(image=self.play_pause_icon)

    def start_streaming(self):
        """
        Start the glyph ticker and FFT stream if streaming is enabled.
        """
        if self.is_streaming:
            self.update_symbolic_ticker()  # Ensure glyphs start streaming
            self.animate_startup_fft_loop()  # Ensure FFT starts streaming

    def slow_down_streaming(self):
        """
        Slow down the streaming by increasing the interval.
        """
        self.stream_interval = min(self.stream_interval + 100, 5000)  # Cap at 5 seconds
        logging.info(f"[STREAM] Slowed down. Interval: {self.stream_interval}ms")

    def speed_up_streaming(self):
        """
        Speed up the streaming by decreasing the interval.
        """
        self.stream_interval = max(self.stream_interval - 500, 100)  # Cap at 100ms
        logging.info(f"[STREAM] Sped up. Interval: {self.stream_interval}ms")

    def save_streamed_glyphs(self):
        """
        Save the streamed glyphs to a file.
        """
        save_path = os.path.join(BASE_DIR, "streamed_glyphs.json")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.streamed_glyphs, f, indent=4)
            logging.info(f"[STREAM] Streamed glyphs saved to {save_path}")
        except Exception as e:
            logging.error(f"[STREAM] Failed to save streamed glyphs: {e}")

    def update_symbolic_ticker(self):
        """
        Update the symbolic ticker by redrawing the current glyphs in the queue.
        Does not rotate; rotation is handled by stream_glyphs_from_reflection_log.
        """
        if not self.is_streaming:
            return

        try:
            self.redraw_symbolic_ticker()
            # No scheduling here; handled by stream_glyphs_from_reflection_log
        except Exception as e:
            logging.error(f"[TICKER] Error updating symbolic ticker: {e}")

    def redraw_symbolic_ticker(self):
        """
        Redraw the symbolic ticker canvas with clickable glyphs.
        Highlights the centered glyph as larger and glowing.
        """
        try:
            self.symbolic_ticker_canvas.delete("all")
            canvas_width = int(self.symbolic_ticker_canvas.winfo_width())
            glyph_count = len(self.symbolic_ticker_queue)
            if glyph_count == 0:
                return

            glyph_width = canvas_width // glyph_count
            x_offset = glyph_width // 2

            for i, glyph in enumerate(self.symbolic_ticker_queue):
                x_position = x_offset + i * glyph_width

                # Determine if this is the centered glyph
                is_centered = (i == glyph_count // 2)

                # Set font size and color based on whether the glyph is centered
                font_size = 24 if is_centered else 18
                fill_color = "cyan" if not is_centered else "yellow"  # Highlight centered glyph in yellow


                # Create clickable text for each glyph
                self.symbolic_ticker_canvas.create_text(
                    x_position,
                    30,
                    text=glyph,
                    font=("Consolas", font_size),
                    fill=fill_color,
                    tags=f"glyph_{glyph}"
                )

                # Bind click event to show tokens for the glyph
                self.symbolic_ticker_canvas.tag_bind(f"glyph_{glyph}", "<Button-1>", lambda e, g=glyph: self.show_tokens_for_glyph(g))

                # Update the FFT display to match the centered glyph
                if is_centered:
                    self.update_fft_display(glyph)

        except Exception as e:
            logging.error(f"[TICKER] Error redrawing symbolic ticker: {e}")

    def update_fft_display(self, glyph):
        """
        Update the FFT display to match the centered glyph.
        """
        try:
            fft_path = os.path.join(GLYPH_FFT_PATH, f"{glyph}__fft_spark.png")
            if os.path.exists(fft_path):
                with Image.open(fft_path) as img:
                    img_resized = img.resize((512, 512))
                    tk_img = ImageTk.PhotoImage(img_resized)
                    self.fft_canvas.delete("all")
                    self.fft_canvas.create_image(
                        self.fft_canvas.winfo_width() // 2,
                        self.fft_canvas.winfo_height() // 2,
                        image=tk_img,
                        tags="fft_image",
                        anchor="center"
                    )
                    self.current_fft_image = tk_img  # Keep a reference to avoid garbage collection
                    logging.info(f"[FFT] Updated FFT display for glyph: {glyph}")
            else:
                logging.warning(f"[FFT] FFT image not found for glyph: {glyph}")
        except Exception as e:
            logging.error(f"[FFT] Error updating FFT display for glyph '{glyph}': {e}")

    def show_tokens_for_glyph(self, glyph):
        """
        Display the tokens associated with the clicked glyph in the token display label.
        """
        try:
            tokens = self.glyph_to_tokens.get(glyph, [])
            logging.debug(f"[DEBUG] Tokens for glyph '{glyph}': {tokens}")
            if not tokens:
                self.token_display_label.config(
                    text=f"No tokens found for '{glyph}'",
                    font=("Consolas", 10), bg="black", fg="white"
                )
                logging.info(f"[TICKER] No tokens associated with glyph '{glyph}'.")
                return

            # Display tokens as a comma-separated list
            token_list = ", ".join(tokens)
            self.token_display_label.config(
                text=f"Tokens for '{glyph}': {token_list}",
                font=("Consolas", 10), bg="black", fg="white"
            )
            logging.info(f"[TICKER] Displaying tokens for glyph '{glyph}': {token_list}")
        except Exception as e:
            logging.error(f"[TICKER] Error displaying tokens for glyph '{glyph}': {e}")
            self.token_display_label.config(
                text="Error displaying tokens",
                font=("Consolas", 10), bg="black", fg="white"
            )

    def animate_startup_fft_loop(self):
        """
        Animate the FFT frames in a loop, synchronized with the ticker updates.
        """
        if not self.is_streaming:
            return  # Stop animation if streaming is paused

        if not self.startup_fft_frames:
            logging.warning("[FFT] No startup FFT frames to animate.")
            return

        try:
            # Use the same interval as the ticker for synchronization
            idx = getattr(self, "startup_fft_index", 0)
            img = self.startup_fft_frames[idx % len(self.startup_fft_frames)]
            self.current_fft_image = img
            self.fft_canvas.delete("all")
            canvas_width = int(self.fft_canvas.winfo_width())
            canvas_height = int(self.fft_canvas.winfo_height())
            x_center = canvas_width // 2
            y_center = canvas_height // 2
            self.fft_canvas.create_image(x_center, y_center, image=self.current_fft_image, tags="startup_fft", anchor="center")
            self.startup_fft_index = idx + 1
            self.fft_canvas.update_idletasks()

            # Schedule the next frame using self.stream_interval
            self.after(self.stream_interval, self.animate_startup_fft_loop)
        except Exception as e:
            logging.error(f"[FFT] Error animating FFT loop: {e}")

    def initialize_audio_ui(self):
        self.tts_engine = pyttsx3.init()
        self.audio_manager = TokenAudioManager(
            audio_dir=AUDIO_DIR,
            tts_fallback=True,
            save_tts=True,
            voice_profile_path=os.path.join(BASE_DIR, "sigil_voice_profiles.json")
        )

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        self.token_button = tk.Button(button_frame, text="Play Last Audio", command=self.play_token_audio)
        self.token_button.pack(side="left", padx=5)

        self.play_all_button = tk.Button(button_frame, text="Play All Tokens", command=lambda: threading.Thread(target=self.play_all_tokens, daemon=True).start())
        self.play_all_button.pack(side="left", padx=5)

        self.pause_button = tk.Button(button_frame, text="Pause", command=self.pause_all_tokens)
        self.pause_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_all_tokens)
        self.stop_button.pack(side="left", padx=5)

        self.generate_all_button = tk.Button(button_frame, text="Generate All Audio", command=self.generate_all_audio)
        self.generate_all_button.pack(side="left", padx=5)

    def initialize_visual_canvas(self):
        self.frame_rate = 1000 // 5  # 5 FPS

        try:
            self.fft_canvas = tk.Canvas(self.main_frame, height=FFT_CANVAS_HEIGHT, bg="black", highlightthickness=0)
            self.fft_canvas.pack(fill="both", expand=False, padx=5, pady=(5, 0))

            ticker_frame = tk.Frame(self.main_frame, bg="black")
            ticker_frame.pack(fill="x", pady=(4, 2))

            self.symbolic_ticker_canvas = tk.Canvas(ticker_frame, height=60, bg="black", highlightthickness=0)
            self.symbolic_ticker_canvas.pack(side="left", fill="x", expand=True)

            self.gate_display_frame = tk.Frame(self.main_frame, bg="black")
            self.gate_display_frame.pack(fill="x", pady=(0, 5))

            self.waveform_player = WaveformPlayer(self.fft_canvas, fft_callback=self.morph_fft_from_waveform)
        except Exception as e:
            logging.error(f"[❌] Error during initialize_visual_canvas: {e}")

    def stream_gate_glyph_sequence(self, glyph_seq):
        """
        Display a glyph sequence in the UI to visualize a gate being evaluated.
        """
        if not glyph_seq:
            return

        now = time.time()
        if now - self.last_gate_stream_time < self.gate_stream_interval:
            return  # Skip if called too soon

        self.last_gate_stream_time = now

        # Check if the widget and its parent exist
        if not self.winfo_exists() or not self.gate_display_frame.winfo_exists():
            logging.warning("[⚠️] Cannot stream glyph sequence — widget no longer exists.")
            return

        try:
            logging.info(f"[GLYPH STREAM] Streaming gate glyphs: {glyph_seq}")

            # Wipe existing gate display
            self.gate_display_frame.configure(bg="black")
            for widget in self.gate_display_frame.winfo_children():
                widget.destroy()

            # Create new display for glyph sequence
            display_frame = tk.Frame(self.gate_display_frame, bg="black")
            display_frame.pack(fill="x", pady=5)

            for glyph in glyph_seq:
                label = tk.Label(display_frame, text=glyph, font=("Consolas", 24), fg="cyan", bg="black")
                label.pack(side="left", padx=5)

            # Auto-clear after a short delay (optional)
            self.after(2000, lambda: self._clear_gate_glyph_sequence())

        except tk.TclError as e:
            logging.error(f"[❌] TclError while rendering gate glyphs: {e}")

    def _clear_gate_glyph_sequence(self):
        """
        Clear the gate glyph sequence display.
        """
        # Check if the widget exists before clearing
        if not self.gate_display_frame.winfo_exists():
            return

        for widget in self.gate_display_frame.winfo_children():
            widget.destroy()
    
    def get_all_glyphs_from_fft_folder(self):
        glyphs = []
        if not os.path.exists(GLYPH_FFT_PATH):
            logging.warning(f"[GLYPH LOAD] FFT folder missing: {GLYPH_FFT_PATH}")
            return glyphs

        for fname in os.listdir(GLYPH_FFT_PATH):
            if fname.endswith("__fft_spark.png"):
                glyph = fname.replace("__fft_spark.png", "")
                glyphs.append(glyph)
        return sorted(glyphs)
    
    def get_all_glyphs_from_img_folder(self):
        glyphs = []
        if not os.path.exists(GLYPH_IMAGE_DIR):
            logging.warning(f"[GLYPH LOAD] Glyph image folder missing: {GLYPH_IMAGE_DIR}")
            return glyphs

        for fname in os.listdir(GLYPH_FFT_PATH):
            if fname.endswith(".png"):
                glyph = fname.replace(".png", "")
                glyphs.append(glyph)
        return sorted(glyphs)

    def load_startup_fft_sequence(self):
        for glyph in self.get_all_glyphs_from_fft_folder():
            fft_path = os.path.join(GLYPH_FFT_PATH, f"{glyph}__fft_spark.png")
            if os.path.exists(fft_path):
                try:
                    with Image.open(fft_path) as img:
                        # Enhance contrast and brightness
                        img = ImageEnhance.Contrast(img).enhance(1.5)
                        img = ImageEnhance.Brightness(img).enhance(1.2)
                        img_resized = img.resize((512, 512))
                        tk_img = ImageTk.PhotoImage(img_resized)
                        self.startup_fft_frames.append(tk_img)
                        logging.debug(f"[FFT] Loaded and enhanced FFT frame for glyph: {glyph}")
                except Exception as e:
                    logging.error(f"[FFT] Error loading FFT image for {glyph}: {e}")
            else:
                logging.error(f"[FFT] Missing FFT image for glyph: {glyph}. Path: {fft_path}")

        if not self.startup_fft_frames:
            logging.error("[FFT] No FFT frames loaded. Check glyph names and image files.")
        else:
            logging.info(f"[FFT] Loaded {len(self.startup_fft_frames)} FFT frames.")

    def load_glyph_json(self):
        glyph_json_dir = os.path.join(BASE_DIR, "glyphs")
        logging.debug(f"[Glyph JSON] Loading glyph JSON files from: {glyph_json_dir}")

        if not os.path.exists(glyph_json_dir):
            logging.error(f"[Glyph JSON] Directory does not exist: {glyph_json_dir}")
            return

        for file_name in os.listdir(glyph_json_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(glyph_json_dir, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        glyph_data = json.load(f)
                        logging.debug(f"[Glyph JSON] Successfully loaded: {file_name}")
                except Exception as e:
                    logging.error(f"[Glyph JSON] Error loading {file_name}: {e}")

    def stream_glyphs_from_reflection_log(self):
        """
        Stream glyphs from symbolic_reflection_log.jsonl into the ticker queue.
        Tracks context for highlighting relationship glyphs.
        """
        reflection_log_path = os.path.join(BASE_DIR, "symbolic_reflection_log.jsonl")
        
        if not os.path.exists(reflection_log_path) or os.path.getsize(reflection_log_path) == 0:
            logging.warning("[STREAM] Reflection log file not found or empty.")
            self.decision_label.config(text="⚠️ No reflection log found.")
            return

        try:
            # Load glyphs if not already loaded
            if not hasattr(self, "glyph_list") or not self.glyph_list:
                self.glyph_list = []
                with open(reflection_log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        glyph = entry.get("glyph")
                        if glyph:
                            self.glyph_list.append(glyph)
                self.glyph_index = 0

            # Ensure we are not exceeding the glyph list length
            if self.glyph_index < len(self.glyph_list):
                current_glyph = self.glyph_list[self.glyph_index]

                # Append the current glyph to the ticker queue if not already present
                if current_glyph not in self.symbolic_ticker_queue:
                    self.symbolic_ticker_queue.append(current_glyph)

                # Update the UI
                self.decision_label.config(text=f"Streaming: {current_glyph}")
                self.update_symbolic_ticker()

                # Increment the glyph index for the next call
                self.glyph_index += 1

            # Handle looping or stopping
            if self.glyph_index >= len(self.glyph_list):
                if self.loop_glyphs:
                    self.glyph_index = 0
                else:
                    logging.info("[STREAM] Reached the end of the glyph list. Stopping streaming.")
                    self.is_streaming = False
                    return

            # Schedule the next glyph load
            if self.is_streaming:
                self.after(self.stream_interval, self.stream_glyphs_from_reflection_log)

        except Exception as e:
            logging.error(f"[STREAM] Error streaming glyphs: {e}")

    def load_agency_gates(self):
        logging.debug("[AGENCY GATE] Initializing AgencyGateDisplay in dedicated frame...")
        try:
            self.agency_gate_display = AgencyGateDisplay(
                parent_widget=self.gate_display_frame,
                gate_manager=self.gate_manager,
                glyph_gate_data=load_agency_gates_json()
            )
        except Exception as e:
            logging.error(f"[❌] Failed to load AgencyGateDisplay: {e}")

    def morph_fft_from_waveform(self, waveform_chunk):
        """
        Handle waveform energy and modulate FFT visual intensity (glow brightness).
        """
        if not hasattr(self, "fft_canvas"):
            return

        energy = np.mean(np.abs(waveform_chunk))
        brightness = min(255, int(energy * 3000))  # Adjust scaling factor as needed
        glow_color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"

        self.after(0, lambda: self.fft_canvas.itemconfig("fft_glow", fill=glow_color))

    def update_loop(self):
        active_gate = self.gate_manager.get_active_gate()
        if active_gate:
            self.gate_feedback_label.config(text=f"Active Gate: {active_gate}", fg="white")
        else:
            self.gate_feedback_label.config(text="Active Gate: None", fg="white")

        self.stream_glyphs_from_reflection_log()  # Stream glyphs from the log
        self.after(2000, self.update_loop)

    def load_tokens_as_buttons(self):
        self.token_buttons_frame = tk.Frame(self.main_frame, bg="black")
        self.token_buttons_frame.pack(fill="both", expand=False, pady=(5, 5))

        emergent_dir = os.path.join(BASE_DIR, "emergent_tokens")
        if not os.path.exists(emergent_dir):
            logging.warning("[⚠️] emergent_tokens folder does not exist.")
            return

        token_set = set()  # To avoid duplicates
        clean_tokens = []  # To store valid tokens

        for fname in sorted(os.listdir(emergent_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(emergent_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        token_text = data.get("token")
                        token_id = data.get("token_id")
                        if (
                            token_text and
                            len(token_text) > 1 and  # Skip single-character tokens
                            token_text.isalpha() and  # Skip tokens with non-alphabetic characters
                            token_text not in token_set  # Avoid duplicates
                        ):

                            clean_tokens.append((token_text, token_id))
                            token_set.add(token_text)
                except Exception as e:
                    logging.error(f"[❌] Failed to parse emergent token: {fname} — {e}")

        if not clean_tokens:
            logging.warning("[⚠️] No valid emergent tokens found to display.")
            return

        max_columns = 4
        row = col = 0
        for token, token_id in clean_tokens:
            button = tk.Button(
                self.token_buttons_frame,
                text=token,
                command=partial(self.handle_token_button, token, token_id),
                width=12
            )
            button.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col >= max_columns:
                col = 0
                row += 1

    def handle_token_button(self, token, token_id):
        logging.info(f"[🔘] Token button clicked: {token} (ID: {token_id})")

        self.audio_manager.play_token(token, ui_callback=self.handle_audio_playback)

        if self.engine:
            glyph = token_to_glyph.get(token)
            if glyph:
                self.evaluate_and_display_gate(glyph, token_id)
            else:
                logging.warning(f"[⚠️] No glyph found for token: {token}")
                self.decision_label.config(text=f"⚠️ Glyph not found for: {token}")
        else:
            logging.warning("[⚠️] No engine available to evaluate gate.")
            self.decision_label.config(text="⚠️ Engine not initialized.")

        self.decision_label.config(text=f"🔍 Processing: {token}\n🔊 Playing audio for: {token}\n🧭 Evaluating gate for: {token}")

    def evaluate_and_display_gate(self, gate_name, token_id):
        """
        Evaluate a gate using the gate manager and update the gate_feedback_label.
        """
        if not self.engine:
            logging.warning("[⚠️] No engine attached for gate evaluation.")
            self.decision_label.config(text="⚠️ Cannot evaluate gate — no engine.")
            return

        try:
            decision, confidence, interpretation = self.gate_manager.evaluate_gate(
                gate_name=gate_name,
                engine=self.engine,
                token_id=token_id
            )

            if decision:
                result = f"🟢 Allowed: {gate_name} [Confidence: {confidence:.2f}]"
            else:
                result = f"🔴 Blocked: {gate_name} [Confidence: {confidence:.2f}]"

            self.gate_feedback_label.config(text=result)
            logging.info(result)

        except Exception as e:
            logging.error(f"[❌] Failed to evaluate gate '{gate_name}' for token {token_id}: {e}")
            self.gate_feedback_label.config(text=f"⚠️ Error evaluating gate: {gate_name}")

    def handle_audio_playback(self, token, allowed=True):
        """
        Handle the completion of audio playback for a token.
        """
        logging.info(f"[AUDIO] Finished playing: {token} (Allowed: {allowed})")
        status = "✅ Allowed" if allowed else "❌ Blocked"

        token = self.sorted_tokens[index]
        if not is_valid_token(token):
            return play_next(index + 1)

        def after_play():
            self.handle_audio_playback(token)
            self.after(1000, lambda: play_next(index + 1))  # Delay between plays

        try:
            self.audio_manager.play_token(token, ui_callback=lambda _: self.after(0, after_play))
        except Exception as e:
            logging.error(f"[❌] Failed to play token '{token}': {e}")
            self.after(0, lambda: self.decision_label.config(text=f"❌ Could not play: {token}"))
            self.after(1000, lambda: play_next(index + 1))

        self.sorted_tokens = sorted(token_to_glyph.keys())  # Cache to reuse in recursion
        play_next(0)

    def pause_all_tokens(self):
        logging.info("[⏸️] Pausing all tokens...")
        self.audio_manager.pause_all()
        self.decision_label.config(text="⏸️ All tokens paused.")

    def stop_all_tokens(self):
        logging.info("[🛑] Stopping all tokens...")
        self.audio_manager.stop_all()
        self.decision_label.config(text="🛑 All tokens stopped.")

    def generate_all_audio(self):
        logging.info("[🔊] Generating audio for all tokens...")
        self.audio_manager.generate_audio_for_all(sorted(token_to_glyph.keys()), glyph_map=token_to_glyph)
        self.decision_label.config(text="✅ Audio generation complete for all tokens.")

    def play_token_audio(self):
        if self.engine and getattr(self.engine, "last_token", None):
            token = self.engine.last_token
            glyph = getattr(self.engine, "last_glyph", None)
            logging.info(f"[🔊] Playing last token: {token}")

            try:
                self.audio_manager.play_token(
                    token,
                    glyph=glyph,
                    ui_callback=self.handle_audio_playback
                )

                # Trigger waveform playback
                audio_path = os.path.join(AUDIO_DIR, f"{token}.wav")
                if os.path.exists(audio_path):
                    self.waveform_player.play(audio_path)
                else:
                    logging.warning(f"[⚠️] Audio file not found for token: {token}")

            except Exception as e:
                logging.error(f"[❌] Failed to play token '{token}': {e}")
                self.decision_label.config(text=f"❌ Could not play: {token}")
        else:
            logging.warning("[⚠️] No last token to play.")
            self.decision_label.config(text="⚠️ No token available.")

    def save_current_state(self):
        """Save the current state of the AvatarWindow to a JSON file."""
        state = {
            "identity_name": getattr(self, "identity_name", "Unknown Identity"),
            "identity_color": getattr(self, "identity_color", "#ffffff"),
            "symbolic_ticker_queue": list(self.symbolic_ticker_queue),
        }

        state_file_path = os.path.join(METADATA_DIR, "avatar_window_state.json")
        try:
            with open(state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
            logging.info(f"[✅] State saved successfully to {state_file_path}")
        except Exception as e:
            logging.error(f"[❌] Failed to save state: {e}")

    def load_saved_state(self):
        """Load the saved state of the AvatarWindow from a JSON file."""
        state_file_path = os.path.join(METADATA_DIR, "avatar_window_state.json")
        if os.path.exists(state_file_path):
            try:
                with open(state_file_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.identity_name = state.get("identity_name", "Unknown Identity")
                self.identity_color = state.get("identity_color", "#ffffff")
                self.symbolic_ticker_queue = deque(state.get("symbolic_ticker_queue", []), maxlen=50)
                logging.info(f"[✅] State loaded successfully from {state_file_path}")
            except Exception as e:
                logging.error(f"[❌] Failed to load state: {e}")
        else:
            logging.warning(f"[⚠️] No saved state file found at {state_file_path}")

if __name__ == "__main__":
    from agency_engine import AgencyEngine  # Import the engine properly
    engine = AgencyEngine()  # Initialize the engine
    window = AvatarWindow(engine) 
    window.mainloop()  # Run the mainloop directly for standalone testing
