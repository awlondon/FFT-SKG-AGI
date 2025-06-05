# main.py
import sys
import logging

# Reconfigure stdout/stderr to UTF-8 if needed
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configure console handler to suppress Unicode errors
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s', defaults={'errors': 'replace'}
))

# Add the console handler to the root logger
logging.getLogger().addHandler(console_handler)

# Ensure file logging uses UTF-8
file_handler = logging.FileHandler("skg_log.txt", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(file_handler)


import os
import io
import re
import sys
import json
import time
import argparse
import shutil
import math
import matplotlib

from symbolic_constants import PROTO_SIGILS
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import threading
import openai
from openai import OpenAI
from datetime import datetime
from PIL import Image as PilImage
from PIL import ImageDraw, ImageFont, ImageTk
import numpy as np
from scipy.fft import fft2, fftshift
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque, Counter
from tkinter import ttk, Tk, simpledialog, messagebox
import logging
from pydub.utils import which

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

from visual_replayer import VisualReplayer
from replay_analyzer import ReplayAnalyzer

# Import the SKGVisualizer from the new file
from skg_visualizer import SKGVisualizer

# Import the SymbolicConvergenceField class
from symbolic_convergence_field import SymbolicConvergenceField

# Import emergent thoughts handler
from emergent_thoughts import handle_emergent_token

# Import moviepy for video creation
from moviepy.editor import *

# Import identity style selector
from identity_style_selector import get_identity_style

# Import intermodal linker
from intermodal_linker import init_intermodal_map, update_intermodal_map

# Import intermodal inference system
from intermodal_inferencer import infer_missing_modalities

# Import reentrant_skg_stream
from reentrant_skg_stream import reentrant_skg_stream

from visualizers.hlsf_visualizer import HLSFVisualizer

# Import ThoughtLoopReentry
from replay_thought_loop import ThoughtLoopReentry

# Import utility functions
from utils import (
    human_time,
    log_phrase_candidate,
    update_token_heatmap,
    update_sigil_activity,
    snapshot_skg_state,
    maybe_log_emergent_token,
)

# Import glyph decision engine
from glyph_decision_engine import decide_glyph_for_token

# Import HLSF frame logger
from hlsf_frame_logger import log_hlsf_frame

from relationship_types import RELATIONSHIP_TYPES

# Import pruning engine
from prune_engine import evaluate_slot_for_pruning

# Import modularized functions
from glossary_utils import process_training_file_with_glossary
from config import GLOSSARY_FOLDER, BASE_DIR
from skg_utils import update_initial_skg_size, update_skg_size_during_processing
from file_stats import log_folder_stats, get_folder_stats
from reentrant_utils import reentrant_skg_ingest
from skg_validation import validate_skg_structure
from snapshot_utils import snapshot_skg_state
from glyph_utils import load_token_to_glyph_map, ensure_glyph_db_exists
from tokenizer import tokenize_wave
from analytics_utils import update_token_heatmap, update_sigil_activity
from visualizer_utils import start_hlsf_visualizer
from phrase_utils import log_phrase_candidate, stable_phrase_detected
from agency_gate_display import AgencyGateDisplay

# Import glyph sequence processor
from src.glyph_sequence.glyph_processor import load_glyph_sequence, load_glyph_metadata

# Import glyph data loader
from agency_gate_loader import load_agency_gates_json

# Import PhraseLoop
from phrase_loop_utils import PhraseLoop

# Import emergent token tracker
from emergent_token_utils import EmergentTokenTracker

# Import training file selector
from training_file_selector import choose_training_files

# Import FFT generator
from fft_generator import generate_signal_fft_image_for_token

# Import phrase bootstrapper
from phrase_bootstrapper import process_phrase_input

# Import SKGEngine
from skg_engine import SKGEngine

# Import AvatarWindow
from avatar_window import AvatarWindow

# Import glyph renderer
from glyph_renderer import render_glyph_image

# Import logging optimization functions
from logging_optimization import (
    log_fft_image_progress,
    log_existing_fft_images,
    log_output_stream_status,
    log_debug_summary,
)

from symbolic_visualizer_interface import SymbolicVisualizerInterface

from logging_config import setup_logging

from visualizer_log_handler import VisualizerLogHandler

# Import dotenv for environment variable management
from dotenv import load_dotenv

# Import glossary handler
from glossary_handler import load_glossary

# === CONFIG ===
MAX_TOKEN_LEN = 100_000_000
MAX_LEN = 100_000_000

# === BASE CONFIG ===
CORPUS_FILE = "__TRAINING_DATA__/___STARTER_PACKS__/sp01.txt"
PROJECT_NAME = "skg_sp01"

# Full project path
BASE_DIR = os.path.abspath(PROJECT_NAME)
TOKENS_DIR = os.path.join(BASE_DIR, "tokens")
DBRW_DIR = os.path.join(BASE_DIR, "tokens", "dbRw")
CORPUS_PATH = os.path.abspath(CORPUS_FILE)

# Load glyph glossary once and cache it
GLYPH_GLOSSARY_PATH = os.path.join(os.getcwd(), "glyph_glossary.json")
GLYPH_MAP = {}

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    logging.warning("[⚠️] OPENAI_API_KEY not set — GPT-based glossary generation will be disabled.")
    os.environ["OPENAI_API_KEY"] = ""
else:
    os.environ["OPENAI_API_KEY"] = openai_key

# Function to ensure OpenAI API key is available when needed
def ensure_openai_key():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("[❌] OPENAI_API_KEY is required for GPT glossary generation.")

REL_TYPE_SYMBOL = {rel_type: symbol for rel_type, symbol in RELATIONSHIP_TYPES}

# Function to initialize glossary with error handling
def initialize_glossary(gg_path, engine):
    from glossary_utils import load_and_process_glossary
    try:
        logging.debug(f"Glossary path: {gg_path}")
        glossary = load_and_process_glossary(gg_path, engine=engine)
    except FileNotFoundError:
        logging.error(f"Glossary file not found: {gg_path}")
        raise
    except ValueError as e:
        logging.error(f"Invalid glossary format: {e}")
        raise
    return glossary

# Check if the glyph glossary exists, if not, create it
if not os.path.exists(GLYPH_GLOSSARY_PATH):
    logging.debug(f"Creating empty glossary at {GLYPH_GLOSSARY_PATH}")
    with open(GLYPH_GLOSSARY_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)
    logging.info(f"Empty glyph glossary created at {GLYPH_GLOSSARY_PATH}")
else:
    logging.info(f"Glyph glossary found at {GLYPH_GLOSSARY_PATH}")

# Function to ensure all Tkinter windows are created in the main thread
def ensure_main_thread_tk():
    """Ensure all Tkinter windows are created in the main thread."""
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("Tkinter must be run in the main thread.")

# Ensure main thread for Tkinter
ensure_main_thread_tk()

def main():
    try:
        logging.debug("Attempting to load glossary...")
        glossary_data = get_glossary_data()  # Replace with actual data retrieval logic
        glossary = load_glossary(glossary_data)
        logging.debug("Glossary loaded successfully.")
    except ValueError as e:
        logging.error(f"Failed to load glossary: {e}")
        # Handle the error or exit gracefully

if __name__ == "__main__":
    # Add --headless mode support
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    args = parser.parse_args()

    print("\u2500" * 30)
    print("   \u263f  SKG SYMBOLIC ENGINE  \u263f")
    print("   \u21c5  Recursive Cognition   \u21c5")
    print("\u2500" * 30)

    if args.headless:
        engine = SKGEngine(visualizer=None)
        engine.start_pipeline()
    else:
        # Create visualizer and engine
        visualizer = SymbolicVisualizerInterface()
        engine = SKGEngine(visualizer=visualizer)

        # Link them together
        visualizer.link_engine(engine)

        # Create AvatarWindow on the main thread
        avatar = AvatarWindow(engine)
        engine.avatar_window = avatar

        # Run the symbolic engine in the background
        engine_thread = threading.Thread(target=engine.start_pipeline, daemon=True)
        engine_thread.start()

        # Launch GUI (blocking main thread)
        avatar.mainloop()

