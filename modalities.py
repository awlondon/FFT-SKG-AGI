import os
import json
import hashlib
from typing import List

# Import optional dependencies within try/except so that missing libraries
# do not break modality generation.
try:
    from tts_engine import generate_tts
except Exception:
    generate_tts = None  # type: ignore
try:
    from fft_generator import generate_fft_from_audio
except Exception:
    generate_fft_from_audio = None  # type: ignore
try:
    from generate_fft_from_image import generate_fft_from_image
except Exception:
    generate_fft_from_image = None  # type: ignore
try:
    from image_search import fetch_images_from_serpapi
except Exception:
    fetch_images_from_serpapi = None  # type: ignore
try:
    from glyph_visualizer import generate_glyph_image
except Exception:
    generate_glyph_image = None  # type: ignore


def generate_modalities(token: str, glyph_id: str) -> dict:
    """
    Generate and store multimodal representations for a token/glyph.

    This includes synthesizing speech and computing its FFT, creating an image
    for the glyph and computing its FFT, performing an image search for
    additional visual context and generating a simple ASCII representation.

    Missing or failing dependencies are handled gracefully; if a modality
    cannot be produced its entry will either be omitted or set to None.
    """
    print(f"[Modalities] Generating modalities for: {token} / {glyph_id}")
    hash_id = hashlib.sha1(token.encode()).hexdigest()[:8]

    # Construct file paths
    audio_path = f"modalities/audio/{token}_{hash_id}.wav"
    fft_audio_path = f"modalities/fft_audio/{token}_{hash_id}.npy"
    fft_visual_path = f"modalities/fft_visual/{token}_{hash_id}.png"
    symbolic_image_path = f"modalities/images/{token}_{hash_id}_sigil.png"

    # Ensure directories exist
    for p in [audio_path, fft_audio_path, fft_visual_path, symbolic_image_path]:
        os.makedirs(os.path.dirname(p), exist_ok=True)

    # --- AUDIO + AUDIO-FFT ---
    if generate_tts:
        try:
            generate_tts(token, audio_path)
            if generate_fft_from_audio:
                generate_fft_from_audio(audio_path, fft_audio_path, fft_visual_path)
        except Exception as e:
            print(f"[Modalities] Warning: audio modalities failed for '{token}': {e}")
    else:
        print("[Modalities] Warning: tts_engine not available; skipping audio modalities")

    # --- GLYPH IMAGE + GLYPH FFT ---
    generated_glyph_path = None
    if generate_glyph_image:
        try:
            generated_glyph_path = generate_glyph_image(glyph_id)
        except Exception as e:
            print(f"[Modalities] Warning: glyph image generation failed for '{glyph_id}': {e}")
    if generated_glyph_path and os.path.exists(generated_glyph_path) and generate_fft_from_image:
        try:
            fft_from_image_path = generate_fft_from_image(generated_glyph_path)
            symbolic_image_path = generated_glyph_path
        except Exception as e:
            print(f"[Modalities] Warning: FFT-from-image failed: {e}")
            fft_from_image_path = None
    else:
        fft_from_image_path = None

    # --- IMAGE SEARCH ---
    if fetch_images_from_serpapi:
        try:
            fetched_images: List[str] = fetch_images_from_serpapi(token, glyph_id, max_results=3)  # type: ignore
        except Exception as e:
            print(f"[Modalities] Warning: image search failed for '{token}': {e}")
            fetched_images = []
    else:
        print("[Modalities] Warning: image_search not available; skipping image search")
        fetched_images = []

    # --- TEXTUAL/ASCII REPRESENTATION ---
    ascii_art = f"<{token.upper()}>"

    return {
        "text": {
            "weight": 1
        },
        "audio": {
            "tts": audio_path if os.path.exists(audio_path) else None,
            "fft_audio": fft_audio_path if os.path.exists(fft_audio_path) else None
        },
        "visual": {
            "fft_visual": fft_visual_path if os.path.exists(fft_visual_path) else None,
            "photographic": fetched_images,
            "symbolic_image": symbolic_image_path if os.path.exists(symbolic_image_path) else None,
            "fft_from_image": fft_from_image_path
        },
        "extra": {
            "ascii_art": ascii_art
        }
    }