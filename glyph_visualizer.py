# glyph_visualizer.py

import os
import re
import hashlib
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Resolve the project root and set default font path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FONT_PATH = os.path.join(ROOT_DIR, "Symbola.ttf")

def generate_glyph_image(token, output_dir="modalities/images", font_path=DEFAULT_FONT_PATH):
    """
    Generate and save an image of a glyph corresponding to the given token.
    """
    print(f"[GlyphVisualizer] Generating glyph image for: {token}")

    # Create a hashed and sanitized filename
    hash_id = hashlib.sha1(token.encode()).hexdigest()[:8]
    safe_token = re.sub(r"[^a-zA-Z0-9_-]", "_", token)
    image_filename = f"{safe_token}_{hash_id}_sigil.png"
    image_path = os.path.join(output_dir, image_filename)
    os.makedirs(output_dir, exist_ok=True)

    # Image configuration
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
    # Example manual invocation (normally triggered from SKGEngine)
    token_data = {
        "token": "truth",
        "frequency": 5,
        "weight": 10
    }
    externalize_token(token_data["token"], token_data)
