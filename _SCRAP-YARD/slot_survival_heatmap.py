# slot_survival_heatmap.py (interactive version)

import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from utils import SIGIL_GLYPHS
from PIL import Image, ImageTk
import tkinter as tk
import os
import logging

PRUNE_SUMMARY_PATH = "prune_summary.json"
HEATMAP_IMG = "slot_survival_heatmap.png"

def load_prune_data():
    if not os.path.exists(PRUNE_SUMMARY_PATH):
        logging.warning(f"Prune summary not found at {PRUNE_SUMMARY_PATH}")
        # Create an empty file as a fallback
        with open(PRUNE_SUMMARY_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    with open(PRUNE_SUMMARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_agency_details_for_glyph(glyph):
    decisions = {"severed": [], "kept": []}
    try:
        with open("agency_log.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("decision") in ["sever", "keep"] and entry.get("action") in ["prune_stack", "prune_reflect"]:
                    if entry["decision"] == "sever":
                        decisions["severed"].append(entry["token_id"])
                    elif entry["decision"] == "keep":
                        decisions["kept"].append(entry["token_id"])
    except:
        pass
    return decisions

def show_glyph_details(glyph):
    details = load_agency_details_for_glyph(glyph)
    window = tk.Toplevel()
    window.title(f"Glyph {glyph} – Pruning Summary")

    tk.Label(window, text=f"Sigil: {glyph}", font=("Consolas", 12, "bold")).pack()
    tk.Label(window, text="Kept Tokens:", fg="green").pack()
    tk.Message(window, text=", ".join(str(t) for t in details["kept"]), width=400).pack()

    tk.Label(window, text="Severed Tokens:", fg="red").pack()
    tk.Message(window, text=", ".join(str(t) for t in details["severed"]), width=400).pack()

def plot_slot_survival_heatmap(save_only=False, embed_target=None):
    data = load_prune_data()
    severed_vals = [data.get(g, {}).get("severed", 0) for g in SIGIL_GLYPHS]
    kept_vals = [data.get(g, {}).get("kept", 0) for g in SIGIL_GLYPHS]

    cmap = plt.cm.RdYlGn
    norm = mcolors.Normalize(vmin=0, vmax=max(kept_vals + severed_vals) or 1)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_title("Sigil Slot Survival Heatmap", fontsize=14)

    boxes = {}

    for i, glyph in enumerate(SIGIL_GLYPHS):
        x = i % 10
        y = i // 10
        severed = severed_vals[i]
        kept = kept_vals[i]
        total = severed + kept

        color = cmap(norm(kept)) if total > 0 else "gray"
        rect = plt.Rectangle((x, -y), 1, 1, color=color, ec="black")
        ax.add_patch(rect)
        ax.text(x + 0.5, -y + 0.5, glyph, ha="center", va="center", fontsize=18)
        boxes[rect] = glyph

    def on_click(event):
        for rect, glyph in boxes.items():
            if rect.contains_point([event.x, event.y]):
                show_glyph_details(glyph)

    fig.canvas.mpl_connect("button_press_event", on_click)
    ax.set_xlim(0, 10)
    ax.set_ylim(-5, 0)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(HEATMAP_IMG)
    if not save_only:
        plt.show()

# For embedding, same function call can use save_only=True

def embed_heatmap_in_tk(parent_frame):
    try:
        plot_slot_survival_heatmap(save_only=True)
        img = Image.open(HEATMAP_IMG)
        img = img.resize((400, 200), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)

        label = tk.Label(parent_frame, image=photo)
        label.image = photo
        label.pack(side="bottom", padx=5, pady=5)
        return label
    except Exception as e:
        logging.error(f"Failed to embed heatmap: {e}")
        return None
