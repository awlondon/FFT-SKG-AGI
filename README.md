# FFT-SKG-AGI

FFT-SKG-AGI is a symbolic cognition engine that assigns a glyph to every token
and generates multimodal representations. Tokens are expanded with semantic
adjacents (using GPT or an offline lookup) and the resulting glyph data drives
text‑to‑speech, FFT analysis and image search.

```
 +-------+        +---------------+        +-------------+
 | input | -----> | glyph builder | -----> | modalities |
 +-------+        +---------------+        +-------------+
                        |                        |
                        v                        v
                   agency gates            FFT/visual output
```

## Components

- **skg_engine.py** – orchestrates token processing, persistence and recursive
  thought loops
- **glyph_builder.py** – creates glyph records and modalities
- **glyph_decision_engine.py** – selects glyphs via agency gates
- **adjacency_seed.py** – provides semantic adjacents (GPT or offline)
- **modalities.py** – generates TTS, FFT and images
- **glyph_visualizer.py** – renders glyph images
- **agency_gate.py** – applies gating decisions
- **graph_cli.py** – visualizes adjacency graphs and weight history
- **main.py** – CLI entry point with optional voice and webcam input

## Setup

1. Install dependencies: `pip install -r requirements.txt`
   (includes `numpy`, `Pillow`, `pyttsx3`, `networkx`, etc.)
2. Optional environment variables:
   - `OPENAI_API_KEY` – enable online adjacency queries
   - `SERPAPI_API_KEY` – enable image search

Run tests with:

```bash
python -m unittest -v
```

## Usage

```
$ python cli.py fire
{'token': 'fire', 'glyph': 'f', 'fft_image': 'modalities/fft_visual/<hash>.png'}
```

Glyphs and logs are stored in `glyph_output/` by default. The symbolic stream log lives at `glyph_output/logs/symbolic_stream.jsonl`.

## Directory Layout

- `glossary/` – default glyph pool used by the engine
- `modalities/` – generated audio, images and FFT visualizations
- `glyph_output/` – persisted glyph objects and log files

