import os
import json
from datetime import datetime
from adjacency_seed import generate_adjacents
from modalities import generate_modalities
from glyph_decision_engine import choose_glyph_for_token

def build_glyph_if_needed(token, path, adj_count: int = 50):
    print(f"[GlyphBuilder] Building glyph for unknown token: '{token}'")
    now = datetime.utcnow().isoformat() + "Z"

    # Step 1: Generate adjacents first (required for glyph decision)
    adjacents = generate_adjacents(token, top_k=adj_count)

    # Step 2: Choose glyph based on token and adjacents
    glyph_id = choose_glyph_for_token(token, adjacents)

    # Step 3: Generate modalities (FFT, TTS, image, etc.)
    modalities = generate_modalities(token, glyph_id)

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
        "self_notes": [
            f"Auto-generated from token '{token}' on {now}."
        ]
    }

    # Save glyph object
    with open(path, 'w') as f:
        json.dump(glyph, f, indent=2)

    return glyph
