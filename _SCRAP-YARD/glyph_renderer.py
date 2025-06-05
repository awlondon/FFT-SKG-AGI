# glyph_renderer.py

import os
from PIL import Image as PilImage, ImageDraw, ImageFont, ImageOps
from symbolic_constants import GLYPH_IMAGE_DIR, GLYPH_IMAGE_SIZE, PROTO_SIGILS, DEFAULT_GLYPH_FONT_PATH  # Import PROTO_SIGILS from symbolic_constants
import cv2
import numpy as np
from fft_utils import normalize_and_generate_fft

FONT_PATH = DEFAULT_GLYPH_FONT_PATH
os.makedirs(GLYPH_IMAGE_DIR, exist_ok=True)

# Ensure the Symbola font exists at the specified path
try:
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(
            f"[ERROR] Missing font: {FONT_PATH}. Please ensure Symbola.ttf is located in the repository root."
        )
except FileNotFoundError as e:
    print(e)
    exit(1)


def render_glyph_image(glyph, font_path=FONT_PATH):
    """
    Renders a glyph as an image.

    Args:
        glyph (str): The glyph to render.
        size (int): The size of the image (width and height).
        font_path (str): Path to the font file.

    Returns:
        PIL.Image.Image: The rendered glyph image.
    """
    # print(f"[TRACE] render_glyph_image called with glyph={glyph}, size={size}, font_path={font_path}")
    # assert isinstance(size, int), f"[CRITICAL] 'size' must be an int, got {type(size).__name__}: {size}"
    # if not os.path.exists(font_path):
    #     raise FileNotFoundError(f"[❌] Font not found: {font_path}. Please ensure the font file exists.")
    # if not isinstance(glyph, str):
    #     raise TypeError(f"[CRITICAL] 'glyph' must be a string, got {type(glyph).__name__}: {glyph}")

    # # Debugging log to check glyph type and value
    # print(f"[DEBUG] Rendering glyph: {glyph} (type: {type(glyph)})")
    # print(f"[DEBUG] Image size: {size}x{size}, Font path: {font_path}")

    size = GLYPH_IMAGE_SIZE[0]

    min_font_size = 10  # Define a minimum font size
    calculated_font_size = max(int(size * 0.8), min_font_size)
    try:
        font = ImageFont.truetype(font_path, size=calculated_font_size)
    except Exception as e:
        raise RuntimeError(f"[❌] Failed to load font: {font_path}. Error: {e}")

    img = PilImage.new("L", (size, size), color=255)
    draw = ImageDraw.Draw(img)

    # Check if the glyph is supported by the font
    if not font.getmask(glyph).getbbox():
        raise ValueError(f"[❌] The glyph '{glyph}' is not supported by the font at {font_path}.")

    # Ensure text_bbox values are integers to avoid type mismatch
    text_bbox = draw.textbbox((0, 0), glyph, font=font)
    text_size = (int(text_bbox[2] - text_bbox[0]), int(text_bbox[3] - text_bbox[1]))
    print(f"[DEBUG] Calculated text size using textbbox: {text_size}")
    pos = (int((size - text_size[0]) // 2), int((size - text_size[1]) // 2))
    print(f"[DEBUG] Calculated text position: {pos}")
    draw.text(pos, glyph, fill=0, font=font)

    print(f"[DEBUG] Successfully rendered glyph: {glyph}")
    return img


# Optional batch run for PROTO_SIGILS
if __name__ == "__main__":
    os.makedirs(GLYPH_IMAGE_DIR, exist_ok=True)  # Ensure the directory exists

    for glyph in PROTO_SIGILS:
        img = render_glyph_image(glyph, size=GLYPH_IMAGE_SIZE[0], font_path=FONT_PATH)
        path = os.path.join(GLYPH_IMAGE_DIR, f"{glyph}.png")

        # Save the rendered image to the specified path
        img.save(path)
        print(f"[🖼] Rendered glyph image: {glyph} → {path}")

    input_folder = "glyph_images"
    output_folder = "glyph_images/_processed"

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".png"):
                image_path = os.path.join(root, file)
                normalize_and_generate_fft(image_path, output_folder)
