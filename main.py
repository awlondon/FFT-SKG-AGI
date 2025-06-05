import os
import json
from skg_engine import SKGEngine
from glyph_builder import build_glyph_if_needed
from agency_gate import process_agency_gates
from tts_engine import speak
from stt_engine import transcribe_speech


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


def process_input(user_input):
    # Assuming you're processing the 'user_input' to get the glyph and its data
    token = user_input.lower()  # Get token from user input

    glyph = load_or_create_glyph(token)
    adjacents = glyph.get("adjacents", [])
    skg.update_adjacency_map(token, adjacents)

    token_data = {
        "token": token,
        "frequency": 1,
        "weight": 1
    }

    decisions = process_agency_gates(token, token_data)
    space_field = skg.generate_space_field(token)
    top_three = sorted(
        skg.get_adjacencies_for_token(token).items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    print(decisions)
    print("Top adjacents:", top_three)
    print("Space Field:", space_field)
    speak(" ".join(t for t, _ in top_three))



if __name__ == "__main__":
    print("SKG-R2 Engine Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("\nEnter token or type 'voice': ").strip()
        if user_input.lower() == 'exit':
            break
        if user_input.lower() == 'voice':
            spoken = transcribe_speech()
            if spoken:
                speak(f"You said {spoken}")
                process_input(spoken)
            continue
        process_input(user_input)
