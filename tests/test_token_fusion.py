import os
import json
import tempfile
import unittest
from token_fusion import TokenFusion
from glyph_builder import build_glyph_if_needed


class TestTokenFusion(unittest.TestCase):
    def test_text_and_stt_share_glyph(self):
        fusion = TokenFusion()
        phrase = "hello world"
        tid_text = fusion.fuse_token(phrase)
        tid_speech = fusion.fuse_from_stt(phrase)
        self.assertEqual(tid_text, tid_speech)

        with tempfile.TemporaryDirectory() as tmp:
            glyph1 = build_glyph_if_needed(phrase, base_dir=tmp, adj_count=1)
            glyph2 = build_glyph_if_needed(phrase, base_dir=tmp, adj_count=1)
            path = os.path.join(tmp, f"{tid_text}.json")
            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["token"], phrase)
            self.assertEqual(glyph1["glyph_id"], glyph2["glyph_id"])


if __name__ == "__main__":
    unittest.main()
