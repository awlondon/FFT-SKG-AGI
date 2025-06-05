import os
import json
from skg_engine import SKGEngine
from glyph_builder import build_glyph_if_needed
from agency_gate import process_agency_gates
from tts_engine import speak
from stt_engine import transcribe_speech
from glyph_visualizer import generate_glyph_image

# Setup required directories
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

# Initialize symbolic cognition engine
skg = SKGEngine(data_path)

# Load extended glyph pool if available
glyph_pool_path = "extended_glyph_pool.json"
if os.path.exists(glyph_pool_path):
    with open(glyph_pool_path, "r", encoding="utf-8") as f:
        for g in json.load(f):
            skg.add_glyph_to_pool(g)

# Glyph I/O helpers
def load_or_create_glyph(token):
    glyph_path = os.path.join(data_path, f"{token}.json")
    if os.path.exists(glyph_path):
        with open(glyph_path, 'r') as f:
            return json.load(f)
    else:
        glyph = build_glyph_if_needed(token, glyph_path, adj_count=50)
        return glyph

def save_glyph(glyph):
    glyph_path = os.path.join(data_path, f"{glyph['token']}.json")
    with open(glyph_path, 'w') as f:
        json.dump(glyph, f, indent=2)

# Input processor
def process_input(user_input):
    token = user_input.lower()

    glyph_data = load_or_create_glyph(token)
    if glyph_data.get("glyph_id") not in skg.glyph_pool:
        skg.add_glyph_to_pool(glyph_data.get("glyph_id"))

    # Update SKG adjacency map
    adjacents = glyph_data.get("adjacents", [])
    skg.update_adjacency_map(token, adjacents)

    # Visual glyph rendering
    generate_glyph_image(token)

    # Run symbolic recursion
    skg.recursive_thought_loop(token)
    save_glyph(glyph_data)

    # Top adjacents report
    top_three = sorted(
        skg.get_adjacencies_for_token(token).items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    print("[Top Adjacents]", top_three)

    if top_three:
        speak(" ".join(t for t, _ in top_three))

    # Optional console clear after externalization
    if hasattr(skg, "externalized_last") and skg.externalized_last:
        os.system("cls" if os.name == "nt" else "clear")
        print("[Main] Recent thought loop:")
        if hasattr(skg, "thought_history"):
            print(" -> ".join(skg.thought_history[-10:]))
        skg.externalized_last = False

# Main loop
if __name__ == "__main__":
    print("⚙️  SKG-R2 Engine Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("\nEnter token or type 'voice': ").strip()
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'voice':
            spoken = transcribe_speech()
            if spoken:
                speak(f"You said {spoken}")
                process_input(spoken)
            continue
        process_input(user_input)
