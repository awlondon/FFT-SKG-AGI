import json
from datetime import datetime
import random
import os
from superknowledge_graph import SuperKnowledgeGraph

class SKGEngine:
    def __init__(self, memory_path, glyph_pool_path="glossary/extended_glyph_pool.json"):
        self.memory_path = memory_path
        self.glyph_pool = []  # Holds available glyphs
        if os.path.exists(glyph_pool_path):
            try:
                with open(glyph_pool_path, "r", encoding="utf-8") as f:
                    self.glyph_pool = json.load(f)
            except Exception as e:
                print(f"[SKGEngine] Failed to load glyph pool: {e}")
        else:
            print(f"[SKGEngine] Glyph pool file not found at {glyph_pool_path}")
        self.token_map = {}  # Maps tokens to glyphs
        self.adjacency_map = {}  # Maps tokens to their adjacencies (could be semantic or contextual)
        # Superknowledge graph composed of nested matrices
        self.graph = SuperKnowledgeGraph()

    def update_glyph_weight(self, glyph):
        """Increment symbolic weight for existing glyph or initialize if absent."""
        if "modalities" in glyph and "text" in glyph["modalities"]:
            if "weight" in glyph["modalities"]["text"]:
                glyph["modalities"]["text"]["weight"] += 1
            else:
                glyph["modalities"]["text"]["weight"] = 1
        else:
            glyph.setdefault("modalities", {}).setdefault("text", {})["weight"] = 1
        
        glyph["last_updated"] = datetime.utcnow().isoformat() + "Z"
        return glyph

    def assign_glyph_to_token(self, token, adjacency=None):
        """Assign a glyph to a token, considering its adjacency and context."""
        # Ensure this function assigns a glyph like 🜂, ⚚, etc.
        if token in self.token_map:
            glyph = self.token_map[token]
        else:
            # Select an actual symbolic glyph (not the token text)
            glyph = self.select_glyph_for_token(token, adjacency)
            self.token_map[token] = glyph

        # Update the glyph's weight
        glyph = self.update_glyph_weight(glyph)
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

    def recursive_thought_loop(self, token, depth=0, max_depth=5):
        """Perform a recursive exploration of a token's adjacencies, activating agency gates."""
        if depth >= max_depth:
            return []

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
            result.extend(self.recursive_thought_loop(adjacent_token, depth + 1, max_depth))

        return result

    def evaluate_agency_gate(self, token):
        """Evaluate which agency gate should be activated based on the token's context."""
        # For now, a random decision is made (this could be made more sophisticated based on token's state)
        decisions = ['explore', 'reevaluate', 'externalize', 'prune']
        return random.choice(decisions)

    def externalize_token(self, token):
        """Externalize the token's glyph (i.e., generate its output)."""
        # Here we would trigger the visual/audio generation for the token's glyph
        print(f"Externalizing token: {token} with glyph: {self.token_map[token]}")

    def update_adjacency_map(self, token, adjacencies):
        """Update the adjacency map for a given token."""
        self.adjacency_map[token] = adjacencies
        # Store connections in the default matrix of the superknowledge graph
        for adj in adjacencies:
            self.graph.connect("global", token, adj)

    def add_glyph_to_pool(self, glyph):
        """Add a new glyph to the glyph pool."""
        self.glyph_pool.append(glyph)

    def traverse_superknowledge(self, start_token, steps=5):
        """Walk through overlapping matrices starting from a token."""
        return self.graph.traverse(start_token, max_steps=steps)
