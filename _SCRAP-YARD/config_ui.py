# config_ui.py
import tkinter as tk
import time
import json
import os

# Shared expression config
EXPRESSION_MODES = {
    "text": True,
    "audio": True,
    "image": True,
    "glyphs": True,
    "fft": True
}

CONFIG_FILE = "expression_config.json"

def save_mode_state():
    """Save the current expression mode state to a JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(EXPRESSION_MODES, f, indent=2)

def load_mode_state():
    """Load the expression mode state from a JSON file if it exists."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            EXPRESSION_MODES.update(json.load(f))

# Load the state at the start
load_mode_state()

# TPS tracker shared state
tps_value = 0.0
_last_thought_time = time.time()

def update_tps():
    """
    Update the TPS (Thoughts Per Second) value based on the time elapsed since the last thought.
    """
    global tps_value, _last_thought_time
    now = time.time()
    elapsed = now - _last_thought_time
    if elapsed > 0:
        tps_value = 1.0 / elapsed
    _last_thought_time = now

def get_tps():
    """
    Get the current TPS value, rounded to two decimal places.
    """
    return round(tps_value, 2)

def add_tooltip(widget, text):
    """
    Add a tooltip to a widget to provide symbolic feedback about its functionality.
    """
    tooltip = tk.Toplevel(widget, bg="black", padx=5, pady=5)
    tooltip.overrideredirect(True)
    tooltip.withdraw()
    tk.Label(tooltip, text=text, bg="black", fg="white", font=("Arial", 10)).pack()

    def show_tooltip(event):
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

def launch_expression_config_ui():
    """
    Launch a live toggle panel for controlling Digital Twin expression modes with a real-time TPS display.
    """
    window = tk.Toplevel()
    window.title("Digital Twin Expression Controls")
    window.geometry("300x300")

    tk.Label(window, text="🧠 Expression Modes", font=("Arial", 14, "bold")).pack(pady=10)

    checkboxes = {}

    def toggle(key):
        EXPRESSION_MODES[key] = not EXPRESSION_MODES[key]
        save_mode_state()  # Save state whenever a toggle is changed
        print(f"[🎛️] {key} mode set to {EXPRESSION_MODES[key]}")

    # Fix lambda capture issue by using a helper function
    def make_toggle(key):
        return lambda: toggle(key)

    for key in EXPRESSION_MODES:
        var = tk.BooleanVar(value=EXPRESSION_MODES[key])
        cb = tk.Checkbutton(window, text=key.capitalize(), variable=var,
                            command=make_toggle(key))
        cb.pack(anchor='w', padx=20)
        checkboxes[key] = var

        tooltip_text = {
            "text": "Symbolic phrase output",
            "audio": "TTS voice synthesis",
            "image": "Image generation/association",
            "glyphs": "Visual glyph emission",
            "fft": "Spectral thought visual stream"
        }.get(key, "")
        add_tooltip(cb, tooltip_text)

    def select_all():
        for k in EXPRESSION_MODES:
            checkboxes[k].set(True)
            EXPRESSION_MODES[k] = True
        save_mode_state()

    def select_none():
        for k in EXPRESSION_MODES:
            checkboxes[k].set(False)
            EXPRESSION_MODES[k] = False
        save_mode_state()

    tk.Button(window, text="🔘 Enable All", command=select_all).pack(pady=4)
    tk.Button(window, text="🔇 Disable All", command=select_none).pack(pady=4)

    # TPS Live Display
    tps_label = tk.Label(window, text="TPS: 0.00", font=("Consolas", 16, "bold"))
    tps_label.pack(pady=12)

    def update_tps_label():
        tps_label.config(text=f"TPS: {get_tps():.2f}")
        window.after(1000, update_tps_label)

    update_tps_label()
    window.mainloop()
