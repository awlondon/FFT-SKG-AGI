import os
import json
from skg_engine import SKGEngine
from glyph_builder import build_glyph_if_needed

required_dirs = [
    "modalities/fft_visual",
    "modalities/audio",
    "modalities/images",
    "modalities/fft_audio"
]

for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)


# Constants
data_path = "./glyph_memory"
os.makedirs(data_path, exist_ok=True)

# Initialize engine
skg = SKGEngine(data_path)

# Load the extended glyph pool so the engine has options
glyph_pool_path = "extended_glyph_pool.json"
if os.path.exists(glyph_pool_path):
    with open(glyph_pool_path, "r", encoding="utf-8") as f:
        for g in json.load(f):
            skg.add_glyph_to_pool(g)


def load_or_create_glyph(token):
    glyph_path = os.path.join(data_path, f"{token}.json")
    if os.path.exists(glyph_path):
        with open(glyph_path, 'r') as f:
            return json.load(f)
    else:
        glyph = build_glyph_if_needed(token, glyph_path)
        return glyph


def save_glyph(glyph):
    glyph_path = os.path.join(data_path, f"{glyph['token']}.json")
    with open(glyph_path, 'w') as f:
        json.dump(glyph, f, indent=2)


def process_input(user_input):
    token = user_input.lower()

    glyph_data = load_or_create_glyph(token)
    if glyph_data.get("glyph_id") not in skg.glyph_pool:
        skg.add_glyph_to_pool(glyph_data.get("glyph_id"))

    skg.recursive_thought_loop(token)
    save_glyph(glyph_data)

    if skg.externalized_last:
        os.system("cls" if os.name == "nt" else "clear")
        print("[Main] Recent thought loop:")
        print(" -> ".join(skg.thought_history[-10:]))
        skg.externalized_last = False



if __name__ == "__main__":
    print("SKG-R2 Engine Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("\nEnter token: ").strip()
        if user_input.lower() == 'exit':
            break
        process_input(user_input)
