import os
import json
import hashlib
from datetime import datetime

import config
from adjacency_seed import generate_adjacents
from modalities import generate_modalities
from glyph_decision_engine import choose_glyph_for_token
from token_fusion import TokenFusion

fusion = TokenFusion()


def build_glyph_if_needed(
    token: str,
    base_dir: str | None = None,
    adj_count: int = 50,
) -> dict:
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
    base_dir : str | None
        Directory where glyph JSON files are stored.  If ``None`` the
        location defined in :mod:`config` will be used.
    adj_count : int
        Number of adjacents to request when generating adjacency context.

    Returns
    -------
    dict
        The created glyph object.
    """
    if base_dir is None:
        base_dir = config.GLYPH_OUTPUT_DIR
    print(f"[GlyphBuilder] Building glyph for unknown token: '{token}'")
    now = datetime.utcnow().isoformat() + "Z"
    token_id = fusion.fuse_token(token)
    path = os.path.join(base_dir, f"{token_id}.json")
    manifest_path = os.path.join(base_dir, "manifest.json")

    # Determine if we already built this glyph
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    manifest: dict[str, str] = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    if os.path.exists(path) and manifest.get(token_id) == token_hash:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

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
        modalities = generate_modalities(token, glyph_id, token_id)
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

    # Save glyph object and update manifest
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(glyph, f, indent=2)
        manifest[token_id] = token_hash
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    except Exception as e:
        print(f"[GlyphBuilder] Error saving glyph to '{path}': {e}")

    return glyph
