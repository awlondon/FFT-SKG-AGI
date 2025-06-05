# visualizers/fft_visuals.py
import tkinter as tk
from PIL import Image, ImageTk
import os
import pygame
import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Warning: Could not initialize pygame mixer: {e}")

class FFTGifPlayer:
    """Player for FFT animation sequences as GIFs."""
    
    def __init__(self, gif_path):
        self.gif_path = gif_path
        self.root = None
        self.canvas = None
        self.frames = []
        self.current_frame = 0
        self.playing = False
        self.speed = 100
        
        try:
            self.gif = Image.open(gif_path)
            # Extract all frames
            self.frames = []
            for i in range(self.gif.n_frames):
                self.gif.seek(i)
                frame = self.gif.copy()
                self.frames.append(ImageTk.PhotoImage(frame))
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
            return

        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the player UI components."""
        self.root = tk.Toplevel()
        self.root.title(f"FFT Visualizer - {os.path.basename(self.gif_path)}")
        
        # If we got no frames, show error message
        if not self.frames:
            tk.Label(self.root, text=f"Error: Could not load frames from {self.gif_path}").pack(pady=20)
            return
            
        # Create canvas for the animation
        self.canvas = tk.Canvas(self.root, width=self.gif.width, height=self.gif.height)
        self.canvas.pack(pady=10)

        # Controls frame
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Player controls
        self.play_button = tk.Button(controls_frame, text="⏯ Play", command=self.toggle_play)
        self.play_button.pack(side="left", padx=5)
        
        self.rewind_button = tk.Button(controls_frame, text="⏮ Rewind", command=self.rewind)
        self.rewind_button.pack(side="left", padx=5)
        
        self.speed_slider = tk.Scale(controls_frame, from_=50, to=500, orient=tk.HORIZONTAL, label="Speed (ms)")
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(side="left", padx=5, fill="x", expand=True)
        
        # Initial frame display
        self.update_frame()

    def toggle_play(self):
        """Toggle play/pause state."""
        self.playing = not self.playing
        if self.playing:
            self.play_button.config(text="⏸ Pause")
            self.play()
        else:
            self.play_button.config(text="⏯ Play")

    def play(self):
        """Play the animation."""
        if self.playing:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.update_frame()
            self.root.after(self.speed_slider.get(), self.play)

    def rewind(self):
        """Rewind to the first frame."""
        self.current_frame = 0
        self.update_frame()

    def update_frame(self):
        """Update the displayed frame."""
        if self.canvas and self.frames:
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.frames[self.current_frame])

    def run(self):
        """Run the player."""
        if self.root:
            self.root.mainloop()


class FFTCombinedVisualizer:
    """Combined visualizer showing both audio spectrogram and time domain visualization."""
    
    def __init__(self, audio_path=None, fft_image_path=None):
        self.audio_path = audio_path
        self.fft_image_path = fft_image_path
        self.root = None
        
    def setup_ui(self):
        """Set up the visualizer UI."""
        self.root = tk.Toplevel()
        self.root.title("FFT Audio-Visual Analyzer")
        self.root.geometry("800x600")
        
        # FFT image display (if available)
        if self.fft_image_path and os.path.exists(self.fft_image_path):
            try:
                img = Image.open(self.fft_image_path)
                # Resize if needed
                max_width = 600
                if img.width > max_width:
                    ratio = max_width / img.width
                    img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
                self.display_img = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(self.root, image=self.display_img)
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading FFT image: {e}")
        
        # Audio controls (if available)
        if self.audio_path and os.path.exists(self.audio_path):
            audio_frame = tk.Frame(self.root)
            audio_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(audio_frame, text="Audio Controls:").pack(side="left", padx=5)
            
            play_btn = tk.Button(audio_frame, text="▶️ Play", 
                              command=lambda: self.play_audio())
            play_btn.pack(side="left", padx=5)
            
            stop_btn = tk.Button(audio_frame, text="⏹️ Stop", 
                               command=lambda: pygame.mixer.music.stop())
            stop_btn.pack(side="left", padx=5)
            
            # Audio visualization if matplotlib is available
            try:
                self.setup_audio_visualization()
            except Exception as e:
                print(f"Could not create audio visualization: {e}")
    
    def setup_audio_visualization(self):
        """Set up matplotlib-based audio visualization (optional)."""
        # This would require additional audio processing libraries
        # like librosa to extract features from the audio file
        pass
    
    def play_audio(self):
        """Play the audio file."""
        if pygame.mixer.get_init() and self.audio_path and os.path.exists(self.audio_path):
            try:
                pygame.mixer.music.load(self.audio_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Error playing audio: {e}")
    
    def run(self):
        """Run the visualizer."""
        self.setup_ui()
        if self.root:
            self.root.mainloop()


# Utility functions to launch various visualizers

def launch_fft_gif_viewer(glyph_id):
    """Launch the FFT GIF player for a specific glyph."""
    path = f"glyphs/fft/{glyph_id}.gif"  # Expects pre-rendered loopable GIF

    if not os.path.exists(path):
        print(f"FFT GIF not found at {path}.")
        return

    player = FFTGifPlayer(path)
    player.run()

def play_frame_audio(frame_id):
    """Play the audio associated with a specific frame."""
    path = f"symbolic_frames/frame_{frame_id:08d}/audio.wav"
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing audio {path}: {e}")
    else:
        print(f"Audio not found at {path}")

def visualize_fft_for_token(token_id):
    """Show a combined visualization for a token."""
    # Define paths to both audio and FFT image for the token
    audio_path = f"tokens_audio/{token_id}.wav"
    fft_path = f"tokens_fft_img/{token_id}.png"
    
    visualizer = FFTCombinedVisualizer(audio_path, fft_path)
    visualizer.run()


if __name__ == "__main__":
    # Example usage for testing
    if len(sys.argv) > 1:
        glyph_id = sys.argv[1]
        launch_fft_gif_viewer(glyph_id)
    else:
        print("Usage: python -m visualizers.fft_visuals <glyph_id>")
        print("Example: python -m visualizers.fft_visuals 🜲")