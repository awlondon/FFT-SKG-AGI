import unittest
from agency_gate import process_agency_gates

class TestAgencyGate(unittest.TestCase):
    def test_decision_structure(self):
        decisions = process_agency_gates('fire', {'frequency': 2, 'weight': 3}, adjacency_count=1)
        self.assertTrue(any(d['gate'] == 'expression' for d in decisions))
        for d in decisions:
            self.assertIn('gate', d)
            self.assertIn('decision', d)
            if d['gate'] == 'expression':
                self.assertIn('confidence', d)

if __name__ == '__main__':
    unittest.main()
