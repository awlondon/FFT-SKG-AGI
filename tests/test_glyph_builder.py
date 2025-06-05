import json
from pathlib import Path
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from glyph_builder import build_glyph_if_needed


def test_build_glyph(monkeypatch, tmp_path):
    token = "test"
    expected_adj = [{"token": "a"}]
    monkeypatch.setattr('glyph_builder.generate_adjacents', lambda t: expected_adj)
    monkeypatch.setattr('glyph_decision_engine.choose_glyph_for_token', lambda t, adj: "⟁")
    monkeypatch.setattr('modalities.generate_modalities', lambda t, g: {"dummy": True})

    path = tmp_path / f"{token}.json"
    glyph = build_glyph_if_needed(token, str(path))
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["token"] == token
    assert data["adjacents"] == expected_adj
