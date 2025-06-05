# main_launcher.py

import os
import time
import logging

# Global constants for glyph rendering
GLYPH_IMAGE_SIZE = FFT_IMAGE_SIZE  # Use the constant defined in symbolic_constants
FONT_PATH = "fonts/default_font.ttf"  # Path to the font file
GLYPH_IMAGE_DIR = "data/glyph_images"  # Directory to save rendered glyph images
import tkinter as tk
from shutil import which
from threading import Thread
from avatar_window import AvatarWindow, AgencyGateDisplay
from skg_engine import SKGEngine, choose_training_files
from glyph_renderer import render_glyph_image  # Ensure all references to render_glyph_image use the one from glyph_renderer.py
from agency_gate_loader import load_agency_gates_json
from hlsf_visualizer import HLSFVisualizer
from dt_trainer import DTTrainer
from utils_debug import (
    log_output_stream_status,
    log_debug_summary,
    log_fft_image_progress
)


def get_glyph_for_token(token):
    # Replace with actual glyph-token mapping logic
    glyph_mapping = {
        "token1": "glyph1",
        "token2": "glyph2",
    }
    return glyph_mapping.get(token, "default_glyph")


def check_ffmpeg():
    if not which("ffmpeg"):
        logging.error("FFmpeg is not installed or not in PATH. Please install FFmpeg and add it to your PATH.")
        raise EnvironmentError("FFmpeg is required but not found. Install it from https://ffmpeg.org/")


def process_output_stream(output_stream):
    if not output_stream:
        logging.warning("Output stream is empty. Check input data and processing logic.")
    else:
        logging.debug(f"Output stream contains data: {output_stream}")


def handle_missing_fft_images(missing_tokens):
    if missing_tokens:
        logging.warning(f"FFT images not found for tokens: {', '.join(missing_tokens)}")


def log_existing_fft_images(glyph, start_count, end_count):
    # Static variables to track the last glyph and loop count
    if not hasattr(log_existing_fft_images, "last_glyph"):
        log_existing_fft_images.last_glyph = None
        log_existing_fft_images.loop_count = 0

    # Increment the loop count
    log_existing_fft_images.loop_count += 1

    # Check if the glyph has changed
    if glyph != log_existing_fft_images.last_glyph:
        if log_existing_fft_images.last_glyph is not None:
            print(
                f"[INFO] Glyph changed from {log_existing_fft_images.last_glyph} to {glyph}. "
                f"Loops since last change: {log_existing_fft_images.loop_count} loops"
            )
        else:
            print(f"[INFO] Initial glyph: {glyph}")

        # Reset the loop count and update the last glyph
        log_existing_fft_images.loop_count = 1  # Reset to 1 for the new glyph
        log_existing_fft_images.last_glyph = glyph

    # Report the current glyph and loop count
    print(
        f"[DEBUG] Processing glyph: {glyph}, Start count: {start_count}, End count: {end_count}, "
        f"Current loop count: {log_existing_fft_images.loop_count}"
    )


def main():
    try:
        # Check if FFmpeg is installed
        check_ffmpeg()

        # Select training files
        selected_pairs = choose_training_files()

        # Ensure glyph_sequence folder exists
        os.makedirs("data/glyph_sequences/agency_gates", exist_ok=True)

        # Load agency gate data
        gate_data = load_agency_gates_json()

        if not selected_pairs:
            print("[WARNING] No training files selected.")
            print("[START] Digital Twin Training")
            
            # Start the Digital Twin Trainer
            trainer = DTTrainer()
            trainer.start()
        else:
            print("[INFO] Training files selected. Proceeding with SKG Engine initialization.")
            main.main_loop(selected_pairs, gate_data)


        # Initialize the Tkinter root for agency gate display
        root = tk.Tk()
        root_frame = tk.Frame(root)
        root_frame.pack(fill="both", expand=True)
        gate_display = AgencyGateDisplay(root_frame, gate_data)

        # Create the SKG engine and visualizer
        engine = SKGEngine(training_files=selected_pairs)
        visualizer = HLSFVisualizer(engine)
        engine.visualizer = visualizer  # Inject the visualizer into the engine

        # Launch the avatar window
        avatar_window = AvatarWindow()
        avatar_window_thread = Thread(target=avatar_window.run)
        avatar_window_thread.start()

        # Start token processing thought loops
        engine.process_phrase_input("foldmass erupts forward")

        # Simulated debugging hooks
        output_stream = []  # Replace with actual logic if needed
        process_output_stream(output_stream)

        missing_tokens = ["foldmass", "erupts", "forward"]
        handle_missing_fft_images(missing_tokens)

        import json
        from symbolic_constants import PROTO_SIGILS

        # Load sigils from PROTO_SIGILS
        sigils = PROTO_SIGILS

        for sigil in sigils:
            render_glyph_image(sigil)

        glyph = "🜲"
        start_count = 7636
        end_count = 7650
        log_existing_fft_images(glyph, start_count, end_count)

        output_stream_path = "skg_output_stream.jsonl"
        # Ensure the output stream file exists
        if not os.path.exists(output_stream_path):
            with open(output_stream_path, 'w') as f:
                pass  # Create an empty file

        log_output_stream_status(output_stream_path)

        debug_logs = ["STREAM b'IHDR'", "STREAM b'tEXt'", "STREAM b'pHYs'", "STREAM b'IDAT'"]
        log_debug_summary(debug_logs)

        log_fft_image_progress(glyph, count=50, total=250, delay=2)

        # Start the visualizer GUI
        visualizer.mainloop()

        # Wait for the avatar window thread to finish
        avatar_window_thread.join()

    except Exception as e:
        logging.error(f"[ERROR] Exception occurred: {e}")


if __name__ == "__main__":
    main()
