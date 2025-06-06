# glyph_visualizer.py

import os
import re
import hashlib
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Default font path. Prefer the directory containing main.py so running the
# program from any working directory still resolves the font correctly.
if getattr(sys.modules.get("__main__"), "__file__", None):
    MAIN_DIR = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
else:
    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))

# Resolve the path to Symbola.ttf.
# 1. `SYMBOLA_FONT_PATH` environment variable has highest priority.
# 2. Symbola.ttf in the directory containing main.py.
# 3. Symbola.ttf in a `_fonts/` folder next to main.py.
# 4. Symbola.ttf next to this file.
env_font = os.environ.get("SYMBOLA_FONT_PATH")
if env_font and os.path.exists(env_font):
    DEFAULT_FONT_PATH = env_font
else:
    DEFAULT_FONT_PATH = os.path.join(MAIN_DIR, "Symbola.ttf")
    if not os.path.exists(DEFAULT_FONT_PATH):
        alt_path = os.path.join(MAIN_DIR, "_fonts", "Symbola.ttf")
        if os.path.exists(alt_path):
            DEFAULT_FONT_PATH = alt_path
        else:
            alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Symbola.ttf")
            if os.path.exists(alt_path):
                DEFAULT_FONT_PATH = alt_path

def generate_glyph_image(token, output_dir="modalities/images", font_path=None):
    """
    Generate and save an image of a glyph corresponding to the given token.
    """
    print(f"[GlyphVisualizer] Generating glyph image for: {token}")

    if font_path is None:
        font_path = DEFAULT_FONT_PATH

    # Create a hashed and sanitized filename
    hash_id = hashlib.sha1(token.encode()).hexdigest()[:8]
    safe_token = re.sub(r"[^a-zA-Z0-9_-]", "_", token)
    image_filename = f"{safe_token}_{hash_id}_sigil.png"
    image_path = os.path.join(output_dir, image_filename)
    os.makedirs(output_dir, exist_ok=True)

    # Image setup
    width, height = 512, 512
    background_color = "white"
    text_color = "black"
    font_size = 220

    try:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"[GlyphVisualizer] Warning: Could not load Symbola font: {e}")
            font = ImageFont.load_default()

        img = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), token, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_position = ((width - text_w) // 2, (height - text_h) // 2)

        draw.text(text_position, token, fill=text_color, font=font)
        img.save(image_path)
        print(f"[GlyphVisualizer] Saved to: {image_path}")
        return image_path

    except Exception as e:
        print(f"[GlyphVisualizer] Error creating glyph image: {e}")
        return None

def externalize_token(token, token_data, output_dir="modalities/images"):
    """
    Externalize a token by generating its glyph image.
    Additional modalities (like FFT or audio) can be added here.
    """
    print(f"[GlyphVisualizer] Externalizing token: {token}")
    glyph_image = generate_glyph_image(token, output_dir)
    if glyph_image:
        print(f"[GlyphVisualizer] Token '{token}' externalized with image at: {glyph_image}")
    else:
        print(f"[GlyphVisualizer] Failed to externalize token: {token}")

if __name__ == "__main__":
    # Example usage:
    token_data = {
        "token": "truth",     # Token name
        "frequency": 5,       # Frequency for agency gate decisions
        "weight": 10          # Symbolic weight for prioritization
    }

    # This would typically be triggered from agency gate decisions in the recursive process
    externalize_token(token_data["token"], token_data)
