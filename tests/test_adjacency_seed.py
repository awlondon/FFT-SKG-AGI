import unittest

try:
    from adjacency_seed import generate_adjacents
except Exception:
    generate_adjacents = None

class TestAdjacencySeed(unittest.TestCase):
    def test_offline_data(self):
        if generate_adjacents is None:
            self.skipTest('openai module not available')
        adjs = generate_adjacents('fire')
        self.assertTrue(any(a['token'] == 'flame' for a in adjs))

if __name__ == '__main__':
    unittest.main()
