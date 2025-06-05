import json
import os
from datetime import datetime
import random

class SKGEngine:
    def __init__(self, memory_path):
        self.memory_path = memory_path
        self.glyph_pool = []  # Holds available glyphs
        self.token_map = {}
        self.adjacency_map = {}

        # Load persisted state if available
        self._load_state()

        # Setup logging for adjacency walks and weight changes
        self.log_dir = os.path.join(self.memory_path, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.adj_log = os.path.join(self.log_dir, "adjacency_walk.log")
        self.weight_log = os.path.join(self.log_dir, "weight_updates.log")

    def _state_path(self, name):
        return os.path.join(self.memory_path, f"{name}.json")

    def _load_state(self):
        """Load persisted token and adjacency maps if they exist."""
        for attr in ("token_map", "adjacency_map"):
            path = self._state_path(attr)
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        setattr(self, attr, json.load(f))
                except Exception:
                    setattr(self, attr, {})

    def save_state(self):
        """Persist token_map and adjacency_map to disk."""
        for attr in ("token_map", "adjacency_map"):
            path = self._state_path(attr)
            try:
                with open(path, "w") as f:
                    json.dump(getattr(self, attr), f, indent=2)
            except Exception:
                pass

    def _log(self, path, entry):
        """Append a JSON entry to a log file."""
        try:
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def update_glyph_weight(self, glyph):
        """Increment symbolic weight for existing glyph or initialize if absent."""
        if not isinstance(glyph, dict):
            return glyph

        old_weight = glyph.get("modalities", {}).get("text", {}).get("weight", 0)

        if "modalities" in glyph and "text" in glyph["modalities"]:
            if "weight" in glyph["modalities"]["text"]:
                glyph["modalities"]["text"]["weight"] += 1
            else:
                glyph["modalities"]["text"]["weight"] = 1
        else:
            glyph.setdefault("modalities", {}).setdefault("text", {})["weight"] = 1

        new_weight = glyph["modalities"]["text"]["weight"]
        glyph["last_updated"] = datetime.utcnow().isoformat() + "Z"

        self._log(self.weight_log, {
            "timestamp": glyph["last_updated"],
            "token": glyph.get("token"),
            "glyph_id": glyph.get("glyph_id"),
            "old_weight": old_weight,
            "new_weight": new_weight,
        })

        return glyph

    def assign_glyph_to_token(self, token, adjacency=None):
        """Assign a glyph to a token, considering its adjacency and context."""
        # Ensure this function assigns a glyph like 🜂, ⚚, etc.
        if token in self.token_map:
            glyph = self.token_map[token]
        else:
            # Select an actual symbolic glyph (not the token text)
            glyph_id = self.select_glyph_for_token(token, adjacency)
            now = datetime.utcnow().isoformat() + "Z"
            glyph = {
                "glyph_id": glyph_id,
                "token": token,
                "created_on": now,
                "last_updated": now,
                "modalities": {"text": {"weight": 0}},
            }
            self.token_map[token] = glyph
            self.save_state()

        # Update the glyph's weight
        glyph = self.update_glyph_weight(glyph)
        self.save_state()
        return glyph


    def select_glyph_for_token(self, token, adjacency=None):
        """Select the most appropriate glyph for a token, considering context."""
        # Here, we can select the glyph based on contextual relevance.
        # For now, select a random glyph from the pool.
        glyph = random.choice(self.glyph_pool)
        return glyph

    def get_adjacencies_for_token(self, token):
        """Get the adjacency list for a token. Can be expanded to semantic adjacencies."""
        return self.adjacency_map.get(token, [])

    def recursive_thought_loop(self, token, depth=0, max_depth=5, visited=None):
        """Perform a recursive exploration of a token's adjacencies while logging the walk."""
        if visited is None:
            visited = set()
        if depth >= max_depth or token in visited:
            return []
        visited.add(token)

        # Assign the glyph for the current token
        current_glyph = self.assign_glyph_to_token(token)

        # Check agency gates (e.g., should we explore further or prune?)
        agency_gate_decision = self.evaluate_agency_gate(token)
        if agency_gate_decision == 'externalize':
            self.externalize_token(token)
            return [current_glyph]  # Return the glyph if it's externalized

        # Otherwise, continue the recursive thought loop
        adjacencies = self.get_adjacencies_for_token(token)
        result = [current_glyph]
        
        for adjacent_token in adjacencies:
            self._log(self.adj_log, {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "from": token,
                "to": adjacent_token,
                "depth": depth,
            })
            result.extend(self.recursive_thought_loop(adjacent_token, depth + 1, max_depth, visited))

        return result

    def evaluate_agency_gate(self, token):
        """Evaluate which agency gate should be activated using contextual heuristics."""
        glyph = self.token_map.get(token, {})
        weight = glyph.get("modalities", {}).get("text", {}).get("weight", 1)
        frequency = weight
        adjacency_count = len(self.adjacency_map.get(token, []))

        token_data = {
            "frequency": frequency,
            "weight": weight,
        }

        from agency_gate import process_agency_gates

        decisions = process_agency_gates(token, token_data, adjacency_count)

        for d in decisions:
            if d["decision"] == "YES":
                return d["gate"]

        # default if nothing triggered
        return random.choice([d["gate"] for d in decisions])

    def externalize_token(self, token):
        """Externalize the token's glyph (i.e., generate its output)."""
        # Here we would trigger the visual/audio generation for the token's glyph
        print(f"Externalizing token: {token} with glyph: {self.token_map[token]}")

    def update_adjacency_map(self, token, adjacencies):
        """Update the adjacency map for a given token."""
        self.adjacency_map[token] = adjacencies
        self.save_state()

    def add_glyph_to_pool(self, glyph):
        """Add a new glyph to the glyph pool."""
        self.glyph_pool.append(glyph)
