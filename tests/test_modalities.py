import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modalities import generate_modalities


def test_generate_modalities(monkeypatch, tmp_path):
    monkeypatch.setattr('tts_engine.generate_tts', lambda text, path: None)
    monkeypatch.setattr('fft_generator.generate_fft_from_audio', lambda a,b,c: None)
    monkeypatch.setattr('generate_fft_from_image.generate_fft_from_image', lambda p: None)
    monkeypatch.setattr('image_search.fetch_images_from_serpapi', lambda t,g,max_results=3: [])
    monkeypatch.setattr('glyph_visualizer.generate_glyph_image', lambda g: str(tmp_path/"glyph.png"))

    result = generate_modalities('token','g')
    assert 'audio' in result
    assert 'visual' in result
