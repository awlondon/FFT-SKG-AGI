import unittest
from unittest.mock import patch
import tempfile

from skg_engine import SKGEngine

class TestModality(unittest.TestCase):
    def test_evaluate_agency_gate_modality(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = SKGEngine(tmp)
            engine.token_map['wave'] = {'token': 'wave', 'modalities': {'text': {'weight': 1}}}
            gate, modality, conf = engine.evaluate_agency_gate('wave')
            self.assertEqual(modality, 'gesture')
            self.assertLessEqual(conf, 0.6)
            engine.token_map['hello'] = {'token': 'hello', 'modalities': {'text': {'weight': 4}}}
            gate, modality, conf = engine.evaluate_agency_gate('hello')
            self.assertEqual(modality, 'speak')
            self.assertGreater(conf, 0.5)

    def test_externalize_token_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = SKGEngine(tmp)
            with patch('skg_engine.speak') as mock_speak, patch('skg_engine.display_gesture') as mock_gesture:
                engine.externalize_token('hi', modality='speak')
                mock_speak.assert_called_once_with('hi')
                mock_gesture.assert_not_called()
                mock_speak.reset_mock()
                engine.externalize_token('wave', modality='gesture')
                mock_gesture.assert_called_once_with('wave')
                mock_speak.assert_not_called()

if __name__ == '__main__':
    unittest.main()
