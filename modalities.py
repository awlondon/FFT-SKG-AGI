import os
import json
import hashlib
from tts_engine import generate_tts
from fft_generator import generate_fft_from_audio
from generate_fft_from_image import generate_fft_from_image
from image_search import fetch_images_from_serpapi
from glyph_visualizer import generate_glyph_image

def generate_modalities(token, glyph_id):
    print(f"[Modalities] Generating modalities for: {token} / {glyph_id}")

    hash_id = hashlib.sha1(token.encode()).hexdigest()[:8]

    # Paths
    audio_path = f"modalities/audio/{token}_{hash_id}.wav"
    fft_audio_path = f"modalities/fft_audio/{token}_{hash_id}.npy"
    fft_visual_path = f"modalities/fft_visual/{token}_{hash_id}.png"
    symbolic_image_path = f"modalities/images/{token}_{hash_id}_sigil.png"

    # Ensure directories exist
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    os.makedirs(os.path.dirname(fft_audio_path), exist_ok=True)
    os.makedirs(os.path.dirname(fft_visual_path), exist_ok=True)
    os.makedirs(os.path.dirname(symbolic_image_path), exist_ok=True)

    # --- AUDIO + AUDIO-FFT ---
    generate_tts(token, audio_path)
    generate_fft_from_audio(audio_path, fft_audio_path, fft_visual_path)

    # --- GLYPH IMAGE + GLYPH FFT ---
    generated_glyph_path = generate_glyph_image(glyph_id)  # Use actual assigned glyph ID
    fft_from_image_path = None
    if generated_glyph_path and os.path.exists(generated_glyph_path):
        fft_from_image_path = generate_fft_from_image(generated_glyph_path)
        symbolic_image_path = generated_glyph_path
    else:
        print("[Modalities] Warning: Glyph image not generated. Skipping FFT-from-image.")

    # --- IMAGE SEARCH ---
    fetched_images = fetch_images_from_serpapi(token, glyph_id, max_results=3)

    # --- TEXTUAL/ASCII REPRESENTATION ---
    ascii_art = f"<{token.upper()}>"

    return {
        "text": {
            "weight": 1
        },
        "audio": {
            "tts": audio_path,
            "fft_audio": fft_audio_path
        },
        "visual": {
            "fft_visual": fft_visual_path,
            "photographic": fetched_images,
            "symbolic_image": symbolic_image_path,
            "fft_from_image": fft_from_image_path
        },
        "extra": {
            "ascii_art": ascii_art
        }
    }