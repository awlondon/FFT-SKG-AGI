import os
import json
from datetime import datetime
from adjacency_seed import generate_adjacents
from modalities import generate_modalities
from glyph_decision_engine import choose_glyph_for_token


def build_glyph_if_needed(token: str, path: str, adj_count: int = 50) -> dict:
    """
    Create a glyph representation for a token if it does not already exist.

    The glyph building process performs several steps:
      1. Generate a list of adjacent tokens to provide context.
      2. Select an appropriate glyph identifier from the pool.
      3. Produce modality data (audio, image, FFTs).
      4. Persist the resulting glyph object to disk.

    Errors in any of the sub‑steps are caught and sensible fallbacks are
    returned so that glyph creation does not abort the entire pipeline.

    Parameters
    ----------
    token : str
        The token for which a glyph is being created.
    path : str
        The file path under which to persist the resulting glyph JSON.
    adj_count : int
        Number of adjacents to request when generating adjacency context.

    Returns
    -------
    dict
        The created glyph object.
    """
    print(f"[GlyphBuilder] Building glyph for unknown token: '{token}'")
    now = datetime.utcnow().isoformat() + "Z"

    # Step 1: Generate adjacents first (required for glyph decision)
    try:
        adjacents = generate_adjacents(token, top_k=adj_count)
    except Exception as e:
        print(f"[GlyphBuilder] Error generating adjacents for '{token}': {e}")
        adjacents = []

    # Step 2: Choose glyph based on token and adjacents
    try:
        glyph_id = choose_glyph_for_token(token, adjacents)
    except Exception as e:
        print(f"[GlyphBuilder] Error choosing glyph for '{token}': {e}")
        glyph_id = "□"

    # Step 3: Generate modalities (FFT, TTS, image, etc.)
    try:
        modalities = generate_modalities(token, glyph_id)
    except Exception as e:
        print(f"[GlyphBuilder] Error generating modalities for '{token}': {e}")
        # Provide a minimal modalities structure
        modalities = {
            "text": {"weight": 1},
            "audio": {},
            "visual": {},
            "extra": {},
        }

    # Step 4: Compose glyph object
    glyph = {
        "glyph_id": glyph_id,
        "token": token,
        "status": "condensing",
        "created_on": now,
        "last_updated": now,
        "modalities": modalities,
        "adjacents": adjacents,
        "agency_trace": [],
        "self_notes": [f"Auto-generated from token '{token}' on {now}."]
    }

    # Save glyph object
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(glyph, f, indent=2)
    except Exception as e:
        print(f"[GlyphBuilder] Error saving glyph to '{path}': {e}")

    return glyph