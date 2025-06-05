import os
import json
import random
from datetime import datetime
from typing import Optional
from superknowledge_graph import SuperKnowledgeGraph
from agency_gate import process_agency_gates
from skg_thought_tracker import SKGThoughtTracker


class SKGEngine:
    def __init__(self, memory_path: str, glyph_path: Optional[str] = None):
        """
        Initialize the SKG engine.

        Parameters
        ----------
        memory_path : str
            Path where glyph memory files are stored.
        glyph_path : Optional[str], default "glossary/extended_glyph_pool.json"
            JSON file containing a list of glyphs to populate glyph_pool.
        """
        self.memory_path = memory_path
        self.glyph_list_path = glyph_path or "glossary/extended_glyph_pool.json"
        self.token_map = {}
        self.adjacency_map = {}
        self.graph = SuperKnowledgeGraph()
        self.thought_tracker = SKGThoughtTracker()

        # Load glyphs
        self._load_glyph_pool(self.glyph_list_path)

        # Load saved state
        self._load_state()

        # Initialize logs
        self.log_dir = os.path.join(self.memory_path, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.adj_log = os.path.join(self.log_dir, "adjacency_walk.log")
        self.weight_log = os.path.join(self.log_dir, "weight_updates.log")

    def _state_path(self, name):
        return os.path.join(self.memory_path, f"{name}.json")

    def _load_state(self):
        for attr in ("token_map", "adjacency_map"):
            path = self._state_path(attr)
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        setattr(self, attr, json.load(f))
                except Exception:
                    setattr(self, attr, {})

    def _load_glyph_pool(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.glyph_pool = json.load(f)
        except Exception as e:
            print(f"[SKGEngine] Unable to load glyphs from {path}: {e}")
            self.glyph_pool = []

    def _log(self, path, entry):
        try:
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def save_state(self):
        for attr in ("token_map", "adjacency_map"):
            path = self._state_path(attr)
            try:
                with open(path, "w") as f:
                    json.dump(getattr(self, attr), f, indent=2)
            except Exception:
                pass

    def update_glyph_weight(self, glyph):
        if not isinstance(glyph, dict):
            return glyph
        old_weight = glyph.get("modalities", {}).get("text", {}).get("weight", 0)
        glyph.setdefault("modalities", {}).setdefault("text", {})["weight"] = old_weight + 1
        glyph["last_updated"] = datetime.utcnow().isoformat() + "Z"

        self._log(self.weight_log, {
            "timestamp": glyph["last_updated"],
            "token": glyph.get("token"),
            "glyph_id": glyph.get("glyph_id"),
            "old_weight": old_weight,
            "new_weight": glyph["modalities"]["text"]["weight"],
        })

        return glyph

    def assign_glyph_to_token(self, token, adjacency=None):
        if token in self.token_map:
            glyph = self.token_map[token]
        else:
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
        glyph = self.update_glyph_weight(glyph)
        self.save_state()
        return glyph

    def select_glyph_for_token(self, token, adjacency=None):
        return random.choice(self.glyph_pool) if self.glyph_pool else "□"

    def get_adjacencies_for_token(self, token):
        return self.adjacency_map.get(token, {})

    def update_adjacency_map(self, token, adjacencies):
        """
        Update adjacency weights. Supports both list-style and dict-style input.
        """
        mapping = self.adjacency_map.setdefault(token, {})
        for adj in adjacencies:
            adj_token = adj.get("token", adj) if isinstance(adj, dict) else adj
            weight = adj.get("weight", 1) if isinstance(adj, dict) else 1
            mapping[adj_token] = mapping.get(adj_token, 0) + weight
            self.graph.connect("global", token, adj_token)
        self.save_state()

    def recursive_thought_loop(self, token, depth=0, max_depth=5, parent=None):
        if depth >= max_depth:
            return []

        if token not in self.token_map and parent is not None:
            origin_glyph = self.token_map.get(parent)
            self.thought_tracker.log_expansion(parent, token, origin_glyph)

        current_glyph = self.assign_glyph_to_token(token)
        self.thought_tracker.log_thought_loop(token, depth, [current_glyph], False)

        gate = self.evaluate_agency_gate(token)
        if gate == "externalize":
            self.externalize_token(token)
            self.thought_tracker.log_thought_loop(token, depth, [current_glyph], True)
            self.thought_tracker.reset()
            return [current_glyph]

        adjacents = self.get_adjacencies_for_token(token)
        self.thought_tracker.log_convergence([token] + list(adjacents.keys()), len(adjacents), 0)
        result = [current_glyph]

        for slot_index, adj_token in enumerate(adjacents.keys()):
            self.thought_tracker.log_adjacency(token, adj_token, slot_index, weight_delta=adjacents[adj_token])
            result.extend(self.recursive_thought_loop(adj_token, depth + 1, max_depth, parent=token))

        return result

    def evaluate_agency_gate(self, token):
        glyph = self.token_map.get(token, {})
        weight = glyph.get("modalities", {}).get("text", {}).get("weight", 1)
        adj_count = len(self.adjacency_map.get(token, {}))
        token_data = {"frequency": weight, "weight": weight}
        decisions = process_agency_gates(token, token_data, adj_count)
        for d in decisions:
            if d["decision"] == "YES":
                return d["gate"]
        return random.choice([d["gate"] for d in decisions])

    def externalize_token(self, token):
        print(f"[SKGEngine] Externalizing token: {token} with glyph: {self.token_map[token]}")

    def add_glyph_to_pool(self, glyph):
        self.glyph_pool.append(glyph)

    def traverse_superknowledge(self, start_token, steps=5):
        return self.graph.traverse(start_token, max_steps=steps)

    def generate_space_field(self, token, radius=1.0):
        """
        Generate a spatial layout for a token's adjacents using HLSF routines.
        """
        from hlsf_adapter import generate_vertices

        field = {token: (0.0, 0.0)}
        adjacents = self.get_adjacencies_for_token(token)
        adjacency_tokens = list(adjacents.keys())

        sides = max(len(adjacency_tokens), 1)
        vertices = generate_vertices((0.0, 0.0), radius, sides)

        for idx, adj_token in enumerate(adjacency_tokens):
            field[adj_token] = vertices[idx % sides]

        return field
