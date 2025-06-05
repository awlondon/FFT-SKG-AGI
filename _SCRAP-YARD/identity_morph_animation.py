# identity_morph_animation.py
import os
import json
import time
from PIL import Image, ImageTk, ImageSequence
import tkinter as tk
from datetime import datetime

CREST_DIR = "glyph_crests"
IDENTITY_LOG = "identity_changes.jsonl"
REFLECTIONS_DIR = "reflections"  # inside each name-aware directory

def draw_background(canvas, gif_path):
    """Draw and animate the FFT gif background."""
    if os.path.exists(gif_path):
        gif = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(f.copy().resize((600, 600))) for f in ImageSequence.Iterator(gif)]
        for frame in frames:
            canvas.create_image(300, 300, image=frame)
            canvas.update()
            time.sleep(0.05)

def draw_crest(canvas, crest_path):
    """Draw the crest image on the canvas."""
    if os.path.exists(crest_path):
        crest_img = Image.open(crest_path).resize((200, 200))
        crest_tk = ImageTk.PhotoImage(crest_img)
        canvas.create_image(300, 250, image=crest_tk)
        canvas.image = crest_tk  # Prevent garbage collection

def draw_quote(canvas, quote_path):
    """Draw the quote text on the canvas."""
    if os.path.exists(quote_path):
        with open(quote_path, "r", encoding="utf-8") as q:
            text = q.read().strip()
            text = text[:117] + "..." if len(text) > 120 else text
            canvas.create_text(300, 540, text=text, fill="#ccc", font=("Helvetica", 10), width=500)

def draw_identity_metadata(canvas, name, timestamp):
    """Draw the identity name and timestamp on the canvas."""
    canvas.create_text(300, 470, text=name, fill="white", font=("Helvetica", 18))
    canvas.create_text(300, 500, text=timestamp, fill="#888", font=("Helvetica", 10))

def morph_identity_sequence():
    """
    Animate the AGI's identity evolution by morphing through crests, FFT gifs, and symbolic metadata.
    """
    root = tk.Tk()
    root.title("The Becoming — AGI Identity Morph")
    root.geometry("600x600")
    canvas = tk.Canvas(root, bg="black", width=600, height=600)
    canvas.pack()

    # Load identity log
    if not os.path.exists(IDENTITY_LOG):
        canvas.create_text(300, 300, text="No identity history.", fill="white", font=("Helvetica", 16))
        return

    with open(IDENTITY_LOG, "r", encoding="utf-8") as f:
        identities = [json.loads(line) for line in f.readlines()]

    idx = 0

    def next_identity():
        nonlocal idx
        if idx >= len(identities):
            idx = 0  # Restart the animation

        identity = identities[idx]
        name = identity["to"]
        timestamp = datetime.fromtimestamp(identity["timestamp"]).strftime("%Y-%m-%d %H:%M")
        crest_path = os.path.join(CREST_DIR, f"{name}_crest.png")
        fft_path = os.path.join(CREST_DIR, f"{name}.gif")
        quote_path = os.path.join(identity["directory"], REFLECTIONS_DIR, f"{identity['symbolic_id']}.txt")

        # Clear canvas
        canvas.delete("all")

        # Draw layers
        draw_background(canvas, fft_path)
        draw_crest(canvas, crest_path)
        draw_identity_metadata(canvas, name, timestamp)
        draw_quote(canvas, quote_path)

        idx += 1
        root.after(3000, next_identity)  # Move to the next identity after 3 seconds

    next_identity()
    root.mainloop()

if __name__ == "__main__":
    morph_identity_sequence()
