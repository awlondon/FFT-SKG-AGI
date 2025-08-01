import os
import tempfile
import unittest
from unittest.mock import patch

from adjacency_seed import generate_adjacents
from glyph_builder import build_glyph_if_needed
from glyph_decision_engine import AGIDecision
from token_fusion import TokenFusion


class TestPipeline(unittest.TestCase):
    def test_adjacency_generation(self):
        adjs = generate_adjacents("fire")
        tokens = [a["token"] for a in adjs]
        self.assertIn("flame", tokens)

    def test_glyph_build_and_fft(self):
        with tempfile.TemporaryDirectory() as tmp:
            fusion = TokenFusion()
            glyph = build_glyph_if_needed("flame", base_dir=tmp, adj_count=1)
            token_id = fusion.fuse_token("flame")
            json_path = os.path.join(tmp, f"{token_id}.json")
            self.assertTrue(os.path.exists(json_path))

    def test_agidecision_fallback(self):
        decider = AGIDecision(["A", "B", "C"])
        with patch("agency_gate.process_agency_gates", return_value=[{"gate": "decide_glyph", "decision": "NO"}]):
            glyph = decider.choose("token")
            self.assertEqual(glyph, "□")


if __name__ == "__main__":
    unittest.main()
