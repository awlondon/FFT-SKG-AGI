# emergent_thoughts.py
import tkinter as tk
import os
import math
from tkinter import Canvas, Entry, Button, filedialog
import numpy as np
import PIL.Image
import matplotlib.pyplot as plt
import json
from PIL import Image
from visual_utils import get_color_for_token, blend_colors

def draw_glyph_ring(canvas, center_x, center_y, radius, glyphs):
    """Draw glyph nodes in a circular layout."""
    angle_step = 360 / len(glyphs)
    nodes = {}

    for i, glyph in enumerate(glyphs):
        angle_rad = i * angle_step * math.pi / 180
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        node = canvas.create_oval(x-30, y-30, x+30, y+30, fill='lightgray')
        text = canvas.create_text(x, y, text=glyph, font=('Arial', 18))
        nodes[node] = (glyph, x, y)

    return nodes

def draw_relationship_lines(canvas, center_x, center_y, nodes, relationships):
    """Draw adjacency threads with color coding."""
    for node, (glyph, x, y) in nodes.items():
        if glyph in relationships:
            top_tokens = sorted(relationships[glyph].items(), key=lambda x: -x[1])[:2]
            if len(top_tokens) == 2 and abs(top_tokens[0][1] - top_tokens[1][1]) < 0.1:
                color = blend_colors(get_color_for_token(top_tokens[0][0]), get_color_for_token(top_tokens[1][0]))
            else:
                color = get_color_for_token(top_tokens[0][0])

            canvas.create_line(center_x, center_y, x, y, fill=color, width=2)

def setup_interaction_bindings(canvas, nodes, relationships):
    """Set up hover, click, and toggle bindings for the canvas."""
    def on_hover(event):
        for node, (glyph, x, y) in nodes.items():
            if canvas.find_withtag("current")[0] == node:
                top_tokens = sorted(relationships[glyph].items(), key=lambda x: -x[1])[:5]
                y_offset = 40
                for i, (tid, weight) in enumerate(top_tokens):
                    txt = get_token_preview(tid)
                    canvas.create_text(x, y + y_offset + (i * 20), text=f"{txt} ({weight})", tag="hover_preview")
                break

    def on_leave(event):
        canvas.delete("hover_preview")

    def on_click(event):
        for node, (glyph, x, y) in nodes.items():
            if canvas.find_withtag("current")[0] == node:
                launch_fft_gif_viewer(glyph)
                break

    canvas.bind("<Motion>", on_hover)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)

def handle_emergent_token(token_id, relationships, fft_path, emergence_duration):
    window = tk.Tk()
    window.title(f"Emergent Thought: {token_id} (after {emergence_duration}s)")

    canvas = tk.Canvas(window, width=800, height=800, bg='white')
    canvas.pack()

    center_x, center_y = 400, 400
    radius = 300
    glyphs = list(relationships.keys())[:12]  # Limit to 12 glyphs for outer ring

    nodes = draw_glyph_ring(canvas, center_x, center_y, radius, glyphs)
    draw_relationship_lines(canvas, center_x, center_y, nodes, relationships)
    setup_interaction_bindings(canvas, nodes, relationships)

    window.mainloop()

def input_router(file_or_text, glyph_hint=None):
    """Route user input (text, image, audio, or video) to the appropriate processor."""
    if os.path.isfile(file_or_text):
        ext = os.path.splitext(file_or_text)[1].lower()
        if ext in [".png", ".jpg", ".jpeg"]:
            process_image(file_or_text, glyph_hint)
        elif ext in [".mp4", ".avi"]:
            process_video(file_or_text, glyph_hint)
        elif ext in [".wav", ".mp3"]:
            process_audio(file_or_text, glyph_hint)
        else:
            print(f"[⚠️] Unsupported file type: {ext}")
    else:
        process_text(file_or_text, glyph_hint)

def process_text(text, glyph_hint):
    from token_utils import TokenUtils
    tu = TokenUtils() 
    token_id = tu.create_token_with_thought_loop(text)
    if glyph_hint:
        link_name_to_glyph(text, glyph_hint)

    # Track glyph stream and detect emergent tokens
    glyph_stream_manager.stream.clear()
    glyph_stream = get_recent_walked_glyphs()
    if token_id not in input_token_ids and engine.get_token_frequency(token_id) == 1:
        export_emergent_fft_stream(token_id, glyph_stream)
        log_emergent_output(token_id)
        update_token_metadata(token_id)

def process_image(image_path, glyph_hint):
    img = PIL.Image.open(image_path).convert("L")
    fft = np.abs(np.fft.fftshift(np.fft.fft2(np.array(img))))
    save_fft(fft, image_path, "images_fft", glyph_hint)

def process_audio(audio_path, glyph_hint):
    # Extract FFT from audio (placeholder for actual implementation)
    fft = np.random.rand(128, 128)  # Replace with actual FFT logic
    save_fft(fft, audio_path, "audio_fft", glyph_hint)

def process_video(video_path, glyph_hint):
    # Extract frames and process each as an image
    frame_dir = os.path.join("video_frames", os.path.basename(video_path))
    os.makedirs(frame_dir, exist_ok=True)
    # Placeholder: Extract frames and process
    for frame in extract_frames(video_path):
        process_image(frame, glyph_hint)

def save_fft(fft, source_path, fft_dir, glyph_hint):
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    fft_path = os.path.join(BASE_DIR, fft_dir, f"{base_name}.npy")
    np.save(fft_path, fft)
    plt.imsave(fft_path.replace(".npy", ".png"), np.log(fft + 1), cmap="magma")
    if glyph_hint:
        engine.link_name_to_glyph(base_name, glyph_hint)

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

# Replace the global `recent_walked_glyphs` with an instance of `GlyphStreamManager`
glyph_stream_manager = GlyphStreamManager()

def symbolic_walk(current_glyph):
    """Update recursive symbolic walker to track glyphs."""
    glyph_stream_manager.add_glyph(current_glyph)
    # TODO: Implement symbolic walk logic here.

def get_recent_walked_glyphs():
    """Return the current glyph path during the thought loop."""
    return glyph_stream_manager.get_stream()

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

def get_token_preview(tid):
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
