# ⚙️ FFT-SKG‑AGI (Improved)

This repository contains a lightweight symbolic cognition engine that maps
incoming tokens to unicode glyphs, records adjacency relationships and
generates multimodal representations such as audio, images and FFT
visualizations.  The project is a sandbox for exploring recursive thought
loops and emergent knowledge graphs while remaining self‑contained and
offline friendly.

## 🧠 Overview

For each token you supply the engine will:

- 🔹 Assign a unicode glyph selected deterministically from a pool.
- 🔸 Record semantically adjacent tokens (either from an offline cache or
  via OpenAI when available) and update an adjacency graph.
- 🔺 Optionally externalize the token by producing a simple glyph image.
- 📈 Log weight updates and adjacency traversals to JSONL files for later
  visualization.

The `SKGEngine` orchestrates thought loops, persistence and simple
heuristic gating.  Audio synthesis, FFT generation and image search are
implemented but disabled by default when dependencies or API keys are
missing.

## 🚀 Getting Started

### Installation

Install dependencies listed in `requirements.txt` (optionally using a
virtual environment):

```bash
pip install -r requirements.txt
```

Optional dependencies include:

- `openai` for generating semantic adjacents when the `OPENAI_API_KEY`
  environment variable is set.
- `requests` for image search via SerpAPI when `SERPAPI_API_KEY` is set.
- `pyttsx3` for offline text‑to‑speech synthesis.
- `speechrecognition` for optional voice input.

### Running the Engine

Execute the CLI and enter tokens interactively:

```bash
python main.py
```

On first run it will create a `glyph_memory/` directory for persistence and
subfolders under `modalities/` for generated assets.  Type tokens or
`voice` to transcribe spoken input.  Type `exit` to quit.

### Visualizing Logs

The `graph_cli.py` script can render the adjacency graph and plot token
weight histories:

```bash
python graph_cli.py --graph --out my_graph.png
python graph_cli.py --token hello --out hello_weights.png
```

## 🧾 Offline Data

- `glossary/extended_glyph_pool.json` – list of unicode glyphs used by
  the engine.  Feel free to add or remove glyphs to customize the pool.
- `offline_adjacency.json` – dictionary mapping tokens to a list of
  pre‑computed adjacents.  Populating this file allows the engine to
  operate without network access.

## 🛠️ Development Notes

This improved version of FFT‑SKG‑AGI adds the following features:

1. **Deterministic glyph selection:** tokens are hashed into the glyph pool
   for reproducible assignments.
2. **Offline friendly:** all external dependencies are optional.  The
   engine falls back to simple heuristics or cached data when APIs are
   unavailable.
3. **Graceful error handling:** network and I/O failures are caught and
   reported without interrupting the thought loop.
4. **Modular testing:** the `tests/` directory contains simple unit tests
   demonstrating basic behaviour of the `SKGEngine`.

## ✔️ Testing

Run the test suite with `pytest`:

```bash
pytest -q
```

The tests create temporary `glyph_memory` directories so they do not
interfere with the main engine's persisted state.