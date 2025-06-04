# initialize_proto_sigils.py
import sys
import io
import os
import logging  # Import logging module

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import numpy as np
from PIL import Image as PilImage
from PIL import ImageDraw, ImageFont

from render_glyph import render_token
from symbolic_constants import GLYPH_IMAGE_SIZE, GLYPH_IMG_FFT_DIR, PROTO_SIGILS, GLYPH_IMAGE_DIR, GLYPH_IMAGE_SIZE, FFT_IMAGE_SIZE, PROTO_SIGIL_TOKENS, GLYPH_FFT_DIR
from glyph_renderer import render_glyph_image

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to console
        logging.FileHandler("initialize_proto_sigils.log", encoding="utf-8")  # Log to file
    ],
    encoding="utf-8"  # Set encoding to UTF-8
)

def initialize_proto_sigils(engine):
    """
    Initialize proto sigils and ensure they are processed into images and FFTs.
    """
    logging.info("[INIT] Initializing proto sigils...")
    proto_sigils = {}

    # Ensure required directories exist
    os.makedirs(GLYPH_IMAGE_DIR, exist_ok=True)
    os.makedirs(GLYPH_IMG_FFT_DIR, exist_ok=True)

    for sigil in PROTO_SIGILS:
        try:
            from glyph_utils import ensure_glyph_db_exists, render_token, generate_fft_image_for_token

            # Ensure glyph database entry exists
            ensure_glyph_db_exists(sigil)

            # Render the sigil into an image
            img_path = os.path.join(GLYPH_IMAGE_DIR, f"{sigil}.png")
            if not os.path.exists(img_path):
                logging.info(f"[INFO] Rendering image for sigil '{sigil}'...")
                render_token(
                    glyph=sigil,
                    size=GLYPH_IMAGE_SIZE[0],  # Pass the correct size as an integer
                    output_path=img_path       # Pass the output path separately
                )

            # Confirm the image exists
            if not os.path.exists(img_path):
                logging.error(f"[ERROR] Image not found after rendering for sigil '{sigil}': {img_path}")
                continue

            # Generate the FFT spectral image
            fft_path = generate_fft_image_for_token(sigil, sigil)
            if fft_path:
                logging.info(f"[INFO] FFT generated for sigil '{sigil}' at {fft_path}")
            else:
                logging.error(f"[ERROR] FFT generation failed for sigil '{sigil}'")
        except Exception as e:
            logging.error(f"[ERROR] Failed to process proto sigil '{sigil}': {e}")

def map_proto_sigils_to_dbRw(proto_sigils):
    """
    Ensure each proto sigil has a corresponding dbRw file and is mapped to its tokens.
    """
    logging.info("[INFO] Mapping proto sigils to dbRw files...")
    dbRw_dir = os.path.join("glyphs", "dbRw")
    os.makedirs(dbRw_dir, exist_ok=True)

    for token, sigil_data in proto_sigils.items():
        try:
            sigil = sigil_data["glyph"]
            token_id = sigil_data["id"]

            # Create or load the dbRw file for the sigil
            db_path = os.path.join(dbRw_dir, f"{sigil}.json")
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    db_data = json.load(f)
            else:
                db_data = {"_id": sigil, "_token": sigil, "_frequency": 0, "_slots": {}}

            # Map the proto sigil to its tokens
            if "proto_sigil_tokens" not in db_data:
                db_data["proto_sigil_tokens"] = []

            # Add the token ID associated with the sigil
            if token_id not in db_data["proto_sigil_tokens"]:
                db_data["proto_sigil_tokens"].append(token_id)

            # Save the updated dbRw file
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)

            logging.info(f"[INFO] Mapped proto sigil '{sigil}' to dbRw file: {db_path}")
        except Exception as e:
            logging.error(f"[ERROR] Failed to map proto sigil '{sigil}' to dbRw: {e}")
