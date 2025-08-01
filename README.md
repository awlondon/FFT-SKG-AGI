# FFT-SKG-AGI

Symbolic cognition engine generating glyphs and FFT based representations for tokens. The project assigns unique glyphs to input text, expands semantic adjacents and produces audio and image FFTs for later visualization.

```
 +-------+        +---------------+        +-------------+
 | input | -----> | glyph builder | -----> | modalities |
 +-------+        +---------------+        +-------------+
                        |                        |
                        v                        v
                   agency gates            FFT/visual output
```

## Components

- **skg_engine.py** – orchestrates token processing and persistence
- **glyph_builder.py** – creates glyph records and modalities
- **modalities.py** – generates TTS, FFT and images
- **adjacency_seed.py** – provides semantic adjacents (GPT or offline)
- **glyph_decision_engine.py** – selects glyphs via agency gates

## Setup

1. `pip install -r requirements.txt`
2. Optional: set `OPENAI_API_KEY` for online adjacency generation

Run tests with `python -m unittest -v`.

## Usage

```
$ python cli.py fire
{'token': 'fire', 'glyph': 'f', 'fft_image': 'modalities/fft_visual/<hash>.png'}
```

Glyphs and logs are stored in `glyph_output/` by default. The symbolic stream log lives at `glyph_output/logs/symbolic_stream.jsonl`.

