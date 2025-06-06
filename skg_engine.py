import os
import json
import random
from datetime import datetime
from typing import Optional
from superknowledge_graph import SuperKnowledgeGraph
from agency_gate import process_agency_gates
from skg_thought_tracker import SKGThoughtTracker

class SKGEngine:
    def __init__(self, memory_path: str, glyph_path: Optional[str] = "glossary/extended_glyph_pool.json"):
        self.memory_path = memory_path
        self.glyph_list_path = glyph_path
        self.token_map = {}
        self.adjacency_map = {}
        self.glyph_pool = []
        self.graph = SuperKnowledgeGraph()
        self.thought_tracker = SKGThoughtTracker()
        self.thought_history = []
        self.externalized_last = False

        # Load glyph pool
        self._load_glyph_pool(self.glyph_list_path)
        self._load_state()

        # Logging paths
        self.log_dir = os.path.join(self.memory_path, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.adj_log = os.path.join(self.log_dir, "adjacency_walk.log")
        self.weight_log = os.path.join(self.log_dir, "weight_updates.log")

    def _log(self, log_path, entry):
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _load_glyph_pool(self, path):
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.glyph_pool = json.load(f)

    def _load_state(self):
        token_path = os.path.join(self.memory_path, "token_map.json")
        adj_path = os.path.join(self.memory_path, "adjacency_map.json")
        if os.path.exists(token_path):
            try:
                with open(token_path, "r", encoding="utf-8") as f:
                    self.token_map = json.load(f)
            except Exception:
                self.token_map = {}
        if os.path.exists(adj_path):
            try:
                with open(adj_path, "r", encoding="utf-8") as f:
                    self.adjacency_map = json.load(f)
            except Exception:
                self.adjacency_map = {}

    def save_state(self):
        os.makedirs(self.memory_path, exist_ok=True)
        token_path = os.path.join(self.memory_path, "token_map.json")
        adj_path = os.path.join(self.memory_path, "adjacency_map.json")
        try:
            with open(token_path, "w", encoding="utf-8") as f:
                json.dump(self.token_map, f, indent=2)
        except Exception:
            pass
        try:
            with open(adj_path, "w", encoding="utf-8") as f:
                json.dump(self.adjacency_map, f, indent=2)
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

    def update_adjacency_map(self, token, adjacencies):
        mapping = self.adjacency_map.setdefault(token, {})
        for adj in adjacencies:
            adj_token = adj.get("token", adj) if isinstance(adj, dict) else adj
            weight = adj.get("weight", 1) if isinstance(adj, dict) else 1
            mapping[adj_token] = mapping.get(adj_token, 0) + weight
            self.graph.connect("global", token, adj_token)
        self.save_state()

    def get_adjacencies_for_token(self, token):
        return self.adjacency_map.get(token, {})

    def recursive_thought_loop(self, token, depth=0, max_depth=5, parent=None):
        if depth >= max_depth:
            return []

        if token not in self.token_map and parent is not None:
            origin_glyph = self.token_map.get(parent)
            self.thought_tracker.log_expansion(parent, token, origin_glyph)

        current_glyph = self.assign_glyph_to_token(token)
        self.thought_history.append(token)
        if len(self.thought_history) > 20:
            self.thought_history = self.thought_history[-20:]

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
        glyph = self.token_map.get(token)
        display = glyph.get("glyph_id", glyph) if isinstance(glyph, dict) else glyph
        weight = glyph.get("modalities", {}).get("text", {}).get("weight") if isinstance(glyph, dict) else None
        print(f"[SKGEngine] Externalizing '{token}' → '{display}' (weight: {weight if weight is not None else 'N/A'})")
        self.externalized_last = True

    def add_glyph_to_pool(self, glyph):
        self.glyph_pool.append(glyph)

    def traverse_superknowledge(self, start_token, steps=5):
        return self.graph.traverse(start_token, max_steps=steps)

    def generate_space_field(self, token, radius=1.0):
        from hlsf_adapter import generate_vertices
        field = {token: (0.0, 0.0)}
        adjacents = self.get_adjacencies_for_token(token)
        adjacency_tokens = list(adjacents.keys())
        sides = max(len(adjacency_tokens), 1)
        vertices = generate_vertices((0.0, 0.0), radius, sides)
        for idx, adj_token in enumerate(adjacency_tokens):
            field[adj_token] = vertices[idx % sides]
        return field
