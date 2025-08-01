import unittest
import tempfile
from unittest.mock import patch

from agency_gate import process_agency_gates
from skg_engine import SKGEngine, AgencyGateDecision


class TestAgencyGate(unittest.TestCase):
    def test_decision_structure(self):
        decisions = process_agency_gates('fire', {'frequency': 2, 'weight': 3}, adjacency_count=1)
        self.assertTrue(any(d['gate'] == 'expression' for d in decisions))
        for d in decisions:
            self.assertIn('gate', d)
            self.assertIn('decision', d)
            if d['gate'] == 'expression':
                self.assertIn('confidence', d)

    def test_engine_handles_dict_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = SKGEngine(tmp)
            engine.token_map['foo'] = {'token': 'foo', 'modalities': {'text': {'weight': 1}}}
            decisions = [
                {'gate': 'expression', 'decision': 'gesture', 'confidence': 0.55},
                {'gate': 'explore', 'decision': 'YES', 'confidence': 0.8},
            ]
            with patch('skg_engine.process_agency_gates', return_value=decisions):
                gate, modality, conf = engine.evaluate_agency_gate('foo')
                self.assertEqual(gate, 'explore')
                self.assertEqual(modality, 'gesture')
                self.assertEqual(conf, 0.55)

if __name__ == '__main__':
    unittest.main()
