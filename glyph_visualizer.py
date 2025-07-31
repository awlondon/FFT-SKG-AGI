import os
import re
import hashlib
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Determine default font path: environment variable first, then local files
if getattr(sys.modules.get("__main__"), "__file__", None):
    MAIN_DIR = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
else:
    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))

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


def generate_glyph_image(token: str, output_dir: str = "modalities/images", font_path: str | None = None) -> str | None:
    """
    Render a Unicode glyph into an image file.  The resulting PNG is saved
    into `output_dir` and the path returned.  If font loading or drawing
    fails, None is returned and a warning printed.
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
    width, height = 512, 512
    background_color = "white"
    text_color = "black"
    font_size = 220
    try:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            fallback = os.path.join("fonts", "Symbola.ttf")
            try:
                font = ImageFont.truetype(fallback, font_size)
            except Exception:
                print("[GlyphVisualizer] Warning: Could not load Symbola font — using default")
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


def externalize_token(token: str, token_data: dict, output_dir: str = "modalities/images") -> None:
    """
    Externalize a token by generating its glyph image.  Additional
    modalities (like FFT or audio) can be added here.
    """
    print(f"[GlyphVisualizer] Externalizing token: {token}")
    glyph_image = generate_glyph_image(token, output_dir)
    if glyph_image:
        print(f"[GlyphVisualizer] Token '{token}' externalized with image at: {glyph_image}")
    else:
        print(f"[GlyphVisualizer] Failed to externalize token: {token}")


if __name__ == "__main__":
    # Example usage
    token_data = {
        "token": "truth",
        "frequency": 5,
        "weight": 10
    }
    externalize_token(token_data["token"], token_data)