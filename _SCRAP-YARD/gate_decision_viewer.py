# gate_decision_viewer.py
import os
import json
import time
import tkinter as tk
from tkinter import ttk

class GateDecisionViewer:
    def __init__(self, parent_frame, log_path="gate_decision_log.jsonl", usage_path="_gate_usage.json", max_entries=50, refresh_interval=3000):
        self.frame = tk.Frame(parent_frame, bg="black")
        self.log_path = log_path
        self.usage_path = usage_path  # Path to gate usage data
        self.max_entries = max_entries
        self.refresh_interval = refresh_interval
        self.last_seen_timestamp = 0

        title = tk.Label(self.frame, text="Agency Gate Timeline", fg="white", bg="black", font=("Consolas", 12, "bold"))
        title.pack(anchor="w", padx=10, pady=(6, 2))

        self.canvas = tk.Canvas(self.frame, bg="black", height=200, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.inner_frame = tk.Frame(self.canvas, bg="black")

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.frame.pack(fill="both", expand=True)

        self.update_view()
        self.frame.after(self.refresh_interval, self.auto_refresh)

    def auto_refresh(self):
        self.update_view()
        self.frame.after(self.refresh_interval, self.auto_refresh)

    def update_view(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(self.log_path):
            return

        # Load gate usage data
        gate_usage = {}
        if os.path.exists(self.usage_path):
            with open(self.usage_path, "r", encoding="utf-8") as f:
                try:
                    gate_usage = json.load(f)
                except json.JSONDecodeError:
                    pass

        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-self.max_entries:]

        for line in reversed(lines):
            try:
                entry = json.loads(line.strip())
                gate = entry["gate"]
                decision = entry["decision"]
                timestamp = entry["timestamp"]
                confidence = entry.get("confidence", 1.0)  # range: 0.0–1.0
                time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
                symbol = "🔓" if decision == "allow" else "🔒"

                # Highlight repeated gates
                repeat_count = gate_usage.get(gate, 0)
                repeat_text = f" (x{repeat_count})" if repeat_count > 1 else ""

                # Color-code by glyph class or decision
                glyph_class_colors = {
                    "allow": "#44ff44",
                    "block": "#ff4444",
                    "default": "#cccccc"
                }
                base_color = glyph_class_colors.get(decision, glyph_class_colors["default"])

                label = tk.Label(
                    self.inner_frame,
                    text=f"{time_str} {symbol} {gate.replace('_', ' ')}{repeat_text}",
                    fg=base_color,
                    bg="black",
                    font=("Consolas", 10),
                    anchor="w"
                )
                label.pack(fill="x", anchor="w", padx=10)

                if timestamp > self.last_seen_timestamp:
                    self.animate_modulated_glow(label, confidence, gate, decision)

            except json.JSONDecodeError:
                continue

        if lines:
            try:
                latest = json.loads(lines[-1])
                self.last_seen_timestamp = latest["timestamp"]
            except:
                pass

        # Enable runtime AGI reflection
        self.reflect_on_common_gates(gate_usage)

    def reflect_on_common_gates(self, gate_usage):
        if not gate_usage:
            return

        most_common_gate = max(gate_usage, key=gate_usage.get, default=None)
        if most_common_gate:
            reflection = f"Why did I allow {most_common_gate} {gate_usage[most_common_gate]} times...?"
            print(reflection)  # Replace with AGI reflection logic

    def animate_modulated_glow(self, widget, confidence, gate, decision, steps=6, interval=100):
        # Dynamic hue mod based on gate type
        gate_colors = {
            "go_deep": "#33ccff",
            "be_creative": "#cc99ff",
            "prioritize_output": "#ffcc66",
            "prioritize_thought": "#66ff99",
            "be_spontaneous": "#ff99aa",
            "refine_voice": "#ccccff"
        }
        base = gate_colors.get(gate, "#44ff44" if decision == "allow" else "#ff4444")
        def adjust(hex_color, factor):
            r = max(0, min(255, int(int(hex_color[1:3], 16) * factor)))
            g = max(0, min(255, int(int(hex_color[3:5], 16) * factor)))
            b = max(0, min(255, int(int(hex_color[5:7], 16) * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"

        glow_colors = [adjust(base, 1.5), adjust(base, 1.2), base, adjust(base, 1.2), adjust(base, 1.5)]
        glow_intensity = min(max(confidence, 0.2), 1.0)
        pause = int(interval * (1.1 - glow_intensity))

        def glow(i=0):
            if i < len(glow_colors):
                widget.config(fg=glow_colors[i])
                widget.after(pause, lambda: glow(i + 1))

        glow()
