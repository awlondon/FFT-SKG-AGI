# agency_gate_ticker.py
import tkinter as tk
import json
import os
import time
import threading

class AgencyGateTicker(tk.Frame):
    def __init__(self, parent, log_path="gate_decision_log.jsonl", reflection_path="gate_reflections.jsonl", refresh_interval=2, on_gate_click=None):
        super().__init__(parent, bg="black")
        self.log_path = log_path
        self.reflection_path = reflection_path  # New reflection log path
        self.refresh_interval = refresh_interval  # seconds
        self.last_seen = 0
        self.on_gate_click = on_gate_click  # Callback when gate line clicked

        self.text = tk.Text(self, height=10, bg="black", fg="white", font=("Consolas", 10), wrap="none")
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")

        self.scroll = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")

        self.text.tag_bind("gate_entry", "<Button-1>", self._on_click)

        self.gate_entries = []  # Store entries for lookup

        threading.Thread(target=self._update_loop, daemon=True).start()

    def _update_loop(self):
        while True:
            self._load_new_entries()
            time.sleep(self.refresh_interval)

    def _load_new_entries(self):
        if not os.path.exists(self.log_path):
            return

        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[self.last_seen:]

        self.last_seen += len(lines)

        if not lines:
            return

        self.text.configure(state="normal")
        for line in lines:
            try:
                entry = json.loads(line.strip())
                ts = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"]))
                decision = entry["decision"]
                gate = entry["gate"]
                confidence = entry.get("confidence", 0.0)
                token = entry.get("token_id", "?")
                msg = f"[{ts}] {gate} → {decision.upper()} ({confidence:.2f}) :: {token}\n"
                color = "#66ff66" if decision == "allow" else "#ff4444"
                tag_start = self.text.index("end-1l")
                self.text.insert("end", msg)
                tag_end = self.text.index("end-1c")
                self.text.tag_add("gate_entry", tag_start, tag_end)
                self.text.tag_add(decision, tag_start, tag_end)
                self.text.tag_config("allow", foreground="#66ff66")
                self.text.tag_config("block", foreground="#ff4444")
                self.gate_entries.append(entry)
            except Exception:
                continue

        self._load_reflections()  # Load reflections after gate entries

        self.text.see("end")
        self.text.configure(state="disabled")

    def _load_reflections(self):
        if not os.path.exists(self.reflection_path):
            return

        with open(self.reflection_path, "r", encoding="utf-8") as f:
            reflections = f.readlines()

        for reflection in reflections:
            try:
                reflection_entry = json.loads(reflection.strip())
                # Process reflection entries if needed
                # Example: Add to UI or log
            except Exception:
                continue

    def _on_click(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        line = self.text.get(index + " linestart", index + " lineend")
        for entry in self.gate_entries:
            if entry["gate"] in line and entry["token_id"] in line:
                if self.on_gate_click:
                    self.on_gate_click(entry)
                break

        # Connect to engine.handle_gate_reflection()
        if hasattr(self, 'engine') and hasattr(self.engine, 'handle_gate_reflection'):
            self.engine.handle_gate_reflection(entry)