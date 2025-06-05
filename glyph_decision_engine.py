# Gracefully handle missing OpenAI dependency or API key
import os
import json

try:
    from openai import OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key) if openai_key else None
except Exception:
    OpenAI = None
    client = None

# Load the pool of all glyphs
# Load the pool of all glyphs from the repository root
GLYPH_POOL_PATH = os.path.join(os.path.dirname(__file__), "extended_glyph_pool.json")
with open(GLYPH_POOL_PATH, "r", encoding="utf-8") as f:
    EXTENDED_GLYPHS = json.load(f)

def choose_glyph_for_token(token, adjacents=None):
    """Choose a glyph for the token using OpenAI if available."""
    glyph_list = EXTENDED_GLYPHS[:30]  # Limit for context

    prompt = f"""
You are a symbolic reasoning agent.
From the list of glyphs below, choose the single most appropriate symbolic glyph for the token '{token}'.
Base your choice on conceptual alignment. You may optionally consider these adjacent concepts: {', '.join(a['token'] for a in adjacents) if adjacents else 'none'}.

Respond with ONLY the glyph.

Glyph pool: {', '.join(glyph_list)}
"""

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a symbolic cognition engine."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=10
            )
            glyph = response.choices[0].message.content.strip()
            if glyph in EXTENDED_GLYPHS:
                return glyph
        except Exception as e:
            print(f"[GlyphAssignment] Error: {e}")
    else:
        print("[GlyphAssignment] OpenAI client unavailable. Using fallback.")

    # Fallback
    return f"⟁{token}"
