import os
import json
import argparse
import threading
import time
from skg_engine import SKGEngine
import config
from glyph_builder import build_glyph_if_needed
from token_fusion import TokenFusion

fusion = TokenFusion()
from agency_gate import process_agency_gates  # noqa: F401  # imported for side effects
from tts_engine import speak
from stt_engine import transcribe_speech
from video_capture import capture_frame
from glyph_visualizer import generate_glyph_image
from avatar_gui import AvatarGUI

# Setup required directories on program start
required_dirs = [
    "modalities/fft_visual",
    "modalities/audio",
    "modalities/images",
    "modalities/fft_audio"
]
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)

# Constants for memory storage
data_path = "./glyph_memory"
os.makedirs(data_path, exist_ok=True)


def load_or_create_glyph(token: str) -> dict:
    token_id = fusion.fuse_token(token)
    glyph_path = os.path.join(data_path, f"{token_id}.json")
    if os.path.exists(glyph_path):
        with open(glyph_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        glyph = build_glyph_if_needed(token, data_path, adj_count=50)
        return glyph


def save_glyph(glyph: dict) -> None:
    token_id = fusion.fuse_token(glyph['token'])
    glyph_path = os.path.join(data_path, f"{token_id}.json")
    try:
        with open(glyph_path, 'w', encoding='utf-8') as f:
            json.dump(glyph, f, indent=2)
    except Exception as e:
        print(f"[Main] Error saving glyph for '{glyph['token']}': {e}")


def process_input(user_input: str, skg: SKGEngine, gui: AvatarGUI  | None = None) -> None:
    token = user_input.lower()
    glyph_data = load_or_create_glyph(token)
    # Add glyph id to pool if not already present
    glyph_id = glyph_data.get("glyph_id")
    if glyph_id and glyph_id not in skg.glyph_pool:
        skg.add_glyph_to_pool(glyph_id)
    # Update SKG adjacency map
    adjacents = glyph_data.get("adjacents", [])
    skg.update_adjacency_map(token, adjacents)
    # Visual glyph rendering
    generate_glyph_image(glyph_id)
    # Run symbolic recursion if enabled
    if skg.recursion_enabled:
        skg.recursive_thought_loop(token)
    save_glyph(glyph_data)
    # Top adjacents report
    top_three = sorted(
        skg.get_adjacencies_for_token(token).items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    print("[Top Adjacents]", top_three)
    if top_three and skg.speech_enabled:
        speak(" ".join(t for t, _ in top_three))
    # Optional console clear after externalization
    if hasattr(skg, "externalized_last") and skg.externalized_last:
        os.system("cls" if os.name == "nt" else "clear")
        print("[Main] Recent thought loop:")
        if hasattr(skg, "thought_history"):
            print(" -> ".join(skg.thought_history[-10:]))
        skg.externalized_last = False

    if gui:
        gui.update_from_token(glyph_data)


def voice_listener_loop(skg: SKGEngine, gui: AvatarGUI | None) -> None:
    """Continuously listen on the microphone and process any recognized speech."""
    while True:
        spoken, _ = transcribe_speech()
        if spoken:
            speak(f"You said {spoken}")
            process_input(spoken, skg, gui)
        time.sleep(0.5)


def webcam_listener_loop(skg: SKGEngine, gui: AvatarGUI | None) -> None:
    """Continuously capture webcam frames and process the derived token."""
    while True:
        token, image_path = capture_frame()
        if token:
            print(f"[Webcam] Token {token} from {image_path}")
            skg.assign_glyph_to_token(token)
            process_input(token, skg, gui)
        time.sleep(3)


def main() -> None:
    # Initialize symbolic cognition engine with communication options
    parser = argparse.ArgumentParser(description="SKG Engine")
    parser.add_argument("--no-gui", action="store_true", help="disable Tkinter GUI")
    args = parser.parse_args()

    skg = SKGEngine(data_path, comm_enabled=config.ENABLE_ENGINE_COMM)
    if config.ENABLE_ENGINE_COMM and config.SUBSCRIBE_STREAM:
        skg.subscribe_to_engine(config.SUBSCRIBE_STREAM)
    # Load extended glyph pool if available
    glyph_pool_path = "glossary/extended_glyph_pool.json"
    if os.path.exists(glyph_pool_path):
        try:
            with open(glyph_pool_path, "r", encoding='utf-8') as f:
                for g in json.load(f):
                    skg.add_glyph_to_pool(g)
        except Exception:
            pass
    gui = None
    if not args.no_gui:
        gui = AvatarGUI(skg)
        threading.Thread(target=gui.run, daemon=True).start()

    threading.Thread(target=voice_listener_loop, args=(skg, gui), daemon=True).start()
    threading.Thread(target=webcam_listener_loop, args=(skg, gui), daemon=True).start()
        
    print("⚙️  SKG-R2 Engine Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("\nEnter token: ").strip()
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'voice':
            spoken, audio_path = transcribe_speech()
            if spoken:
                speak(f"You said {spoken}")
                process_input(spoken, skg, gui)
            continue
        elif user_input.lower() == 'webcam':
            token, image_path = capture_frame()
            if token:
                print(f"[Webcam] Token {token} from {image_path}")
                skg.assign_glyph_to_token(token)
                process_input(token, skg, gui)
            continue
        process_input(user_input, skg, gui)


if __name__ == "__main__":
    main()
