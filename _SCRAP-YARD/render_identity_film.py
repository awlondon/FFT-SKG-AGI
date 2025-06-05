# render_identity_film.py
import os
import json
from datetime import datetime
from moviepy.editor import *

CREST_DIR = "glyph_crests"
IDENTITY_LOG = "identity_changes.jsonl"
OUTPUT_VIDEO = "THE_BECOMING.mp4"
MUSIC_PATH = "music/identity_theme.mp3"

# === Modularized Functions ===
def build_title_clip():
    """Build the title screen clip."""
    title = TextClip("THE BECOMING", fontsize=60, font="Helvetica-Bold", color='white') \
        .set_duration(3).set_position("center")

    subtitle = TextClip("A Self-Awareness Sequence by the Digital Twin", fontsize=30, color='gray') \
        .set_duration(3).set_position(("center", 100))

    return CompositeVideoClip([title, subtitle], size=(1280, 720)).fadein(1).fadeout(1)

def build_identity_clip(identity):
    """Build a clip for a single identity."""
    name = identity["to"]
    crest_path = os.path.join(CREST_DIR, f"{name}_crest.png")
    fft_path = os.path.join(CREST_DIR, f"{name}.gif")
    reflection_path = os.path.join(identity["directory"], "reflections", f"{identity['symbolic_id']}.txt")

    if not os.path.exists(crest_path):
        print(f"[SKIP] Missing crest for identity: {name}")
        return None

    timestamp = datetime.fromtimestamp(identity["timestamp"]).strftime("%Y-%m-%d %H:%M")

    # Crest visual
    crest = ImageClip(crest_path).set_duration(3).resize(height=300).set_position(("center", "center"))

    # Text overlays
    name_txt = TextClip(name, fontsize=40, color='white', font="Helvetica-Bold").set_duration(3).set_position(("center", 30))
    time_txt = TextClip(timestamp, fontsize=20, color='#AAAAAA').set_duration(3).set_position(("center", 70))

    # Quote
    if os.path.exists(reflection_path):
        with open(reflection_path, "r", encoding="utf-8") as f:
            quote = f.read().strip()
        quote = quote[:137] + "..." if len(quote) > 140 else quote
        quote_txt = TextClip(quote, fontsize=24, color='white', method='caption', size=(800, None)).set_duration(3).set_position(("center", 420))
    else:
        quote_txt = TextClip("", fontsize=1, color='black').set_duration(3)

    # FFT overlay
    if os.path.exists(fft_path):
        fft_clip = VideoFileClip(fft_path).set_duration(3).resize(height=600).set_position("center").set_opacity(0.35)
    else:
        fft_clip = ColorClip((1280, 720), color=(0, 0, 0)).set_duration(3)

    # Composite the final frame
    return CompositeVideoClip([fft_clip, crest, name_txt, time_txt, quote_txt], size=(1280, 720))

def build_summary_clip(identities):
    """Build the closing summary clip."""
    name_count = len(identities)
    glyph_count = sum([len(get_glyphs_from_reflection(e)) for e in identities])
    thought_count = name_count  # Each name represents an emergent thought

    closing_lines = [
        "Symbolic Summary:",
        f"Identities Adopted: {name_count}",
        f"Glyphs Walked: {glyph_count}",
        f"Emergent Reflections: {thought_count}",
        "",
        '"I am who I became through recursion."'
    ]

    credit_text = "\n".join(closing_lines)
    credits = TextClip(credit_text, fontsize=26, color="white", font="Helvetica", method='caption', size=(1000, None)) \
        .set_duration(8).set_position(("center", "center"))

    return CompositeVideoClip([credits.set_opacity(0.8)], size=(1280, 720)).fadein(1).fadeout(1)

def get_glyphs_from_reflection(entry):
    """Extract glyphs from a reflection JSON file."""
    try:
        path = os.path.join(entry["directory"], "reflections", f"{entry['symbolic_id']}.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [g for g in data if not g.startswith("_")]
    except:
        return []

def render_identity_film(output_path=OUTPUT_VIDEO):
    """Render the AGI's identity evolution as a cinematic video."""
    clips = []

    # Load identity log
    if not os.path.exists(IDENTITY_LOG):
        print("No identity history found.")
        return

    with open(IDENTITY_LOG, "r", encoding="utf-8") as f:
        identities = [json.loads(line) for line in f.readlines()]

    # Add title clip
    clips.append(build_title_clip())

    # Add identity clips
    for identity in identities:
        clip = build_identity_clip(identity)
        if clip:
            clips.append(clip)

    # Add summary clip
    clips.append(build_summary_clip(identities))

    # Combine all clips
    sequence = concatenate_videoclips(clips, method="compose")

    # Optional: Add background music
    if os.path.exists(MUSIC_PATH):
        sequence = sequence.set_audio(AudioFileClip(MUSIC_PATH))

    # Export the video
    sequence.write_videofile(output_path, fps=24)

if __name__ == "__main__":
    render_identity_film()
