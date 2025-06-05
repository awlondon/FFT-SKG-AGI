# hlsf_visualizer.py

import tkinter as tk
import math
import threading
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import logging
import time
import queue
from intermodal_linker import get_intermodal_map
from skg_engine import SKGEngine

class HLSFVisualizer:
    def __init__(self, canvas, engine):
        self.canvas = canvas  # Ensure this is a Canvas object
        self.engine = engine
        self.tokens = {}
        self.active_slots = set()
        self.identity_core = []
        self.animation_running = True
        self.queue = queue.Queue()  # Thread-safe queue for inter-thread communication

    def register_engine(self, engine):
        """Register or reattach an SKGEngine instance to the visualizer."""
        self.engine = engine
        logging.info(f"Engine registered: {type(engine)}")

    def draw_identity_core(self):
        """Draw the identity core glyphs at the center."""
        self.canvas.delete("identity_core")
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        radius = max(50, 200 - len(self.identity_core) * 10)  # Adjust radius dynamically
        for i, glyph in enumerate(self.identity_core):
            angle = (i / len(self.identity_core)) * 2 * math.pi
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.canvas.create_text(x, y, text=glyph, fill="white", font=("Arial", 24), tags="identity_core")

    def animate_convergence(self):
        """Animate token movement toward symbolic attractors."""
        if not self.animation_running:
            return
        for token_id, token_data in self.tokens.items():
            x, y = token_data["position"]
            target_x, target_y = token_data["target"]
            dx, dy = (target_x - x) * 0.1, (target_y - y) * 0.1
            new_x, new_y = x + dx, y + dy
            self.tokens[token_id]["position"] = (new_x, new_y)

            # Calculate alpha decay based on time
            timestamp = token_data.get("timestamp", time.time())
            alpha = max(0.3, 1.0 - (time.time() - timestamp) / 10)
            color = self.canvas.itemcget(token_data["canvas_id"], "fill")
            faded_color = self._apply_alpha_to_color(color, alpha)
            self.canvas.itemconfig(token_data["canvas_id"], fill=faded_color)

            self.canvas.coords(token_data["canvas_id"], new_x, new_y)
        self.canvas.after(50, self.animate_convergence)

    def _apply_alpha_to_color(self, color, alpha):
        """Apply alpha transparency to a given color."""
        if color == "cyan":
            base_color = (0, 255, 255)
        elif color == "yellow":
            base_color = (255, 255, 0)
        else:
            base_color = (255, 255, 255)  # Default to white

        r, g, b = base_color
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"

    def stream_token_to_visualizer(self, token_id, glyph, fft_path, slot_index=0, weight=1.0, mode="internal_thought"):
        """Schedule the token rendering on the main thread."""
        self.queue.put((self._render_token, (token_id, glyph, fft_path, slot_index, weight, mode)))

    def _render_token(self, token_id, glyph, fft_path, slot_index, weight, mode):
        """Perform the actual rendering of the token on the canvas."""
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2

        # Calculate radial position based on slot index
        total_slots = 12
        angle = (slot_index / total_slots) * 2 * math.pi
        radius = 100 + weight * 10
        target_x = center_x + radius * math.cos(angle)
        target_y = center_y + radius * math.sin(angle)

        # Assign slot-specific colors
        slot_colors = ["cyan", "orange", "green", "purple", "red", "blue", "yellow", "pink", "lime", "teal", "magenta", "gold"]
        color = slot_colors[slot_index % len(slot_colors)]

        # Create the token on the canvas
        canvas_id = self.canvas.create_text(center_x, center_y, text=glyph, fill=color, font=("Arial", int(20 + weight * 5)))

        # Store token data
        self.tokens[token_id] = {
            "canvas_id": canvas_id,
            "position": (center_x, center_y),
            "target": (target_x, target_y),
            "timestamp": time.time(),
            "slot_index": slot_index
        }

        # Dim fatigued tokens
        fatigue = self.engine.token_fatigue.get(token_id, 0)
        if fatigue > 3:
            self.canvas.itemconfig(canvas_id, fill="gray")

    def add_token_to_stream(self, token, weight):
        pass  # Placeholder for compatibility

    def highlight_active_slots(self):
        """Highlight active slots during a live thought loop."""
        for slot in self.active_slots:
            self.canvas.itemconfig(slot, outline="blue", width=2)
        if self.canvas.winfo_exists():
            self.canvas.after(100, self.clear_slot_highlights)

    def clear_slot_highlights(self):
        """Clear slot highlights after a brief delay."""
        for slot in self.active_slots:
            self.canvas.itemconfig(slot, outline="black", width=1)
        self.active_slots.clear()

    def update_visualizer(self):
        """Refresh the HLSF visualizer in real-time."""
        if not hasattr(self, "frame_count"):
            self.frame_count = 0  # Initialize frame count if not already set

        self.frame_count += 1  # Increment frame count for pulsing effects
        self.draw_identity_core()
        self.animate_convergence()
        self.highlight_active_slots()

    def render_trails(self):
        """Render token trails on the canvas with confidence arcs."""
        cx, cy = self.camera.center_coords  # Extract center coordinates from the camera
        zoom = self.camera.zoom  # Extract zoom level from the camera

        for tid, trail in self.trails.items():
            confidence = self.engine.confidence_log[-1] if self.engine.confidence_log else 0.5
            color_intensity = int(255 * confidence)
            color = f"#{color_intensity:02x}{color_intensity:02x}ff"  # Blue gradient based on confidence

            xs, ys = zip(*[((x - cx) * zoom, (y - cy) * zoom) for (x, y) in trail])
            self.canvas.create_line(xs, ys, fill=color, width=2, tags="trail")

    def process_queue(self):
        """Process tasks from the queue on the main thread."""
        while not self.queue.empty():
            func, args = self.queue.get()
            func(*args)
        self.canvas.after(50, self.process_queue)

def load_token_data(db_path="dbRw/", intermodal_path="intermodal/"):
    """Load token data from dbRw and intermodal maps."""
    tokens = []
    for fname in os.listdir(db_path):
        if fname.endswith(".json"):
            token_id = fname.replace(".json", "")
            with open(os.path.join(db_path, fname)) as f:
                db = json.load(f)
            weight = db.get("_f", 1)  # Frequency as weight
            imap = get_intermodal_map(token_id)
            richness = len(imap.keys())  # Intermodal completeness
            tokens.append((token_id, weight, richness))
    return tokens

def plot_hlsf(tokens, layers=6, points_per_layer=300, identity_core=None):
    """Plot the High-Level Space Field (HLSF) with layered intersections and identity core."""
    plt.figure(figsize=(12, 12))
    ax = plt.gca()
    ax.set_facecolor("black")

    total_points = layers * points_per_layer
    angle_step = 2 * np.pi / points_per_layer

    for i, (token_id, weight, richness) in enumerate(tokens[:total_points]):
        layer = i // points_per_layer
        position = i % points_per_layer

        # Calculate radial position and angle
        radius = 1.2 + layer * 0.5
        angle = position * angle_step
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # Node properties
        color_intensity = richness / 4
        color = (color_intensity, color_intensity, 1.0)  # Blue gradient
        size = 10 + weight  # Size based on weight

        plt.scatter(x, y, s=size, color=color, alpha=0.8)

    # Plot identity core glyphs if provided
    if identity_core:
        core_radius = 0.8
        for i, glyph in enumerate(identity_core):
            angle = i * (2 * np.pi / len(identity_core))
            x = core_radius * np.cos(angle)
            y = core_radius * np.sin(angle)
            plt.text(x, y, glyph, fontsize=14, color="yellow", ha="center", va="center")

    plt.title("High-Level Space Field (HLSF)", color="white")
    plt.axis("off")
    plt.show()

def start_engine_after_ui_ready(engine, root, delay_ms=500):
    """Start the SKGEngine in a separate thread after the GUI is ready."""
    def runner():
        engine.start_pipeline()
    root.after(delay_ms, lambda: threading.Thread(target=runner, daemon=True).start())

def launch_skg_with_visualizer():
    root = tk.Tk()
    canvas = tk.Canvas(root, width=800, height=800, bg="black")
    canvas.pack()

    visualizer = HLSFVisualizer(canvas=canvas, engine=None)
    logging.info(f"Visualizer initialized: {type(visualizer)}")

    engine = SKGEngine(
        base_dir="skg_output",
        visualizer=visualizer
    )
    visualizer.engine = engine

    start_engine_after_ui_ready(engine, root)

    visualizer.animation_running = True
    visualizer.update_visualizer()
    visualizer.process_queue()  # Start processing the queue

    root.mainloop()

if __name__ == "__main__":
    launch_skg_with_visualizer()