# filename: emergent_token_utils.py

import os
import json
import time

class EmergentTokenTracker:
    def __init__(self, input_token_ids=None, gate_engine=None):
        self.input_token_ids = set(input_token_ids or [])
        self.token_freq = {}
        self.emergent_log_path = "emergent_tokens.jsonl"
        self.gate_engine = gate_engine
        self.out_dir = "emergent_tokens"
        self.roots_seen = set()
        self.emergent_limit = 200
        self.emergent_count = 0

    def update_frequency(self, token_id):
        self.token_freq[token_id] = self.token_freq.get(token_id, 0) + 1

    def normalize_token(self, token):
        return token.lower().rstrip("s").rstrip("ed").rstrip("ing")

    def is_unique_morphology(self, token):
        norm = self.normalize_token(token)
        if norm in self.roots_seen:
            return False
        self.roots_seen.add(norm)
        return True

    def is_emergent(self, token_id):
        return token_id not in self.input_token_ids and self.token_freq.get(token_id, 0) == 1

    def token_exists_in_skg(self, token_id):
        base_dir = os.getcwd()
        for folder in os.listdir(base_dir):
            if folder.startswith("skg_"):
                token_path = os.path.join(base_dir, folder, "tokens", f"{token_id}.json")
                if os.path.isfile(token_path):
                    return True
        return False

    def log_emergent(self, token, token_id):
        if self.emergent_count >= self.emergent_limit:
            return

        suppress = prioritize = question = False

        if self.gate_engine:  # Check if gate_engine is not None
            suppress = self.gate_engine.gate_decision("suppress_output", token_id)
            prioritize = self.gate_engine.gate_decision("prioritize_output", token_id)
            question = self.gate_engine.gate_decision("question_self", token_id)
        else:
            print("[WARNING] gate_engine is not initialized. Skipping gate decisions.")

        print(f"[GATE] suppress={suppress}, prioritize={prioritize}, question={question}")

        if suppress or not prioritize:
            return

        print(f"[🌀 EMERGENT] {token} ({token_id})")

        entry = {
            "token": token,
            "token_id": token_id,
            "timestamp": time.time(),
            "gates": {
                "suppress_output": suppress,
                "prioritize_output": prioritize,
                "question_self": question
            }
        }

        os.makedirs(self.out_dir, exist_ok=True)
        with open(self.emergent_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        out_path = os.path.join(self.out_dir, f"{token_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)

        self.emergent_count += 1

    def process_token(self, token, token_id):
        self.update_frequency(token_id)
        
        # Ensure token is a string
        token = str(token)
        
        if (
            self.is_emergent(token_id)
            and not self.token_exists_in_skg(token_id)
            and len(token) >= 4
            and self.token_freq[token_id] <= 2
            and self.is_unique_morphology(token)
        ):
            # Update adjacency slots
            adjacency_slots = {}
            for slot_index in range(1, 51):
                slot_key = f"slot_{slot_index}"
                adjacency_slots[slot_key] = {"tokens": []}  # Initialize empty slots

            # Save the token with adjacency slots
            self.log_emergent(token, token_id)
