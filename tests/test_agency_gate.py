import unittest
from agency_gate import process_agency_gates, AgencyGateDecision

class TestAgencyGate(unittest.TestCase):
    def test_decision_structure(self):
        decisions = process_agency_gates('fire', {'frequency': 2, 'weight': 3}, adjacency_count=1)
        self.assertTrue(all(isinstance(d, AgencyGateDecision) for d in decisions))
        self.assertTrue(all(0.0 <= d.confidence <= 1.0 for d in decisions))

if __name__ == '__main__':
    unittest.main()
