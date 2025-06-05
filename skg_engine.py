import json
import os
from datetime import datetime
import random
from superknowledge_graph import SuperKnowledgeGraph
from agency_gate import process_agency_gates

class SKGEngine:
    def __init__(self, memory_path, glyph_pool_path="glossary/extended_glyph_pool.json"):
        self.memory_path = memory_path
        self.token_map = {}  # token -> glyph
        self.adjacency_map = {}  # token -> [adjacent_tokens]
        self.glyph_pool = []
        self.graph = SuperKnowledgeGraph()

        # Load persisted state
        self._load_state()
        self._load_glyph_pool(glyph_pool_path)

        # Logging
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

    def save_state(self):
        for attr in ("token_map", "adjacency_map"):
            path = self._state_path(attr)
            try:
                with open(path, "w") as f:
                    json.dump(getattr(self, attr), f, indent=2)
            except Exception:
                pass

    def _log(self, path, entry):
        try:
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def _load_glyph_pool(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.glyph_pool = json.load(f)
            except Exception as e:
                print(f"[SKGEngine] Failed to load glyph pool: {e}")
        else:
            print(f"[SKGEngine] Glyph pool not found at {path}")

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
        return self.adjacency_map.get(token, [])

    def update_adjacency_map(self, token, adjacencies):
        self.adjacency_map[token] = adjacencies
        for adj in adjacencies:
            self.graph.connect("global", token, adj)
        self.save_state()

    def recursive_thought_loop(self, token, depth=0, max_depth=5, visited=None):
        if visited is None:
            visited = set()
        if depth >= max_depth or token in visited:
            return []
        visited.add(token)

        glyph = self.assign_glyph_to_token(token)
        gate = self.evaluate_agency_gate(token)

        if gate == "externalize":
            self.externalize_token(token)
            return [glyph]

        result = [glyph]
        for adjacent in self.get_adjacencies_for_token(token):
            self._log(self.adj_log, {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "from": token,
                "to": adjacent,
                "depth": depth,
            })
            result.extend(self.recursive_thought_loop(adjacent, depth + 1, max_depth, visited))
        return result

    def evaluate_agency_gate(self, token):
        glyph = self.token_map.get(token, {})
        weight = glyph.get("modalities", {}).get("text", {}).get("weight", 1)
        adj_count = len(self.adjacency_map.get(token, []))
        token_data = {"frequency": weight, "weight": weight}
        decisions = process_agency_gates(token, token_data, adj_count)
        for d in decisions:
            if d["decision"] == "YES":
                return d["gate"]
        return random.choice([d["gate"] for d in decisions])

    def externalize_token(self, token):
        print(f"Externalizing token: {token} with glyph: {self.token_map[token]}")

    def add_glyph_to_pool(self, glyph):
        self.glyph_pool.append(glyph)

    def traverse_superknowledge(self, start_token, steps=5):
        return self.graph.traverse(start_token, max_steps=steps)
