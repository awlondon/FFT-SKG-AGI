import unittest
from agency_gate import process_agency_gates

class TestAgencyGate(unittest.TestCase):
    def test_decision_structure(self):
        decisions = process_agency_gates('fire', {'frequency': 2, 'weight': 3}, adjacency_count=1)
        self.assertTrue(all('gate' in d and 'decision' in d for d in decisions))

if __name__ == '__main__':
    unittest.main()
