# visualizers/emergence.py
import tkinter as tk
from tkinter import Canvas
import os
import math
import numpy as np
import PIL.Image
import matplotlib.pyplot as plt
import json
from PIL import Image
import sys

# Add parent directory to path to allow importing from main package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visual_utils import get_color_for_token, blend_colors

class EmergenceVisualizer:
    """Visualizer for emergent thoughts and symbolic relationships."""
    
    def __init__(self, token_id=None, relationships=None, fft_path=None, emergence_duration=None):
        self.token_id = token_id
        self.relationships = relationships or {}
        self.fft_path = fft_path
        self.emergence_duration = emergence_duration
        self.window = None
        self.canvas = None
        
    def show(self):
        """Create and display the emergence visualization window."""
        self.window = tk.Tk()
        self.window.title(f"Emergent Thought: {self.token_id} (after {self.emergence_duration}s)")

        self.canvas = tk.Canvas(self.window, width=800, height=800, bg='white')
        self.canvas.pack()

        center_x, center_y = 400, 400
        radius = 300
        glyphs = list(self.relationships.keys())[:12]  # Limit to 12 glyphs for outer ring

        nodes = self._draw_glyph_ring(center_x, center_y, radius, glyphs)
        self._draw_relationship_lines(center_x, center_y, nodes)
        self._setup_interaction_bindings(nodes)

        self.window.mainloop()
        
    def _draw_glyph_ring(self, center_x, center_y, radius, glyphs):
        """Draw glyph nodes in a circular layout."""
        angle_step = 360 / len(glyphs)
        nodes = {}

        for i, glyph in enumerate(glyphs):
            angle_rad = i * angle_step * math.pi / 180
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            node = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill='lightgray')
            text = self.canvas.create_text(x, y, text=glyph, font=('Arial', 18))
            nodes[node] = (glyph, x, y)

        return nodes

    def _draw_relationship_lines(self, center_x, center_y, nodes):
        """Draw adjacency threads with color coding."""
        for node, (glyph, x, y) in nodes.items():
            if glyph in self.relationships:
                top_tokens = sorted(self.relationships[glyph].items(), key=lambda x: -x[1])[:2]
                if len(top_tokens) == 2 and abs(top_tokens[0][1] - top_tokens[1][1]) < 0.1:
                    color = blend_colors(get_color_for_token(top_tokens[0][0]), get_color_for_token(top_tokens[1][0]))
                else:
                    color = get_color_for_token(top_tokens[0][0])

                self.canvas.create_line(center_x, center_y, x, y, fill=color, width=2)

    def _setup_interaction_bindings(self, nodes):
        """Set up hover, click, and toggle bindings for the canvas."""
        def on_hover(event):
            for node, (glyph, x, y) in nodes.items():
                if self.canvas.find_withtag("current")[0] == node:
                    top_tokens = sorted(self.relationships[glyph].items(), key=lambda x: -x[1])[:5]
                    y_offset = 40
                    for i, (tid, weight) in enumerate(top_tokens):
                        txt = self._get_token_preview(tid)
                        self.canvas.create_text(x, y + y_offset + (i * 20), text=f"{txt} ({weight})", tag="hover_preview")
                    break

        def on_leave(event):
            self.canvas.delete("hover_preview")

        def on_click(event):
            for node, (glyph, x, y) in nodes.items():
                if self.canvas.find_withtag("current")[0] == node:
                    # Launch FFT gif viewer when available
                    from fft_emergence_gif_stream import launch_fft_gif_viewer
                    launch_fft_gif_viewer(glyph)
                    break

        self.canvas.bind("<Motion>", on_hover)
        self.canvas.bind("<Leave>", on_leave)
        self.canvas.bind("<Button-1>", on_click)
        
    def _get_token_preview(self, tid):
        """Retrieve a preview of the token's content or indicate its media type."""
        text_path = f"tokens/{tid}.txt"
        image_path = f"tokens/{tid}.png"
        audio_path = f"tokens/{tid}.mp3"

        if os.path.exists(text_path):
            try:
                with open(text_path, "r", encoding="utf-8") as f:
                    return f.read()[:50]
            except Exception as e:
                return f"[Error reading text: {e}]"
        elif os.path.exists(image_path):
            return "[Media: image]"
        elif os.path.exists(audio_path):
            return "[Media: audio]"
        else:
            return "[Unknown media type]"


class GlyphStreamManager:
    """Manages the glyph stream during the thought loop."""
    def __init__(self, max_length=50):
        self.stream = []
        self.max_length = max_length

    def add_glyph(self, glyph):
        self.stream.append(glyph)
        if len(self.stream) > self.max_length:
            self.stream.pop(0)

    def get_stream(self):
        return self.stream


# Utility functions for glyph stream and emergence events
def export_emergent_fft_stream(token_id, glyph_stream):
    """Save the glyph-FFT sequence as a .gif."""
    fft_images = []
    for glyph in glyph_stream:
        path = f"glyphs/fft/{glyph}.png"
        if os.path.exists(path):
            fft_images.append(Image.open(path))

    if fft_images:
        out_path = f"tokens_fft_gif/{token_id}.gif"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fft_images[0].save(out_path, save_all=True, append_images=fft_images[1:], duration=80, loop=0)

def log_emergent_output(token_id):
    """Log emergent token output to skg_output_stream.jsonl."""
    log_path = "skg_output_stream.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps({"token_id": token_id, "type": "emergent", "path": f"tokens_fft_gif/{token_id}.gif"}) + "\n")

def update_token_metadata(token_id):
    """Add the stream path to the token's metadata."""
    db_path = f"dbRw/{token_id}.json"
    if os.path.exists(db_path):
        with open(db_path, "r+") as f:
            data = json.load(f)
            data["stream_path"] = f"tokens_fft_gif/{token_id}.gif"
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()


# Function to handle emergent tokens and launch the visualizer
def handle_emergent_token(token_id, relationships, fft_path=None, emergence_duration=None):
    """Visualize an emergent token with its symbolic relationships."""
    visualizer = EmergenceVisualizer(token_id, relationships, fft_path, emergence_duration)
    visualizer.show()


if __name__ == "__main__":
    # Example usage for testing
    mock_relationships = {
        "🜲": {"token1": 5.2, "token2": 3.1},
        "🜃": {"token3": 4.8, "token4": 2.5},
        "🜚": {"token5": 6.1, "token6": 1.9},
    }
    handle_emergent_token("test_token", mock_relationships, emergence_duration=10)