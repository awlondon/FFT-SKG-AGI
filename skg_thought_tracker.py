class SKGThoughtTracker:
    def __init__(self):
        self.adjacency_deltas = []
        self.convergence_deltas = []
        self.thought_loops = []
        self.expansion_chain = []

    def log_adjacency(self, from_token, to_token, slot, weight_delta=1):
        self.adjacency_deltas.append({
            "from": from_token,
            "to": to_token,
            "slot": slot,
            "weight_delta": weight_delta
        })

    def log_convergence(self, token_list, overlap_count, new_slots_created):
        self.convergence_deltas.append({
            "tokens": token_list,
            "overlaps": overlap_count,
            "new_slots": new_slots_created
        })

    def log_thought_loop(self, token, depth, glyphs_visited, externalized):
        self.thought_loops.append({
            "token": token,
            "depth": depth,
            "glyphs_visited": glyphs_visited,
            "externalized": externalized
        })

    def log_expansion(self, source_token, introduced_token, origin_glyph):
        self.expansion_chain.append({
            "source": source_token,
            "new_token": introduced_token,
            "via_glyph": origin_glyph
        })

    def reset(self):
        self.__init__()
