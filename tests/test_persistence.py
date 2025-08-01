import os
import json
import tempfile
import unittest

from skg_engine import SKGEngine

class TestPersistence(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = SKGEngine(tmp)
            engine.add_glyph_to_pool('🜂')
            engine.update_adjacency_map('fire', ['heat'])
            engine.assign_glyph_to_token('fire')
            engine.save_state()

            # Create new engine to load state
            engine2 = SKGEngine(tmp)
            self.assertIn('fire', engine2.token_map)
            self.assertIn('fire', engine2.adjacency_map)

    def test_binary_and_encrypted_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            key = b'secret'
            engine = SKGEngine(tmp, binary=True, encrypt_key=key)
            engine.add_glyph_to_pool('🜂')
            engine.update_adjacency_map('fire', ['heat'])
            engine.assign_glyph_to_token('fire')
            engine.save_state()

            engine2 = SKGEngine(tmp, binary=True, encrypt_key=key)
            self.assertIn('fire', engine2.token_map)
            self.assertIn('fire', engine2.adjacency_map)

    def test_binary_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = SKGEngine(tmp, binary=True)
            engine.add_glyph_to_pool('🜂')
            engine.update_adjacency_map('fire', ['heat'])
            engine.assign_glyph_to_token('fire')
            engine.save_state()

            engine2 = SKGEngine(tmp, binary=True)
            self.assertIn('fire', engine2.token_map)
            self.assertIn('fire', engine2.adjacency_map)

if __name__ == '__main__':
    unittest.main()
