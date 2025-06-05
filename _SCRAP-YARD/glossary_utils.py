# glossary_utils.py
import os
import json
import time
import logging

from openai import OpenAI
from avatar_window import BASE_DIR
from glyph_renderer import render_glyph_image
from glyph_utils import generate_fft_image_for_token, get_glyph_id
from skg_engine import SKGEngine
from symbolic_constants import GLYPH_DB_DIR, GLYPH_DIR, GLYPH_IMAGE_SIZE, FFT_IMAGE_SIZE, GLOSSARY_SUFFIX, GLYPH_TOKENS_DIR
from token_utils import TokenUtils



#=== OPENAI-API SECRET SAUCE - BEGIN ===#


# Unused function: Not directly called or referenced in this file
def process_training_file_with_glossary(engine, filepath):
    base_path = os.path.abspath(filepath)
    folder, filename = os.path.split(base_path)
    name, _ = os.path.splitext(filename)
    glossary_path = os.path.join(folder, f"{name}{GLOSSARY_SUFFIX}")

    if not os.path.exists(glossary_path):
        print(f"[GLYPH_GEN] No glossary found. Calling GPT to generate: {glossary_path}")
        with open(base_path, "r", encoding="utf-8") as f:
            content = f.read()

        prompt = f"""
You are a symbolic knowledge architect.

Your task is to construct a symbolic glyph glossary. Based strictly on the corpus below, extract 100 unique groupings of semantically related tokens. Each group must be assigned a distinct Unicode glyph used as a sigil — a symbolic marker of structural or conceptual meaning (e.g. "🜁", "⚖", "⚗", "⛬").

Each glyph represents a latent category, theme, or logical construct derived from the source text. The tokens grouped beneath each glyph must reflect and reinforce that glyph’s symbolic intent.

Rules:
- Use **only tokens from the corpus**. No placeholders or made-up words.
- Each glyph must appear **only once** as a top-level key.
- Each group must contain **exactly 10 lowercase symbolic tokens** (single words only).
- Return **valid, raw JSON** — no markdown, no comments, no extra text.

Format:
{{
  "🜁": ["truth", "veil", "mirror", "echo", "signal", "origin", "stream", "depth", "symbol", "node"],
  "⚖": ["compare", "weight", "balance", "rank", "decide", "align", "conflict", "choose", "order", "value"],
  ...
}}

IMPORTANT: Return valid JSON only — no markdown, no text before or after the JSON object.


Corpus (first 3,000 chars):
{content[:3000]}
"""



        OPENAI_KEY = os.getenv("OPENAI_API_KEY")

        if not OPENAI_KEY:
            raise EnvironmentError("❌ OPENAI_API_KEY is not set. Export it before running.")

        client = OpenAI(api_key=OPENAI_KEY)



        # === Request GPT Glossary with Timer ===
        print("[GPT] Requesting glossary from GPT...")
        t0 = time.time()

        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an I/O symbolic glossary generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            duration = round(time.time() - t0, 2)
            print(f"[GPT] Glossary received in {duration}s")

            raw_response = response.choices[0].message.content

            # Log raw GPT output
            print("\n[GPT-RAW RESPONSE START]\n")
            print(raw_response)
            print("\n[GPT-RAW RESPONSE END]\n")

            tu = TokenUtils()

            raw_path = os.path.join(folder, f"{name}_gg_raw.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_response)

            try:
                glossary = extract_json_from_response(raw_response)
                
                for glyph, tokens in glossary.items():
                    for token in tokens:
                        token_id = tu.create_token_with_thought_loop(token)
                        TokenRepresentation(token, token_id)  # ← required for FFT
                        engine.relationships[token_id][glyph] = {"weight": 1, "distance": 0}
                        engine.token_freq[token_id] += 1
                        engine._save_dbRw_file(token_id)
                        
                        tu.recursive_walk(token_id, depth=0, max_depth=2)
                        tu.append_to_output_stream(token_id)

            except Exception as e:
                debug_path = os.path.join(folder, f"{name}_gg_debug.txt")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(raw_response)
                raise ValueError(f"[❌ GPT PARSE FAIL] Saved to {debug_path}: {e}")

            with open(glossary_path, "w", encoding="utf-8") as f:
                json.dump(glossary, f, indent=2)
            print(f"[GLYPH_GEN] Glossary saved: {glossary_path}")

        except Exception as e:
            raise RuntimeError(f"[GPT ERROR] Failed to generate glossary: {e}")

# Unused function: Not directly called or referenced in this file
def extract_json_from_response(text):
    import json, re

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown-style code blocks if they exist
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"```$", "", text.strip(), flags=MULTILINE)

    # Try to extract the largest valid JSON object
    brace_stack = []
    start = None

    for i, char in enumerate(text):
        if char == '{':
            if start is None:
                start = i
            brace_stack.append('{')
        elif char == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack:
                    chunk = text[start:i + 1]
                    try:
                        return json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
    # Fallback
    raise ValueError("No valid JSON found in GPT response.")



#=== OPENAI-API SECRET SAUCE - END ===#


def parse_glossary_file(glossary_path):
    """
    Parse and validate a glossary file containing Unicode glyphs as keys.

    Args:
        glossary_path (str): Path to the glossary file.

    Returns:
        dict: Parsed glossary data with Unicode glyphs as keys and token lists as values.
    """
    if not os.path.exists(glossary_path):
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")

    with open(glossary_path, "r", encoding="utf-8") as f:
        try:
            glossary = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in glossary file: {e}")

    if not isinstance(glossary, dict):
        raise ValueError("Glossary file must contain a JSON object.")

    # Ensure all keys are strings and validate values
    validated_glossary = {}
    for glyph, tokens in glossary.items():
        if not isinstance(glyph, str):
            glyph = str(glyph)  # Convert non-string keys to strings
        if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
            raise ValueError(f"Invalid value for glyph '{glyph}': {tokens} (expected list of strings)")
        validated_glossary[glyph] = tokens

    return validated_glossary


def inject_token_into_engine(engine, token_id, glyph_data, walk=True):
    tu = TokenUtils()
    if not isinstance(glyph_data, dict):
        raise TypeError(f"Expected glyph_data to be a dict, got {type(glyph_data)}: {glyph_data}")
    glyph = glyph_data.get("glyph")
    if glyph:
        # Populate self.tokens if not already present
        if token_id not in engine.tokens:
            engine.tokens[token_id] = {"glyph": glyph, "data": {}}
            logging.info(f"[INFO] Initialized token {token_id} with glyph '{glyph}' in engine.tokens")
        engine.relationships[token_id][glyph] = glyph_data
        engine.token_freq[token_id] += 1
        engine._save_dbRw_file(token_id)
        if walk:
            tu.recursive_walk(token_id)

def load_and_process_glossary(glossary_path, engine=None):
    """
    Load and process a glossary file, injecting tokens and glyphs into the engine.

    Args:
        glossary_path (str): Path to the glossary file.
        engine (SKGEngine, optional): Engine instance to inject tokens and glyphs into.
    """
    glossary = parse_glossary_file(glossary_path)
    # Validate glossary format
    if not isinstance(glossary, dict):
        raise ValueError(f"Expected a dictionary, got {type(glossary)}")
    
    if glossary is None:
        logging.error("Glossary data is None. Please provide a valid glossary.")
        raise ValueError("Glossary data cannot be None")

    if engine:
        for glyph, tokens in glossary.items():
            if not isinstance(tokens, list):
                raise ValueError(f"Expected a list of tokens for glyph '{glyph}', got {type(tokens)}")

            # Process each token associated with the glyph
            for token in tokens:
                token_id = str(hash(token))[-6:]  # Generate a unique token ID
                glyph_data = {"glyph": glyph, "tokens": [token]}
                inject_token_into_engine(engine, token_id, glyph_data)
                generate_fft_image_for_token(token, token_id)

                # Log token and glyph registration
                print(f"[GLYPH LOAD] Registered token '{token}' with glyph '{glyph}'")

            # Ensure the glyph is rendered and processed
            try:
                from glyph_utils import generate_fft_image_for_token
                token_id = get_glyph_id(glyph)
                generate_fft_image_for_token(glyph, token_id)  # Generate image and FFT for the glyph
                print(f"[GLYPH PROCESS] Rendered and processed FFT for glyph '{glyph}'")
            except Exception as e:
                print(f"[ERROR] Failed to process glyph '{glyph}': {e}")

        # Ensure directories exist for glyph storage
        glyph_images_dir = os.path.join(engine.base_dir, "glyph_images")
        fft_dir = os.path.join(glyph_images_dir, "fft")
        os.makedirs(glyph_images_dir, exist_ok=True)
        os.makedirs(fft_dir, exist_ok=True)
    return glossary


def process_training_pair(txt_path, gg_path):
    """
    Process a training pair consisting of a text file and a glossary file.
    """
    glossary = None
    print(f"[⚙️] Loading: {txt_path} + {gg_path}")
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    with open(gg_path, "r", encoding="utf-8") as f:
        glossary = json.load(f)
    tokens = text.split()
    token_ids = [str(hash(t))[-6:] for t in tokens[:50]]
    print(f"[🔡] Tokens: {len(tokens)} | Unique IDs: {len(set(token_ids))}")
    return glossary, tokens, token_ids

