# glyph_utils.py

import logging
import os
import json
import hashlib
import numpy as np
from PIL import Image, ImageOps
from skg_engine import SKGEngine
from symbolic_constants import GLYPH_IMAGE_SIZE, PROTO_SIGILS, GLYPH_IMAGE_DIR, FFT_IMAGE_SIZE, GLYPH_IMG_FFT_DIR
from render_glyph import render_token  # Make sure this import is available
import sys



DEFAULT_GLYPH = "🜁"  # Default fallback glyph

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_DATA_DIR = os.path.join(BASE_DIR, "__TRAINING_DATA__")

GLYPH_IMAGE_DIR = "glyph_images"
os.makedirs(GLYPH_IMAGE_DIR, exist_ok=True)

import threading

# Global variables
_token_glyph_cache = None
_token_glyph_cache_lock = threading.Lock()

def get_token_glyph_cache():
    """
    Ensures that the global _token_glyph_cache is initialized before use.
    Returns the initialized _token_glyph_cache.
    """
    global _token_glyph_cache
    if _token_glyph_cache is None:
        with _token_glyph_cache_lock:
            if _token_glyph_cache is None:  # Double-checked locking
                _token_glyph_cache = load_token_to_glyph_map()
    return _token_glyph_cache

def ensure_glyph_db_exists(glyph, example_token=None):
    glyph_path = os.path.join(GLYPH_IMAGE_DIR, f"{glyph}.json")
    if os.path.exists(glyph_path):
        return
    data = {
        "_id": int(hashlib.md5(glyph.encode()).hexdigest(), 16) % 1000000,
        "_sigil": glyph,
        "_frequency": 0,
        "_slots": {}
    }
    if example_token:
        data["example_token"] = example_token
    with open(glyph_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_fft_image_for_token(input_path, output_path):
    """
    Generate an FFT image for a given token.
    """
    from fft_utils import normalize_and_generate_fft
    import os

    logging.debug(f"[DEBUG] Generating FFT for input: {input_path}, output: {output_path}")

    # Check if input image exists
    if not os.path.exists(input_path):
        logging.error(f"[ERROR] Input image not found: {input_path}")
        return None

    # Call the FFT generation function
    try:
        normalize_and_generate_fft(input_path, output_path)
        logging.info(f"[INFO] FFT image generated at: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"[ERROR] Failed to generate FFT for input: {input_path}. Error: {e}")
        return None

def get_glyph_id(glyph):
     token_id = ord(glyph)  # Assign a unique token_id based on the glyph's Unicode value
     return token_id

def load_token_to_glyph_map():
    token_to_glyph = {}
    for root, _, files in os.walk(TRAINING_DATA_DIR):
        for file in files:
            if file.endswith("_gg.json"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    try:
                        glyph_to_tokens = json.load(f)
                        for glyph, tokens in glyph_to_tokens.items():
                            token_id = get_glyph_id(glyph)
                            for token in tokens:
                                token_to_glyph[token.lower()] = glyph
                                ensure_glyph_db_exists(glyph, token)
                                generate_fft_image_for_token(glyph, token_id)  # Pass token_id to FFT generation
                    except json.JSONDecodeError as e:
                        print(f"Error loading glossary {file}: {e}")
    logging.info(f"[GLYPH] Loaded token-to-glyph map: {token_to_glyph}")
    return token_to_glyph

def process_glyph_impression(glyph):
    if glyph is None or not isinstance(glyph, str) or len(glyph) != 1:
        raise ValueError(f"Invalid glyph: {glyph}. Glyph must be a single character string.")

    jsonl_log_path = "symbolic_reflection_log.jsonl"  # New JSONL log file
    try:
        with open(jsonl_log_path, "a", encoding="utf-8") as jsonl_log_file:
            token_id = ord(glyph)

            # Save symbolic metadata
            db_path = f"glyphs/dbRw/{glyph}.json"
            if not os.path.exists(db_path):
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "_frequency": 1,
                        "_id": token_id,
                        "_sigil": glyph,
                        "_slots": {}
                    }, f, indent=2)

            # Save token ID to a text file
            token_path = f"glyphs/tokens/{glyph}.txt"
            if not os.path.exists(token_path):
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(str(token_id))

            token_id = get_glyph_id(glyph)

            generate_fft_image_for_token(glyph, token_id)

            # Write to JSONL log
            jsonl_log_file.write(json.dumps({
                "glyph": glyph,
                "token_id": token_id,
                "unicode": f"U+{ord(glyph):04X}"
            }) + "\n")

            from token_utils import TokenUtils
            tu = TokenUtils()  # Ensure TokenUtils is instantiated
            # Add token ID to create_token_with_thought loop
            tu.create_token_with_thought_loop(token_id)

            # Log processed sigil information
            print(f"[ok] Processed sigil: {glyph}, Token ID: {token_id}, U+{ord(glyph):04X}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to process glyph impression for {glyph}: {e}", exc_info=True)


# Example callback function
def agi_callback(decision, confidence, metadata):
    """
    Callback function to handle decisions made by the AGIDecidor.
    Logs the decision and interacts with the AgencyGateManager for further processing.

    Args:
        decision (bool): The decision made (True for allow, False for block).
        confidence (float): The confidence level of the decision.
        metadata (dict): Additional metadata related to the decision.
    """
    try:
        logging.info(f"[AGI_CALLBACK] Decision: {decision}, Confidence: {confidence}, Metadata: {metadata}")

        # Extract relevant metadata
        token_id = metadata.get("token_id", "unknown")
        interpretation = metadata.get("interpretation", {})
        gate_name = metadata.get("gate_name", "unknown")

        # Instantiate AgencyGateManager (ensure it's properly initialized in your context)
        from agency_gate_manager import AgencyGateManager
        agency_manager = AgencyGateManager()

        # Log the decision using the AgencyGateManager
        agency_manager._log_decision(
            gate_name=gate_name,
            token_id=token_id,
            decision=decision,
            confidence=confidence,
            glyphs=metadata.get("glyphs", ""),
            interpretation=interpretation
        )

        # Perform additional actions based on the decision
        if decision:
            logging.info(f"[AGI_CALLBACK] Positive decision for Token ID: {token_id}. Proceeding with allow actions.")
            # Add any specific actions for a positive decision here
        else:
            logging.info(f"[AGI_CALLBACK] Negative decision for Token ID: {token_id}. Proceeding with block actions.")
            # Add any specific actions for a negative decision here

    except Exception as e:
        logging.error(f"[ERROR] Failed in agi_callback: {e}", exc_info=True)

def get_glyph_for_token(token):
    """
    Retrieves the glyph associated with the given token. If no glyph is found,
    it assigns a glyph to the token. If assignment fails, the default glyph '🜁'
    is used as a fallback.
    """
    token_glyph_cache = get_token_glyph_cache()  # Use the getter function

    glyph = token_glyph_cache.get(token.lower())
    if glyph:
        logging.info(f"[GLYPH] Found glyph '{glyph}' for token: {token}")
        return glyph

    logging.info(f"[GLYPH] No glyph found in cache for token: {token}. Attempting to assign a new glyph.")
    
    # Properly instantiate AGIDecidor
    from glyph_decision_engine import AGIDecidor, decide_glyph_for_token
    from agency_gate_manager import AgencyGateManager
    agency_manager = AgencyGateManager()
    agi_decidor = AGIDecidor(agi_callback=agi_callback, agency_manager=agency_manager)
    
    glyph = decide_glyph_for_token(token, agi_decidor)
    if not glyph:
        glyph = DEFAULT_GLYPH  # Default fallback glyph

    with _token_glyph_cache_lock:
        token_glyph_cache[token.lower()] = glyph

    return glyph

def is_valid_token(token):
    return token and token.isalpha() and len(token) > 1

if __name__ == "__main__":
    test_glyph = "🜲"
    print(f"[GLYPH] Processing test glyph: {test_glyph}")
    generate_fft_image_for_token(test_glyph)