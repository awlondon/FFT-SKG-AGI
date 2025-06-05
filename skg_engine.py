import json
from datetime import datetime
import random
from typing import Optional

class SKGEngine:
    def __init__(self, memory_path: str, glyph_path: Optional[str] = None):
        """Initialize the SKG engine.

        Parameters
        ----------
        memory_path : str
            Path where glyph memory files are stored.
        glyph_path : Optional[str], default "glossary/extended_glyph_pool.json"
            JSON file containing a list of glyphs to populate ``glyph_pool``.
        """

        self.memory_path = memory_path
        self.glyph_list_path = glyph_path or "glossary/extended_glyph_pool.json"

        # Load available glyphs from file
        try:
            with open(self.glyph_list_path, "r", encoding="utf-8") as f:
                self.glyph_pool = json.load(f)
        except Exception as e:
            print(f"[SKGEngine] Unable to load glyphs from {self.glyph_list_path}: {e}")
            self.glyph_pool = []

        self.token_map = {}  # Maps tokens to glyphs
        self.adjacency_map = {}  # Maps tokens to their adjacencies (could be semantic or contextual)

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

    def add_glyph_to_pool(self, glyph):
        """Add a new glyph to the glyph pool."""
        self.glyph_pool.append(glyph)
