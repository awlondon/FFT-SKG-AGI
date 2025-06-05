import os
import json
from glyph_visualizer import generate_glyph_image
from skg_engine import SKGEngine
from glyph_builder import build_glyph_if_needed
from agency_gate import process_agency_gates

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
        glyph = build_glyph_if_needed(token, glyph_path)
        return glyph


def save_glyph(glyph):
    glyph_path = os.path.join(data_path, f"{glyph['token']}.json")
    with open(glyph_path, 'w') as f:
        json.dump(glyph, f, indent=2)


def process_input(user_input):
    # Assuming you're processing the 'user_input' to get the glyph and its data
    token = user_input.lower()  # Get token from user input
    
    # Create token data based on the token (example with frequency and weight)
    token_data = {
        "token": token,
        "frequency": 1,  # You can adjust based on context or token history
        "weight": 1      # You can adjust based on your logic (e.g., weight might increase with each occurrence)
    }

    # Simulate generating the glyph for the token (you may already have this elsewhere)
    # Load Symbola.ttf from the project root rather than using a hard coded path
    font_path = os.path.join(os.path.dirname(__file__), "Symbola.ttf")
    glyph = generate_glyph_image(token, font_path=font_path)  # Assuming this returns a glyph image or associated glyph info

    # Now you call the process_agency_gates with the token_data
    decisions = process_agency_gates(token, token_data)

    # Handle decisions (e.g., proceed with externalization, exploration, etc.)
    print(decisions)



if __name__ == "__main__":
    print("SKG-R2 Engine Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("\nEnter token: ").strip()
        if user_input.lower() == 'exit':
            break
        process_input(user_input)
