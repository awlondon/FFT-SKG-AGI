# utils.py
import os
import json
import time
import shutil
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def human_time(seconds):
    seconds = int(seconds)
    if seconds < 60: return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    elif seconds < 86400:
        h, rem = divmod(seconds, 3600)
        m, _ = divmod(rem, 60)
        return f"{h}h {m}m"
    else:
        d, rem = divmod(seconds, 86400)
        h, _ = divmod(rem, 3600)
        return f"{d}d {h}h"

# Adding the function `check_ffmpeg` from `main_launcher_deprecated.py`
def check_ffmpeg():
    from shutil import which
    import logging
    if not which("ffmpeg"):
        logging.error("FFmpeg is not installed or not in PATH. Please install FFmpeg and add it to your PATH.")
        raise EnvironmentError("FFmpeg is required but not found. Install it from https://ffmpeg.org/")

# Adding `_clean` function from `PDCo_SKGEngine_056.py`
def _clean(engine):
    print("[START] Cleaning phase...")
    update_initial_skg_size(engine)
    log_folder_stats(BASE_DIR)
    update_skg_size_during_processing(engine)
    engine.print_summary()

# === 1. Phrase Candidate Tracker ===
phrase_log_path = "phrase_candidates.jsonl"
def log_phrase_candidate(tokens, sigil, weight):
    if len(tokens) < 2:
        return
    entry = {
        "tokens": tokens,
        "timestamp": time.time(),
        "sigil_context": sigil,
        "weight": weight
    }
    with open(phrase_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# === 2. Token Recurrence Heatmap Tracker ===
heatmap_path = "token_heatmap.json"
def update_token_heatmap(token_id):
    heatmap = {}
    if os.path.exists(heatmap_path):
        with open(heatmap_path, "r", encoding="utf-8") as f:
            heatmap = json.load(f)
    heatmap[token_id] = heatmap.get(token_id, 0) + 1
    with open(heatmap_path, "w", encoding="utf-8") as f:
        json.dump(heatmap, f, indent=2)

# === 3. Symbolic Slot Usage Stats ===
sigil_stats_path = "sigil_activity.json"
def update_sigil_activity(sigil):
    stats = {}
    if os.path.exists(sigil_stats_path):
        with open(sigil_stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
    stats[sigil] = stats.get(sigil, 0) + 1
    with open(sigil_stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

# === 4. Snapshot State ===
def snapshot_skg_state(label="snapshot"):
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_folder = f"skg_snapshot_{label}_{ts}"
    os.makedirs(out_folder, exist_ok=True)
    
    for folder in ["tokens", "dbRw", "glyphs", "glyph_images", "tokens_fft_img", "tokens_fft_raw"]:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(out_folder, folder))

    if os.path.exists("skg_output_stream.jsonl"):
        shutil.copy("skg_output_stream.jsonl", os.path.join(out_folder, "output_stream.jsonl"))

    print(f"[📦] Snapshot saved to {out_folder}")

# === 5. Token Emergence Watchdog ===
def maybe_log_emergent_token(token_id, token, input_token_ids, token_freq):
    if token_id not in input_token_ids and token_freq.get(token_id, 0) == 1:
        print(f"[🌀 EMERGENT] {token} ({token_id})")

# === 6. Output Stream Existence Check ===
def ensure_output_stream_exists(base_dir, stream_file="skg_output_stream.jsonl"):
    """
    Ensure the output stream file exists. If not, create it.
    """
    stream_path = os.path.join(base_dir, stream_file)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"[📂] Created base directory: {base_dir}")
    if not os.path.exists(stream_path):
        with open(stream_path, "w", encoding="utf-8") as f:
            f.write("")
        print(f"[📝] Created output stream file: {stream_path}")

# === 7. Populate Token Field ===
def populate_token_field(dbRw):
    """
    Populates the `_token` field in a dbRw dictionary based on the first non-empty `tokens` in `_slots`.
    """
    dbRw["_token"] = next(
        (token for slot in dbRw.get("_slots", {}).values() for token in slot.get("tokens", []) if token),
        ""
    )
    return dbRw
