"""Placeholder gesture display utilities."""

import tkinter as tk


_root: tk.Tk | None = None
_label: tk.Label | None = None


def _ensure_root() -> None:
    global _root, _label
    if _root is None:
        _root = tk.Tk()
        _root.title("Gesture")
        _label = tk.Label(_root, text="", font=("Arial", 24))
        _label.pack(padx=10, pady=10)
        _root.after(100, lambda: None)  # initial update


def display_gesture(gesture: str) -> None:
    """Display a simple textual gesture cue."""
    _ensure_root()
    assert _label is not None
    _label.config(text=gesture)
    _root.update()
