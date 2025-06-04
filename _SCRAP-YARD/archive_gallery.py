# archive_gallery.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import subprocess
from datetime import datetime
from reactivate_identity import reactivate_identity

INDEX_FILE = "symbolic_archive_index.jsonl"

def render_identity_tile(canvas, entry, x, active_identity=None):
    """Render a single identity tile on the canvas."""
    name = entry["name"]
    glyphs = " ".join(entry["glyphs"])
    zip_path = entry["zip_path"]
    crest_path = f"{zip_path.replace('.zip', '')}/{name}_crest.png"
    idcard_path = f"{zip_path.replace('.zip', '')}/{name}_idcard.png"
    fft_path = f"{zip_path.replace('.zip', '')}/{name}.gif"
    timestamp = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")

    # Highlight active identity
    if active_identity and active_identity == name:
        canvas.create_rectangle(x, 50, x + 100, 350, outline="yellow", width=2)

    # Crest Preview
    if os.path.exists(crest_path):
        crest_img = Image.open(crest_path).resize((100, 100))
    else:
        crest_img = Image.new("RGB", (100, 100), "gray")
    crest_tk = ImageTk.PhotoImage(crest_img)
    canvas.create_image(x + 50, 100, image=crest_tk)
    if not hasattr(canvas, "images"):
        canvas.images = []
    canvas.images.append(crest_tk)

    # Name + glyphs
    canvas.create_text(x + 50, 210, text=name, fill="white", font=("Arial", 12))
    canvas.create_text(x + 50, 235, text=glyphs, fill="#ccc", font=("Arial", 10))
    canvas.create_text(x + 50, 260, text=timestamp, fill="#888", font=("Arial", 8))

    # Buttons
    def make_action(command, path):
        return lambda e: subprocess.Popen(command + [path]) if os.path.exists(path) else messagebox.showerror("Missing File", f"{path} not found.")

    btn_y = 290
    canvas.create_text(x + 50, btn_y, text="🎞️ Replay", fill="#6ef", font=("Arial", 10), tags=f"btn_replay_{x}")
    canvas.tag_bind(f"btn_replay_{x}", "<Button-1>", make_action(["ffplay", "-autoexit"], fft_path))

    canvas.create_text(x + 50, btn_y + 20, text="🗂️ Archive", fill="#aff", font=("Arial", 10), tags=f"btn_open_{x}")
    canvas.tag_bind(f"btn_open_{x}", "<Button-1>", make_action(["explorer" if os.name == "nt" else "xdg-open"], zip_path))

    canvas.create_text(x + 50, btn_y + 40, text="🪪 ID Card", fill="#fff", font=("Arial", 10), tags=f"btn_idcard_{x}")
    canvas.tag_bind(f"btn_idcard_{x}", "<Button-1>", make_action(["ffplay", "-autoexit"], idcard_path))

    canvas.create_text(x + 50, btn_y + 60, text="🔁 Reactivate", fill="#8f8", font=("Arial", 10), tags=f"btn_reactivate_{x}")
    canvas.tag_bind(f"btn_reactivate_{x}", "<Button-1>", lambda e, zp=zip_path: reactivate_identity(zp))

def launch_archive_gallery():
    if not os.path.exists(INDEX_FILE):
        print("[📭] No symbolic archive found.")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f.readlines()]

    root = tk.Tk()
    root.title("Symbolic Archive Gallery")
    root.geometry("1000x600")

    # Search bar
    search_var = tk.StringVar()
    active_identity = tk.StringVar(value="")

    def filter_entries(*args):
        search_term = search_var.get().lower()
        filtered_entries = [entry for entry in entries if search_term in entry["name"].lower() or any(search_term in glyph.lower() for glyph in entry["glyphs"])]
        render_gallery(filtered_entries)

    search_var.trace("w", filter_entries)
    search_entry = tk.Entry(root, textvariable=search_var, font=("Arial", 12))
    search_entry.pack(fill="x", padx=10, pady=5)

    # Canvas and scrollbar
    canvas = tk.Canvas(root, bg="black", width=1000, height=600, scrollregion=(0, 0, 2000, 600))
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scrollbar.pack(side="bottom", fill="x")
    canvas.configure(xscrollcommand=scrollbar.set)

    def render_gallery(filtered_entries):
        canvas.delete("all")
        x = 20
        for entry in filtered_entries:
            render_identity_tile(canvas, entry, x, active_identity.get())
            x += 140

    def reactivate_identity_with_highlight(zip_path):
        reactivate_identity(zip_path)
        for entry in entries:
            if entry["zip_path"] == zip_path:
                active_identity.set(entry["name"])
                break
        render_gallery(entries)

    # Override the reactivation button to include highlight logic
    for entry in entries:
        entry["reactivate"] = lambda zp=entry["zip_path"]: reactivate_identity_with_highlight(zp)

    render_gallery(entries)  # Initial render

    root.mainloop()

if __name__ == "__main__":
    launch_archive_gallery()
