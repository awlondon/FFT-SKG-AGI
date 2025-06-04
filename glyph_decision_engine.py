from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the pool of all glyphs
with open("glossary/extended_glyph_pool.json", "r", encoding="utf-8") as f:
    EXTENDED_GLYPHS = json.load(f)

def choose_glyph_for_token(token, adjacents=None):
    glyph_list = EXTENDED_GLYPHS[:30]  # Limit for context

    prompt = f"""
You are a symbolic reasoning agent.
From the list of glyphs below, choose the single most appropriate symbolic glyph for the token '{token}'.
Base your choice on conceptual alignment. You may optionally consider these adjacent concepts: {', '.join(a['token'] for a in adjacents) if adjacents else 'none'}.

Respond with ONLY the glyph.

Glyph pool: {', '.join(glyph_list)}
"""

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

    # Fallback
    return f"⟁{token}"
