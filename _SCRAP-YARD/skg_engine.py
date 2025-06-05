# skg_engine

import os
import json
import time
import logging
import sys
from skg_thought_tracker import SKGThoughtTracker

from intermodal_linker import update_intermodal_map

# Configure logging to handle Unicode characters
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

# Example log to test Unicode output
logging.info("Unicode test: \U0001f701")

import codecs
import random
from collections import defaultdict
from phrase_loop_utils import PhraseLoop
from emergent_token_utils import EmergentTokenTracker
from phrase_replay_engine import PhraseReplayEngine

from fft_generator import generate_signal_fft_image_for_token
from relationship_types import RELATIONSHIP_TYPES

try:
    import avatar_window
except ImportError as e:
    logging.error(f"Failed to import 'avatar_window': {e}")
    avatar_window = None  # Fallback or handle gracefully

from symbolic_constants import GLOSSARY_SUFFIX, GLYPH_IMAGE_SIZE, PROTO_SIGILS
from utils import ensure_output_stream_exists
import tkinter as tk
from tkinter import filedialog
from trainers.dt_trainer import DTTrainer
from symbolic_training_selector import choose_training_files
from glyph_renderer import render_glyph_image
import sys
from functools import partial
import shutil
from utils import (
    populate_token_field,
    human_time,
    check_ffmpeg,
    snapshot_skg_state,
    log_phrase_candidate,
    update_token_heatmap,
    update_sigil_activity
)

class SKGEngine:
    def __init__(self, base_dir=None, max_rels_per_token=None, visualizer=None, training_files=None, gate_data=None):
        from token_utils import TokenUtils
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.max_rels = max_rels_per_token
        self.token_counter = 1
        self.token_map = {}
        self.id_map = {}
        self.freq_dirty = {}
        self.relationships = defaultdict(lambda: defaultdict(dict))
        self.token_freq = defaultdict(int)
        self.token_linked = defaultdict(int)
        self.processed_tokens = set()
        self.stop_requested = False
        self.visualizer = visualizer
        self.gate_data = gate_data
        self.thought_tracker = SKGThoughtTracker()
        self.tu = TokenUtils(thought_tracker=self.thought_tracker)

        # Initialize input_token_ids before using it
        self.input_token_ids = set()

        # Initialize the AgencyGateManager
        from agency_gate_manager import AgencyGateManager
        self.agency_manager = AgencyGateManager()

        # Pass the AgencyGateManager to the AGIDecidor
        from glyph_decision_engine import AGIDecidor
        self.agi_decidor = AGIDecidor(agi_callback=self.handle_agi_callback, agency_manager=self.agency_manager)

        # Initialize the EmergentTokenTracker with a valid gate_engine
        self.gate_engine = self.agency_manager  # Use AgencyGateManager as the gate engine
        self.emergent_tracker = EmergentTokenTracker(input_token_ids=self.input_token_ids, gate_engine=self.gate_engine)

        print(f"[INFO] Visualizer linked: {self.visualizer is not None}")

        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs("tokens_fft_img", exist_ok=True)
        os.makedirs("tokens_fft", exist_ok=True)

        self.total_tokens = 0
        self.start_time = time.time()
        self.recent_tokens = []
        self.token_weights = {}
        self.current_sigil = "🜁"
        self.training_files = training_files or []
        self.walk_trace = []
        self.token_fatigue = defaultdict(int)
        self.confidence_log = []

        self.phrase_tracker = PhraseLoop()
        self.phrase_replayer = PhraseReplayEngine()

        self.token_to_glyph = {}  # Initialize token-to-glyph mapping
        self.available_glyphs = PROTO_SIGILS # Example glyphs
        self.tokens = {}  # Store token data

        self.initialize_proto_sigils()

    def handle_agi_callback(self, decision, confidence, context):
        """
        Handle decisions made by the AGIDecidor.
        """
        print(f"[AGI CALLBACK] Decision: {decision}, Confidence: {confidence}, Context: {context}")
        # Example: Trigger specific actions based on the decision
        if decision == "process_token":
            token_id = context.get("token_id")
            self.process_token(self.id_map[token_id], token_id)
        elif decision == "halt":
            self.stop_requested = True
            print("[INFO] AGI requested to halt the engine.")

    def initialize_proto_sigils(self):
        """
        Initialize proto sigils and shuffle them for diversity.
        Ensure that each proto sigil is processed into an image and FFT.
        """
        logging.info("Initializing proto sigils...")
        from initialize_proto_sigils import initialize_proto_sigils
        proto_sigils = initialize_proto_sigils(self)
        
        if not proto_sigils:
            logging.error("No proto sigils were initialized. Falling back to default sigils.")
            proto_sigils = ["🜁", "🜂", "🜃", "🜄"]  # Example fallback sigils

        # Ensure proto_sigils is a list
        if isinstance(proto_sigils, dict):
            proto_sigils = list(proto_sigils.keys())  # Extract keys if it's a dictionary

        logging.info(f"[DEBUG] Proto sigils returned: {proto_sigils}")
        self.available_glyphs = proto_sigils
        random.shuffle(self.available_glyphs)  # Shuffle the list of glyphs
        logging.info(f"[INFO] Proto sigils initialized: {len(self.available_glyphs)} glyphs loaded.")

        # Process each proto sigil into an image and FFT
        from glyph_utils import generate_fft_image_for_token, ensure_glyph_db_exists, render_token
        for sigil in self.available_glyphs:
            try:
                logging.info(f"[INFO] Processing proto sigil: {sigil}")
                ensure_glyph_db_exists(sigil)  # Ensure glyph database entry exists
                
                # Render the sigil into an image
                img_path = os.path.join(self.base_dir, "glyph_images", f"{sigil}.png")
                logging.debug(f"[DEBUG] Calling render_token with glyph: {sigil}, size: {GLYPH_IMAGE_SIZE[0]}, output_path: {img_path}")
                render_token(
                    glyph=sigil,
                    size=GLYPH_IMAGE_SIZE[0],  # Pass the correct size as an integer
                    output_path=img_path       # Pass the output path separately
                )
                logging.info(f"[INFO] Image generated for proto sigil '{sigil}' at {img_path}")
                
                # Confirm the image exists
                if not os.path.exists(img_path):
                    logging.error(f"[ERROR] Image not found after rendering for sigil '{sigil}': {img_path}")
                    continue

                # Generate the FFT for the sigil
                fft_path = os.path.normpath(os.path.join(self.base_dir, "glyph_images/fft", f"{sigil}_fft.png"))
                logging.debug(f"[DEBUG] Calling generate_fft_image_for_token with input: {img_path}, output: {fft_path}")
                generate_fft_image_for_token(img_path, fft_path)

                # Confirm the FFT image exists
                if not os.path.exists(fft_path):
                    logging.error(f"[ERROR] FFT image not found after saving: {fft_path}")
                else:
                    logging.info(f"[INFO] FFT image successfully saved at: {fft_path}")
            except Exception as e:
                logging.error(f"[ERROR] Failed to process proto sigil '{sigil}': {e}")

    def start_pipeline(self):
        """
        Choose training files if not already set and proceed.
        If still none are selected, fallback to DTTrainer mode.
        """
        try:
            logging.info("Starting pipeline...")
            from glossary_utils import load_and_process_glossary, process_training_pair
            from symbolic_training_selector import choose_training_files  # assuming renamed GUI

            # Process proto sigils into images and FFTs
            self.initialize_proto_sigils()

            if not self.training_files:
                logging.info("[INFO] Waiting for user to select training files...")
                self.training_files = choose_training_files()

            if not self.training_files:
                logging.info("[INFO] No files selected — launching Digital Twin Trainer...")
                DTTrainer().run()
                return

            # Process each training file pair independently
            for pair in self.training_files:
                try:
                    gg_path = pair.get("gg") or pair.get("glossary")
                    if not gg_path:
                        logging.error(f"[ERROR] Missing 'gg' or 'glossary' key in training file pair: {pair}")
                        continue

                    if "_gg.json" in gg_path:
                        pack_name = os.path.basename(gg_path).replace("_gg.json", "")
                        self.base_dir = os.path.join("skg_" + pack_name)
                        os.makedirs(self.base_dir, exist_ok=True)

                    # Process tokens in the training file
                    self.process_training_file(gg_path)

                except Exception as e:
                    logging.error(f"[ERROR] Failed to process training file pair: {e}")

        except Exception as e:
            logging.error(f"[ERROR] Failed to start pipeline: {e}")

    def tokenize_levels(self, levels):
        for level in levels:
            for token in level:
                token_id = self.tu.create_token_with_thought_loop(token, level, engine=self)
                self.process_token(token, token_id)

        return len(levels)

    def process_training_files(self):
        from glossary_utils import load_and_process_glossary
        for pair in self.training_files:
            try:
                # Validate the training file pair
                if not isinstance(pair, dict):
                    logging.error(f"[ERROR] Invalid training file pair format: {pair}")
                    continue

                gg_path = pair.get("gg") or pair.get(GLOSSARY_SUFFIX)
                if not gg_path:
                    logging.error(f"[ERROR] Missing 'gg' or glossary key in training file pair: {pair}")
                    continue

                txt_path = pair.get("text") or pair.get(".txt")
                if not txt_path:
                    logging.error(f"[ERROR] Missing 'text' key in training file pair: {pair}")
                    continue

                if not os.path.exists(gg_path):
                    logging.warning(f"[WARNING] Glossary file not found: {gg_path}. Skipping this pair.")
                    continue

                logging.info(f"[INFO] Loading glossary: {gg_path}")
                glossary = load_and_process_glossary(gg_path, engine=self)

                # Ensure glossary is a dictionary with arrays of tokens
                if not isinstance(glossary, dict):
                    logging.error(f"[ERROR] Glossary format invalid: {type(glossary)}")
                    continue

                for glyph, token_data in glossary.items():
                    if not isinstance(token_data, list):
                        logging.error(f"[ERROR] Invalid token data for glyph '{glyph}': {token_data}")
                        continue
                    self._process_glossary_entry(glyph, token_data, gg_path)

                if not os.path.exists(txt_path):
                    logging.warning(f"[WARNING] Text file not found: {txt_path}. Skipping this pair.")
                    continue

                logging.info(f"[INFO] Processing corpus: {txt_path}")
                self.process_training_file(txt_path)
            except KeyError as e:
                logging.error(f"[ERROR] Missing key in training file pair: {e}. Pair: {pair}")
            except Exception as e:
                logging.error(f"[ERROR] Failed to process training file pair: {e}. Pair: {pair}")

    def _process_glossary_entry(self, glyph, token_data, source_file):
        """
        Process a single glossary entry and initialize its adjacency slots.
        """
        try:
            # Validate glyph and token_data
            if not glyph:
                logging.error(f"[ERROR] Missing glyph for glossary entry in {source_file}")
                return
            if not isinstance(token_data, list):
                logging.error(f"[ERROR] Invalid token data for glyph '{glyph}' in {source_file}: {token_data}")
                return

            # Iterate through each token in the token_data array
            for token in token_data:
                try:
                    # Validate token
                    if not token:
                        logging.warning(f"[WARNING] Empty token found for glyph '{glyph}' in {source_file}")
                        continue

                    # Create the token as a glossary token
                    token_id = self.tu._create_token(
                        token,
                        source_file=source_file,
                        is_glossary_token=True,
                        glyph=glyph
                    )

                    # Save glossary token to glossary_tokens directory
                    glossary_dir = os.path.join(self.base_dir, "glossary_tokens")
                    os.makedirs(glossary_dir, exist_ok=True)
                    glossary_path = os.path.join(glossary_dir, f"{token_id}.json")
                    with open(glossary_path, "w", encoding="utf-8") as f:
                        json.dump({"token": token, "glyph": glyph}, f, indent=2)

                    # Log the provided glyph for each token
                    from glyph_utils import process_glyph_impression
                    process_glyph_impression(glyph)

                    # Generate FFT image for the token
                    from glyph_utils import generate_fft_image_for_token
                    fft_image_path = generate_fft_image_for_token(token)

                    # Update intermodal map
                    update_intermodal_map(token_id, "glyph", glyph)
                    update_intermodal_map(token_id, "fft_image", fft_image_path)
                except KeyError as e:
                    logging.error(f"[ERROR] Missing key while processing token '{token}' for glyph '{glyph}': {e}")
                except Exception as e:
                    logging.error(f"[ERROR] Failed to process token '{token}' for glyph '{glyph}': {e}")
        except Exception as e:
            logging.error(f"[ERROR] Failed to process glossary entry for glyph '{glyph}': {e}")

    def process_training_file(self, txt_path):
        """
        Process a training file and create tokens with adjacency slots.
        """
        logging.info(f"[INFO] Processing training file: {txt_path}")
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            tokens = line.strip().split()
            for i, token in enumerate(tokens):
                # Extract 50-slot adjacency mapping
                adjacency_slots = {}
                for slot_index in range(1, 51):
                    slot_key = f"slot_{slot_index}"
                    adjacent_token_index = i + slot_index - 25  # Offset to center the current token
                    if 0 <= adjacent_token_index < len(tokens):
                        adjacency_slots[slot_key] = {"tokens": [tokens[adjacent_token_index]]}
                    else:
                        adjacency_slots[slot_key] = {"tokens": []}

                # Create the token with adjacency slots
                token_id = self.tu._create_token(token, source_file=txt_path, context_tokens=None)

                # Save SKG token to dbRw directory
                dbRw_dir = os.path.join(self.base_dir, "dbRw")
                os.makedirs(dbRw_dir, exist_ok=True)
                dbRw_path = os.path.join(dbRw_dir, f"{token_id}.json")
                with open(dbRw_path, "w", encoding="utf-8") as f:
                    json.dump({"_id": token_id, "_token": token, "_slots": adjacency_slots}, f, indent=2)

    def process_token(self, token, token_id):
        """
        Process a single token and assign a glyph if necessary.
        """
        try:
            self.update_token_freq_from_file(token_id)
            self.emergent_tracker.process_token(token, token_id)
            self.recent_tokens.append(token_id)
            if len(self.recent_tokens) > 3:
                self.recent_tokens = self.recent_tokens[-3:]

            # Force the AGI to associate the token with a glyph by showing it the token's FFT image
            fft_image_path = os.path.join(self.base_dir, "tokens_fft_img", f"{token}.png")  # Use token content
            if not os.path.exists(fft_image_path):
                logging.info(f"[INFO] Generating FFT image for token: {token} ({token_id})")
                generate_signal_fft_image_for_token(token, token_id)  # Pass token content and ID

            # Decide on a glyph for the token
            from glyph_decision_engine import decide_glyph_for_token 
            glyph = decide_glyph_for_token(token_id, self.agi_decidor)
            self.token_to_glyph[token_id] = glyph  # Store the glyph in the mapping
            from glyph_utils import process_glyph_impression
            process_glyph_impression(glyph)  # Log the glyph
            logging.info(f"[INFO] Glyph assigned for token '{token}': {glyph}")


            # Update the current sigil
            self.current_sigil = glyph

            # Update phrase tracker and visualizer
            self.phrase_tracker.update(
                token_id,
                self.token_weights,
                self.token_to_glyph,
                skg_db_path="tokens",
                current_sigil=self.current_sigil
            )
            self.phrase_replayer.observe_token(token_id)
            self.tu.stream_to_visualizer(token, token_id)
        except Exception as e:
            logging.error(f"[ERROR] Failed to process token '{token}' ({token_id}): {e}")

    def update_token_freq_from_file(self, token_id):
        """
        Update the frequency of a token by reading from a file or initializing it if not present.
        Also updates the token frequency in its dbRw file.
        """
        try:
            # Path to the token frequency file
            freq_file_path = os.path.join(self.base_dir, "token_frequencies.json")

            # Load existing frequencies if the file exists
            if os.path.exists(freq_file_path):
                with open(freq_file_path, "r", encoding="utf-8") as f:
                    token_frequencies = json.load(f)
            else:
                token_frequencies = {}

            # Update the frequency for the given token_id
            token_frequencies[token_id] = token_frequencies.get(token_id, 0) + 1

            # Save the updated frequencies back to the file
            with open(freq_file_path, "w", encoding="utf-8") as f:
                json.dump(token_frequencies, f, indent=2)

            # Update the in-memory frequency tracker
            self.token_freq[token_id] = token_frequencies[token_id]

            # Update the frequency in the token's dbRw file
            dbRw_dir = os.path.join(self.base_dir, "dbRw")
            db_path = os.path.join(dbRw_dir, f"{token_id}.json")

            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    db_data = json.load(f)

                db_data["_frequency"] = self.token_freq[token_id]

                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(db_data, f, indent=2)
        except Exception as e:
            logging.error(f"[ERROR] Failed to update token frequency for '{token_id}': {e}")


    def should_switch_slot(self, current_token, current_slot_id):
        """
        Decide whether to switch to a different slot.
        """
        # Example logic: Switch slots if the current slot has no more tokens to traverse
        current_slot = self.relationships.get(current_token, {}).get(current_slot_id, {})
        tokens_in_slot = current_slot.get("tokens", [])
        
        # Switch if the slot is empty or all tokens have been processed
        if not tokens_in_slot or all(token in self.processed_tokens for token in tokens_in_slot):
            logging.info(f"[INFO] Switching slot for token: {current_token}, slot: {current_slot_id}")
            return True
        
        return False

    def jump_to_glyph(self, glyph_id):
        """
        Jump to a glyph and start traversal from there.
        """
        from glyph_utils import get_glyph_for_token, process_glyph_impression
        # Example logic: Load glyph data and start traversal
        glyph_data = self.load_glyph_data(glyph_id)
        starting_token = glyph_data.get("example_token")
        if starting_token:
            glyph = get_glyph_for_token(starting_token)
            if glyph:
                process_glyph_impression(glyph)
            self.tu.recursive_walk(starting_token)


    def generate_self_reflection(self, gate_name):
        context_tokens = gate_name.split("_")
        return self.construct_symbolic_phrase(context_tokens + ["why", "now"])

    def construct_symbolic_phrase(self, tokens):
        if len(set(tokens)) < len(tokens):  # Repetition = symbolic loop
            return f"↻ {' → '.join(tokens)}"
        return ""  # Otherwise: remain silent

    def _save_dbRw_file(self, token_id):
        """Save the token's symbolic relationship file to dbRw/"""
        dbRw_dir = os.path.join(self.base_dir, "dbRw")
        os.makedirs(dbRw_dir, exist_ok=True)
        db_path = os.path.join(dbRw_dir, f"{token_id}.json")

        # Ensure 50 slots are initialized
        slots = self.relationships.get(token_id, {})
        for slot_index in range(1, 51):
            slot_key = f"slot_{slot_index}"
            if slot_key not in slots:
                slots[slot_key] = {"tokens": []}

        # Include glyph in the data
        data = {
            "_id": token_id,
            "_token": self.id_map.get(token_id, ""),
            "_frequency": self.token_freq.get(token_id, 1),
            "_glyph": self.tokens.get(token_id, {}).get("glyph"),
            "_slots": slots
        }

        # Save the data to the file
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _update_dbRw_file(self, token_id):
        """Update the token's symbolic relationship file in dbRw/ without overwriting existing data."""
        dbRw_dir = os.path.join(self.base_dir, "dbRw")
        os.makedirs(dbRw_dir, exist_ok=True)
        db_path = os.path.join(dbRw_dir, f"{token_id}.json")

        # Load existing data if the file exists
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {"_id": token_id, "_token": self.id_map.get(token_id, ""), "_frequency": 0, "_slots": {}}

        # Merge existing slots with new relationships
        slots = existing_data.get("_slots", {})
        new_slots = self.relationships.get(token_id, {})
        for slot_key, slot_data in new_slots.items():
            if slot_key not in slots:
                slots[slot_key] = slot_data
            else:
                # Merge tokens and update weight
                slots[slot_key]["tokens"] = list(set(slots[slot_key].get("tokens", []) + slot_data.get("tokens", [])))
                slots[slot_key]["weight"] = slots[slot_key].get("weight", 0) + slot_data.get("weight", 0)

        # Update frequency
        existing_data["_frequency"] = self.token_freq.get(token_id, existing_data["_frequency"])
        existing_data["_slots"] = slots

        # Update relation_type based on slot (distance from source token)
        for slot_key, slot_data in slots.items():
            distance = int(slot_key.split("_")[-1])  # Extract distance from slot key
            relation_type = f"distance_{distance}"
            slot_data["relation_type"] = relation_type

        # Save the updated data back to the file
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)


if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the SKG Engine.")
    parser.add_argument("--base_dir", type=str, default=None, help="Base directory for engine output.")
    parser.add_argument("--max_rels", type=int, default=None, help="Maximum relationships per token.")
    parser.add_argument("--visualizer", type=str, default=None, help="Visualizer module (if any).")
    parser.add_argument("--training_files", nargs="*", help="List of training files.")
    args = parser.parse_args()

    # Initialize the engine
    engine = SKGEngine(
        base_dir=args.base_dir,
        max_rels_per_token=args.max_rels,
        visualizer=args.visualizer,
        training_files=args.training_files,
    )

    # Start the engine pipeline
    try:
        print("[INFO] Starting the SKG Engine...")
        engine.start_pipeline()
    except KeyboardInterrupt:
        print("[WARNING] Engine stopped by user.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

