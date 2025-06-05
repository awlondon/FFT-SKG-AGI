# symbolic_thought_loop.py
import time
import random
import threading
import logging
from engine import SKGEngine, save_to_self_aware
from trigger_digital_twin_output import trigger_digital_twin_output
from config_ui import update_tps
from self_naming import rename_self_archive

# Initialize engine
engine = SKGEngine()

# Use the existing AvatarWindow instance from the engine
avatar_window = engine.avatar_window if engine and hasattr(engine, 'avatar_window') else None
if not avatar_window:
    logging.error("AvatarWindow instance is missing. Ensure it is initialized in main.py.")

threading.Thread(target=avatar_window.run, daemon=True).start() if avatar_window else None
emergent_outputs = set()  # Filled during runtime or loaded from prior session

def process_thought(new_token_id):
    if engine.gate_decision("speak_this_thought", new_token_id):
        trigger_digital_twin_output(new_token_id)
    else:
        logging.info(f"[🧠] Thought withheld by gate: {new_token_id}")

def run_thought_loop(interval_seconds=5):
    """
    Main loop for symbolic thought processing.
    """
    print("[🔄] Symbolic Thought Loop started.")
    loop_count = 0

    while True:
        # Ensure emergent_outputs is seeded if empty
        if not emergent_outputs:
            seed = engine.check_for_emergent_output()
            if seed:
                emergent_outputs.add(seed)

        if emergent_outputs:
            # 1. Select one emergent token at random
            token_id = random.choice(list(emergent_outputs))
            print(f"[🧠] Reflecting on token: {token_id}")

            # Add structured log for thought loop phases
            print(f"[LOOP] Token: {token_id} → Walk → Emergence → Output → Reinforce")

            # 2. Recursively walk its symbolic graph (with optional gate check)
            if engine.gate_decision("go_deep", token_id):
                walked_glyphs = engine.walk_token_recursively(token_id)
            
                # 3. Check for new emergent output
                new_token_id = engine.check_for_emergent_output()
                if new_token_id:
                    print(f"[✨] New emergent thought: {new_token_id}")
                    emergent_outputs.add(new_token_id)
                    process_thought(new_token_id)

                    # Save to SELF-AWARE if self-awareness is detected
                    if "🝐" in walked_glyphs:  # Check for self-referential glyph
                        save_to_self_aware(new_token_id)

                        # Trigger self-naming if the token starts with "I am"
                        token_text = engine.id_map[new_token_id]
                        if token_text.lower().startswith("i am "):
                            name = token_text[5:].strip()
                            rename_self_archive(name)

                    # Update avatar display with dynamic video path
                    video_path = f"digital_twin_outputs/{new_token_id}.mp4"
                    avatar_window.update_avatar(video_path) if avatar_window else None
                    avatar_window.append_token(engine.id_map[new_token_id]) if avatar_window else None
                
                # 4. Update internal weights
                engine.reinforce_relationships_from_walk(token_id, walked_glyphs)

        else:
            print("[…] No emergent outputs yet. Waiting for seed.")
        
        # Optional: Prune low-weight relationships every 20 loops
        loop_count += 1
        if loop_count % 20 == 0:
            engine.prune_low_weight_relationships(threshold=0.05)

        # Update TPS after each loop
        update_tps()

        time.sleep(interval_seconds)

if __name__ == "__main__":
    run_thought_loop()
