class SKGThoughtTracker:
    """
    Collects trace data during recursive thought loops.  This structure
    captures adjacency transitions, convergence events, expansions and
    complete thought loops.  It can be reset after an externalization.
    """
    def __init__(self) -> None:
        self.adjacency_deltas: list[dict] = []
        self.convergence_deltas: list[dict] = []
        self.thought_loops: list[dict] = []
        self.expansion_chain: list[dict] = []

    def log_adjacency(self, from_token: str, to_token: str, slot: int, weight_delta: int = 1) -> None:
        self.adjacency_deltas.append({
            "from": from_token,
            "to": to_token,
            "slot": slot,
            "weight_delta": weight_delta
        })

    def log_convergence(self, token_list: list[str], overlap_count: int, new_slots_created: int) -> None:
        self.convergence_deltas.append({
            "tokens": token_list,
            "overlaps": overlap_count,
            "new_slots": new_slots_created
        })

    def log_thought_loop(self, token: str, depth: int, glyphs_visited: list, externalized: bool) -> None:
        self.thought_loops.append({
            "token": token,
            "depth": depth,
            "glyphs_visited": glyphs_visited,
            "externalized": externalized
        })

    def log_expansion(self, source_token: str, introduced_token: str, origin_glyph: dict | None) -> None:
        self.expansion_chain.append({
            "source": source_token,
            "new_token": introduced_token,
            "via_glyph": origin_glyph
        })

    def reset(self) -> None:
        self.__init__()