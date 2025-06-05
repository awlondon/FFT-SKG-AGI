# visualizers/hlsf.py
import matplotlib.pyplot as plt
import numpy as np
import json
import time
import os
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import sys
import imageio
import keyboard  # For hotkey-based camera mode switching

# Add parent directory to path to allow importing from main package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hlsf_camera import HLSFCamera
from agency_ticker_overlay import load_agency_decisions

# Configuration constants
STATE_CACHE = "hlsf_state_cache.json"
FRAME_DIR = "HLSF_frames/"
VIDEO_OUTPUT = "hlsf_evolution.mp4"

class HLSFVisualizer:
    """Visualizer for the High-Level Symbolic Field (HLSF)."""
    
    def __init__(self, canvas=None, engine=None):
        self.canvas = canvas
        self.engine = engine
        self.camera = HLSFCamera()
        self.trails = {}  # token_id: list of coords
        self.frame_count = 0  # For frame recording
        self.positions = {}  # Store token positions for rendering
        self.fig = None
        
    def update_visualizer(self, token_states, identity_core_token=None, frame=None):
        """Update the visualizer with the current token states."""
        center = self.camera.get_center(token_states, identity_core_token)
        self.camera.pan_to(center)
        self.camera.zoom_to(1.0)  # Adjust zoom dynamically if needed
        self._apply_camera_offset(token_states)
        self.render_hlsf(token_states, identity_core_token=identity_core_token, frame=frame)
        self.frame_count += 1

    def _apply_camera_offset(self, token_states):
        """Apply camera offset and zoom to token coordinates."""
        cx, cy = self.camera.center_coords
        zoom = self.camera.zoom
        for token in token_states:
            x, y = token["coords"]
            token["render_coords"] = ((x - cx) * zoom, (y - cy) * zoom)

    def render_hlsf(self, token_states, identity_core_token=None, layers=6, points_per_layer=300, frame=None):
        """Render the HLSF visualization with all components."""
        plt.figure(figsize=(12, 12))
        ax = plt.gca()
        ax.set_facecolor("black")

        self.render_tokens(ax, token_states, layers, points_per_layer)
        self.render_trails(ax, token_states)
        self.render_agency_overlay(ax, token_states)
        self.render_minimap(ax, token_states)
        self.render_overlay_text(ax, frame)
        self.render_legend(ax)

        # Add recording indicator overlay if recording
        if frame is not None:
            plt.text(
                0.95, 0.95, "● REC",
                transform=ax.transAxes,
                fontsize=12,
                color="red",
                backgroundcolor="#222222",
                bbox=dict(boxstyle="round", fc="#222", ec="none", alpha=0.6)
            )

        plt.title("Live High-Level Space Field (HLSF)", color="white")
        plt.axis("off")

        if frame is not None:
            self.save_frame(frame)

        plt.pause(0.1)
        plt.clf()

    def render_legend(self, ax):
        """Render the legend for token status colors."""
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Identity', markerfacecolor='#ffff00', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Recurrent', markerfacecolor='#00ffff', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Emergent', markerfacecolor='#ff00ff', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Dormant', markerfacecolor='#555555', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Pruned', markerfacecolor='#ff3333', markersize=10)
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=8, frameon=False, labelcolor='white')

    def render_tokens(self, ax, token_states, layers, points_per_layer):
        """Render token nodes in the field."""
        angle_step = 2 * np.pi / points_per_layer
        positions = {}
        agency_map = load_agency_decisions()

        for i, token in enumerate(token_states):
            layer = token["layer"]
            angle = (i % points_per_layer) * angle_step
            radius = 1.0 + layer * 0.5

            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            token["coords"] = (x, y)
            zx, zy = token["render_coords"]
            positions[token["token_id"]] = (zx, zy)

            # Custom color palette by token type
            color_map = {
                "identity": "#ffff00",   # Bright yellow
                "recurrent": "#00ffff",  # Cyan
                "emergent": "#ff00ff",   # Magenta
                "dormant": "#555555",    # Gray
                "pruned": "#ff3333"      # Red
            }
            status = token["status"]
            color = color_map.get(status, "#aaaaaa")
            size = 8 + token["intermodal_links"] * 10
            alpha = 0.9 if token["active"] else 0.3

            # Pulse effect for convergence events
            if token.get("highlight") == "pulse":
                plt.scatter(zx, zy, s=size * 1.4, color="#ffffff", alpha=0.2, linewidths=0)

            # Animate identity core glow
            if token["token_id"] == self.camera.follow_token_id:  # Identity root
                glow_radius = size + np.sin(self.frame_count * 0.3) * 5
                plt.scatter(zx, zy, s=glow_radius, color="#ffffaa", alpha=0.3, linewidths=0)

            plt.scatter(zx, zy, s=size, color=color, alpha=alpha, picker=True)

        self.positions = positions

    def render_trails(self, ax, token_states):
        """Render movement trails behind tokens."""
        for token in token_states:
            tid = token["token_id"]
            self.trails.setdefault(tid, []).append(token["coords"])
            self.trails[tid] = self.trails[tid][-20:]  # Keep only last 20 positions

            if len(self.trails[tid]) > 1:
                xs, ys = zip(*[((x - self.camera.center_coords[0]) * self.camera.zoom, 
                                (y - self.camera.center_coords[1]) * self.camera.zoom) for (x, y) in self.trails[tid]])
                ax.plot(xs, ys, color="gray", linewidth=0.5, alpha=0.4)

    def render_agency_overlay(self, ax, token_states):
        """Render agency decision overlays for tokens."""
        agency_map = load_agency_decisions()
        for token in token_states:
            tid = token["token_id"]
            if tid in agency_map:
                zx, zy = token["render_coords"]
                label = agency_map[tid][-1][:18] if agency_map[tid] else "?"
                ax.text(zx + 3, zy + 3, f"🧭 {label}", fontsize=6, color="#8ff")

    def render_minimap(self, ax, token_states):
        """Render a minimap in the corner of the visualization."""
        inset_ax = inset_axes(ax, width="25%", height="25%", loc="lower right")
        inset_ax.set_facecolor("#111111")
        inset_ax.axis("off")
        for t in token_states:
            x, y = t["coords"]
            mini_color = "#00ffff" if t["active"] else "#444444"
            inset_ax.scatter(x, y, s=3, color=mini_color, alpha=0.6)

    def render_overlay_text(self, ax, frame):
        """Render status text overlay."""
        overlay_text = f"Mode: {self.camera.mode.upper()}"
        if self.camera.mode == "follow_token" and self.camera.follow_token_id:
            overlay_text += f" | Following: {self.camera.follow_token_id}"
        overlay_text += f" | Recording: {'ON' if frame is not None else 'OFF'}"
        ax.text(
            0.02, 0.95, overlay_text,
            transform=ax.transAxes,
            fontsize=10,
            color="white",
            backgroundcolor="#222222",
            bbox=dict(boxstyle="round", fc="#222", ec="none", alpha=0.6)
        )

    def draw_convergence_paths(self, ax, token_states):
        """Draw lines between high-weight tokens and identity center."""
        for token in token_states:
            if token["status"] == "recurrent":
                x1, y1 = self.positions[token["token_id"]]
                for other_token in token_states:
                    if other_token["status"] == "recurrent" and other_token != token:
                        x2, y2 = self.positions[other_token["token_id"]]
                        ax.add_line(Line2D([x1, x2], [y1, y2], color="gray", alpha=0.3, linewidth=0.5))

    def save_frame(self, frame):
        """Save the current frame as an image for video creation."""
        os.makedirs(FRAME_DIR, exist_ok=True)
        plt.savefig(os.path.join(FRAME_DIR, f"frame_{frame:05d}.png"), dpi=150)

    def create_video(self):
        """Compile saved frames into a video."""
        images = sorted([os.path.join(FRAME_DIR, f) for f in os.listdir(FRAME_DIR) if f.endswith(".png")])
        if not images:
            print("[ERROR] No frames found to create video.")
            return
            
        try:
            with imageio.get_writer(VIDEO_OUTPUT, fps=10) as writer:
                for image in images:
                    writer.append_data(imageio.imread(image))
            print(f"[VIDEO SAVED] {VIDEO_OUTPUT}")
        except Exception as e:
            print(f"[ERROR] Failed to create video: {e}")

    def on_click(self, event):
        """Handle mouse clicks to select and follow a token."""
        if event.xdata is None or event.ydata is None:
            return
            
        x_click, y_click = event.xdata, event.ydata
        token_states = self.load_hlsf_state()
        min_dist = float("inf")
        nearest = None

        for token in token_states:
            if "render_coords" not in token:
                continue
                
            zx, zy = token["render_coords"]
            dist = (zx - x_click) ** 2 + (zy - y_click) ** 2
            if dist < min_dist:
                min_dist = dist
                nearest = token

        if nearest:
            self.camera.set_mode("follow_token", nearest["token_id"])
            print(f"[🎯] Following token {nearest['token_id']}")

    def live_loop(self, delay=2.0, record=False):
        """Run the main visualization loop."""
        plt.ion()  # Enable interactive mode
        self.fig = plt.figure(figsize=(12, 12))
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        frame = 0
        recording = record  # Track recording state

        try:
            while True:
                try:
                    # Handle camera mode switching via hotkeys
                    if keyboard.is_pressed("1"):
                        self.camera.set_mode("identity_core")
                        print("[MODE] Switched to identity_core mode")
                        time.sleep(0.3)  # Debounce
                    if keyboard.is_pressed("2"):
                        self.camera.set_mode("follow_token")  # Will set default token
                        print("[MODE] Switched to follow_token mode")
                        time.sleep(0.3)  # Debounce
                    if keyboard.is_pressed("3"):
                        self.camera.set_mode("cluster_focus")
                        print("[MODE] Switched to cluster_focus mode")
                        time.sleep(0.3)  # Debounce
                    if keyboard.is_pressed("4"):
                        self.camera.set_mode("free")
                        print("[MODE] Switched to free mode")
                        time.sleep(0.3)  # Debounce

                    # Add hotkey for recentering to identity core
                    if keyboard.is_pressed("r"):
                        self.camera.set_mode("identity_core")
                        print("[🧭] Recentered on identity core.")
                        time.sleep(0.3)  # Debounce

                    # Toggle recording mode with "t"
                    if keyboard.is_pressed("t"):
                        recording = not recording
                        print(f"[🎥] Recording {'enabled' if recording else 'disabled'}.")
                        time.sleep(0.3)  # Debounce

                    token_states = self.load_hlsf_state()
                    self.update_visualizer(token_states, frame=frame if recording else None)
                    if recording:
                        frame += 1
                    time.sleep(delay)
                    
                except FileNotFoundError:
                    print("[WARNING] State cache file not found. Waiting...")
                    time.sleep(2)
                    
                except json.JSONDecodeError:
                    print("[WARNING] Invalid JSON in state cache. Waiting...")
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[ERROR] Visualization error: {e}")
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            print("[INFO] Visualization stopped by user.")
            if recording:
                self.create_video()

    def load_hlsf_state(self):
        """Load the current HLSF state from the cache file."""
        if not os.path.exists(STATE_CACHE):
            # Create a minimal state if none exists
            return [{"token_id": "default", "layer": 0, "status": "identity", 
                    "active": True, "intermodal_links": 1, "coords": (0, 0), 
                    "render_coords": (0, 0), "highlight": None}]
                    
        with open(STATE_CACHE, "r") as f:
            return json.load(f)


def launch_hlsf_dashboard(canvas=None, engine=None, record=False):
    """
    Launch the HLSF dashboard as a standalone window.
    """
    visualizer = HLSFVisualizer(canvas=canvas, engine=engine)
    print("[🚀] Launching HLSF Dashboard...")
    visualizer.live_loop(record=record)


# Standalone execution
if __name__ == "__main__":
    launch_hlsf_dashboard(record=False)