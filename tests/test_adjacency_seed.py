import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adjacency_seed import generate_adjacents


def test_generate_adjacents_no_api_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    result = generate_adjacents('token')
    assert result == []
