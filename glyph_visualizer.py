# glyph_visualizer.py
import os
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None
    ImageDraw = None
    ImageFont = None
import hashlib
from datetime import datetime

def generate_glyph_image(token, output_dir="modalities/images", font_path="../Symbola.ttf"):
    """
    Generate and save an image of a glyph corresponding to the given token.
    """
    if not Image:
        print("[GlyphVisualizer] PIL not available. Skipping glyph image.")
        return None
    print(f"[GlyphVisualizer] Generating glyph image for: {token}")

    # Generate a hash for the token to create a unique filename
    hash_id = hashlib.sha1(token.encode()).hexdigest()[:8]
    image_path = os.path.join(output_dir, f"{token}_{hash_id}_sigil.png")
    os.makedirs(output_dir, exist_ok=True)

    width, height = 512, 512
    background_color = "white"
    text_color = "black"
    font_size = 220

    try:
        # Try to load the Symbola font from the provided path
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"[GlyphVisualizer] Error loading Symbola font: {e}")
            # Fallback if Symbola font is unavailable
            font = ImageFont.load_default()

        img = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(img)

        # Use textbbox for positioning the token in the center
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
    Externalize a token by generating its glyph image and possibly additional symbolic output.
    """
    print(f"[GlyphVisualizer] Externalizing token: {token}")
    glyph_image = generate_glyph_image(token, output_dir)

    # Additional processing can happen here, like generating FFT or other outputs
    if glyph_image:
        print(f"Token {token} externalized with glyph image at {glyph_image}")
    else:
        print(f"Failed to externalize token: {token}")

# Example usage:
token_data = {
    "token": "truth",  # Token name
    "frequency": 5,    # Frequency (useful for gate decisions)
    "weight": 10       # Weight (for decision making)
}

# This would typically be triggered from agency gate decisions in the recursive process
externalize_token(token_data["token"], token_data)
