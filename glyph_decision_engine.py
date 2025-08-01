"""Glyph decision helper integrated with agency gates."""

from __future__ import annotations

import random
from typing import List, Optional

import config
from agency_gate import process_agency_gates


class AgencyGateManager:
    """Lightweight wrapper around :func:`process_agency_gates`."""

    def evaluate(self, gate: str, token: str, adj_count: int = 0) -> str:
        data = {"frequency": 1, "weight": 1}
        for d in process_agency_gates(token, data, adj_count):
            if d.get("gate") == gate:
                return d.get("decision", "NO")
        return "NO"


class AGIDecision:
    """Choose glyphs with agency gate feedback."""

    def __init__(self, glyph_pool: List[str]):
        self.glyph_pool = glyph_pool
        self.attempts: dict[str, int] = {}
        self.manager = AgencyGateManager()

    def choose(self, token: str, adjacents: Optional[List[dict]] = None) -> str:
        adj_count = len(adjacents or [])
        pool = self.glyph_pool or ["□"]
        self.attempts.setdefault(token, 0)

        for idx, glyph in enumerate(pool):
            decision = self.manager.evaluate("decide_glyph", token, adj_count)
            if decision == "YES":
                self.attempts[token] = 0
                return glyph
            self.attempts[token] += 1
            if self.attempts[token] >= config.CONFIRMATION_THRESHOLD:
                break
        return "□"


def choose_glyph_for_token(token: str, adjacents: Optional[List[dict]] = None) -> str:
    """Fallback helper using a temporary :class:`AGIDecision`."""
    pool = ["□", "○", "●", "■", "◆"]
    decider = AGIDecision(pool)
    return decider.choose(token, adjacents)
