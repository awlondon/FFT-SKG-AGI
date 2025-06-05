# visualizers/replayer.py
import os
import json
import time
import tkinter as tk
from tkinter import Canvas
from collections import deque
from agency_log_ticker import AgencyLogTicker
from PIL import Image, ImageTk

BASE_DIR = "skg_sp01"
OUTPUT_STREAM = os.path.join(BASE_DIR, "skg_output_stream.jsonl")
DBRW_DIR = os.path.join(BASE_DIR, "dbRw")
TOKENS_DIR = os.path.join(BASE_DIR, "tokens")
FRAME_DIR = "symbolic_frames"
AVATAR_SLOT_DIR = "avatar_slots"


class VisualReplayer:
    def __init__(self, root=None, canvas=None):
        self.external = (root is not None and canvas is not None)
        self.root = root if self.external else tk.Tk()

        self.canvas_width = 800
        self.canvas_height = 900
        self.scroll_speed = 20
        self.scroll_delay = 30
        self.feed_delay = 400

        self.glyph_lines = []
        self.token_ids = []
        self.live_buffer = deque(maxlen=100)
        self.index = 0
        self.paused = False

        self.canvas = canvas if self.external else Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="black")
        if not self.external:
            self.root.title("SKG Stream Replayer")
            self.canvas.pack()

        self.token_ids = self.load_token_ids()
        print(f"[BOOT] Loaded {len(self.token_ids)} token IDs")

        # Initial symbolic loading glyph
        self.glyph_lines.append({
            "text": "↻ loading...",
            "color": "#ffaa00",
            "y": self.canvas_height // 2
        })

        self.scroll_x = 0
        self.ticker = AgencyLogTicker(self.root, self.canvas, y_offset=500)

        self.root.after(self.scroll_delay, self.scroll_loop)

        if not self.external:
            self.root.bind("<space>", self.toggle_pause)
            self.root.bind("n", self.feed_next_token)
            self.root.after(1000, self.feed_tokens)
            self.root.mainloop()
        else:
            self.root.after(100, self.process_live_buffer)

        self.frame_id = 1
        self.total_frames = len([f for f in os.listdir(FRAME_DIR) if f.startswith("frame_")])

        self.setup_controls()
        self.render_current_frame()

    # ---------------------------
    #    CORE LOGIC
    # ---------------------------

    def load_token_ids(self):
        if not os.path.exists(OUTPUT_STREAM):
            print(f"[⚠️] Output stream not found: {OUTPUT_STREAM}")
            return []
        token_ids = []
        with open(OUTPUT_STREAM, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    token_ids.append(str(obj["id"]))
                except Exception as e:
                    print(f"[⚠️] Failed to parse line: {e}")
        return token_ids

    def feed_tokens(self):
        if self.paused:
            self.root.after(self.feed_delay, self.feed_tokens)
            return

        max_y = max((line["y"] for line in self.glyph_lines if isinstance(line["y"], (int, float))), default=0)
        if max_y < self.canvas_height - 120:
            if self.index < len(self.token_ids):
                token_id = self.token_ids[self.index]
                self.index += 1
                self.handle_token_id(token_id)

        self.root.after(self.feed_delay, self.feed_tokens)

    def handle_token_id(self, token_id):
        db_path = os.path.join(DBRW_DIR, f"{token_id}_dbRw.json")
        if not os.path.exists(db_path):
            return

        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        token = self.get_token_text(token_id)
        self.render_token(token_id, token, data)

    def get_color(self, weight):
        if weight >= 10:
            return "#ff4444"
        elif weight >= 5:
            return "#ffaa00"
        return "#ffffff"

    def render_token(self, token_id, token, data):
        glyph_spacing = 60
        visible_lines = [line for line in self.glyph_lines if isinstance(line["y"], (int, float)) and line["y"] > 0]
        if visible_lines:
            last_y = max(line["y"] for line in visible_lines)
            y_start = max(self.canvas_height - 60, last_y + 60)
        else:
            y_start = self.canvas_height - 60

        for slot_id, rels in data.items():
            if slot_id.startswith("_"):
                continue
            for glyph_symbol, rel_data in rels.items():
                # Ensure rel_data is a dictionary and extract the weight
                if isinstance(rel_data, dict) and "w" in rel_data:
                    weight = rel_data["w"]
                else:
                    print(f"[WARNING] Invalid relationship data for {glyph_symbol}: {rel_data}")
                    continue

                color = self.get_color(weight)
                main_text = f"{glyph_symbol}{weight} ({token})"
                subtext = f"   → connected to: {slot_id} [w={weight}]"

                self.glyph_lines.append({
                    "text": main_text,
                    "color": color,
                    "y": y_start
                })
                self.glyph_lines.append({
                    "text": subtext,
                    "color": "#888888",
                    "y": y_start + 28
                })
                y_start += glyph_spacing

    def scroll_loop(self):
        self.canvas.delete("all")
        updated = []

        center_y = self.canvas_height // 2
        fade_radius = 300

        for line in self.glyph_lines:
            line["y"] -= self.scroll_speed
            if line["y"] > -50:
                self.draw_fading_text(line, center_y, fade_radius)
                updated.append(line)

        self.glyph_lines = updated[-100:]
        self.scroll_x += self.scroll_speed
        self.render()
        self.root.after(self.scroll_delay, self.scroll_loop)

    def draw_fading_text(self, line, center_y, fade_radius):
        """Helper method to draw fading text based on distance from center."""
        dist = abs(line["y"] - center_y)
        fade = min(dist / fade_radius, 1.0)

        r, g, b = (255, 255, 255)
        if line["color"] == "#ff4444":
            r, g, b = (255, 68, 68)
        elif line["color"] == "#ffaa00":
            r, g, b = (255, 170, 0)
        elif line["color"] == "#888888":
            r, g, b = (136, 136, 136)

        r = int(r * (1 - fade))
        g = int(g * (1 - fade))
        b = int(b * (1 - fade))

        color = f"#{r:02x}{g:02x}{b:02x}"

        self.canvas.create_text(
            400, line["y"],
            text=line["text"],
            font=("Courier", 36, "bold"),
            fill=color
        )

    def get_token_text(self, token_id):
        for length_dir in os.listdir(TOKENS_DIR):
            path = os.path.join(TOKENS_DIR, length_dir, f"{token_id}.txt")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        return "?"

    def process_live_buffer(self):
        if self.live_buffer:
            token_id = self.live_buffer.popleft()
            self.handle_token_id(token_id)
        self.root.after(100, self.process_live_buffer)

    def render(self):
        self.ticker.render(self.scroll_x)

    def setup_controls(self):
        """
        Add navigation buttons for scrolling through frames.
        """
        toolbar = tk.Frame(self.root, bg="black")
        toolbar.pack(side="bottom", fill="x")

        tk.Button(toolbar, text="←", command=self.prev_frame).pack(side="left", padx=5)
        tk.Button(toolbar, text="→", command=self.next_frame).pack(side="right", padx=5)

    def prev_frame(self):
        """
        Navigate to the previous frame.
        """
        self.frame_id = max(1, self.frame_id - 1)
        self.render_current_frame()

    def next_frame(self):
        """
        Navigate to the next frame.
        """
        self.frame_id = min(self.total_frames, self.frame_id + 1)
        self.render_current_frame()

    def render_current_frame(self):
        """
        Render the current frame, including avatar, text, and other symbolic outputs.
        """
        self.canvas.delete("all")
        frame_folder = f"{FRAME_DIR}/frame_{self.frame_id:08d}/"
        avatar_path = f"{AVATAR_SLOT_DIR}/{self.frame_id:08d}.png"

        # Display Avatar
        self.render_avatar(avatar_path)

        # Display Text
        text_path = os.path.join(frame_folder, "text.txt")
        self.render_text(text_path)

    def render_avatar(self, avatar_path):
        """Helper method to render the avatar image."""
        if os.path.exists(avatar_path):
            img = Image.open(avatar_path).resize((320, 320), Image.NEAREST)
            tk_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(10, 10, anchor="nw", image=tk_img)
            self.canvas.image = tk_img

    def render_text(self, text_path):
        """Helper method to render the thought text."""
        if os.path.exists(text_path):
            with open(text_path, "r", encoding="utf-8") as f:
                thought = f.read()
            self.canvas.create_text(350, 50, text=thought, fill="#0f0", font=("Courier", 12), anchor="nw", width=600)

    # ---------------------------
    #    OPTIONAL CONTROLS
    # ---------------------------

    def toggle_pause(self, event=None):
        self.paused = not self.paused
        print(f"[REPLAYER] Paused: {self.paused}")

    def feed_next_token(self, event=None):
        if self.index < len(self.token_ids):
            token_id = self.token_ids[self.index]
            self.index += 1
            self.handle_token_id(token_id)


# Standalone entry point
def launch_visual_replayer():
    """Launch the visual replayer as a standalone application."""
    root = tk.Tk()
    root.title("Symbolic Knowledge Graph Replayer")
    replayer = VisualReplayer(root=root)
    return replayer
    
    
if __name__ == "__main__":
    launch_visual_replayer()