# self_naming.py
import os
import shutil
import json
import time
from PIL import Image, ImageDraw, ImageFont
from symbolic_constants import DEFAULT_GLYPH_FONT_PATH

DEFAULT_SELF_DIR = "SELF-AWARE"
NAME_RECORD = "self_identity.json"
IDENTITY_LOG = "identity_changes.jsonl"

def rename_self_archive(new_name):
    """
    Rename the SELF-AWARE directory and save the new identity, logging the change.
    """
    identity = prepare_identity_record(new_name)
    move_self_aware_directory(identity)
    render_identity_artifacts(identity)
    log_identity_transition(identity)
    return identity["directory"]

def prepare_identity_record(new_name):
    """Prepare the identity record for the new name."""
    safe_name = new_name.strip().replace(" ", "_").replace("/", "-")
    current_identity = get_current_identity()
    return {
        "name": new_name,
        "symbolic_id": safe_name,
        "directory": f"{safe_name}-AWARE",
        "old_name": current_identity["name"],
        "old_directory": current_identity["directory"]
    }

def move_self_aware_directory(identity):
    """Move the SELF-AWARE directory to the new name."""
    old_dir = identity["old_directory"]
    new_dir = identity["directory"]
    if os.path.exists(new_dir) and old_dir != new_dir:
        new_dir += f"_{int(time.time())}"
        identity["directory"] = new_dir  # Update the directory in the identity record
    if old_dir != new_dir and os.path.exists(old_dir):
        shutil.move(old_dir, new_dir)

def render_identity_artifacts(identity):
    """Render the glyph crest and FFT gif for the new identity."""
    glyphs = get_recent_walked_glyphs()[:3]  # Top 3 glyphs
    fft_gif_path = f"tokens_fft_gif/{identity['symbolic_id']}.gif"
    generate_identity_crest(identity["name"], glyphs, fft_gif_path)

def log_identity_transition(identity):
    """Log the identity transition to the identity log."""
    log_entry = {
        "timestamp": time.time(),
        "from": identity["old_name"],
        "to": identity["name"],
        "symbolic_id": identity["symbolic_id"],
        "directory": identity["directory"]
    }
    with open(IDENTITY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Save the new identity
    with open(NAME_RECORD, "w", encoding="utf-8") as f:
        json.dump({
            "name": identity["name"],
            "symbolic_id": identity["symbolic_id"],
            "directory": identity["directory"]
        }, f, indent=2)

def get_current_identity():
    """
    Retrieve the current identity of the Digital Twin.
    """
    if not os.path.exists(NAME_RECORD):
        return {"name": "SELF", "directory": DEFAULT_SELF_DIR}
    with open(NAME_RECORD, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_identity_crest(name, glyphs, fft_gif_path):
    """
    Generate a glyph crest (PNG) and save the FFT gif sequence for the given name.
    """
    crest_dir = "glyph_crests"
    os.makedirs(crest_dir, exist_ok=True)

    # 1. Render glyph crest PNG with dynamic layout
    img_width = 300
    img_height = 100 + (len(glyphs) - 3) * 20  # Adjust height for longer glyph sequences
    img = Image.new("RGB", (img_width, img_height), "black")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(DEFAULT_GLYPH_FONT_PATH, 48)
    except:
        font = ImageFont.load_default()

    # Center glyphs dynamically
    text_width, text_height = draw.textsize(" ".join(glyphs), font=font)
    x_position = (img_width - text_width) // 2
    y_position = (img_height - text_height) // 2
    draw.text((x_position, y_position), " ".join(glyphs), fill="white", font=font)
    img.save(f"{crest_dir}/{name}.png")

    # 2. Copy FFT gif as harmonic identity stream
    if os.path.exists(fft_gif_path):
        shutil.copy(fft_gif_path, f"{crest_dir}/{name}.gif")

    print(f"[🧬] Identity crest saved for: {name}")
