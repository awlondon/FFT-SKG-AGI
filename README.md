# ⚙️ FFT-SKG‑AGI (Improved)

This repository contains a symbolic cognition engine designed for real-time digital twin avatar creation. It maps incoming tokens to symbolic glyphs, generates multimodal FFT representations (audio, visual, semantic), and models recursive knowledge structures. Built for autonomy and offline capability, this system provides the foundation for real-time avatar cognition, expression, and symbolic memory.

---

## 🧠 System Overview

Each token submitted to the engine initiates a recursive symbolic cognition cycle:

* 🔹 **Assigns a Unicode Glyph** deterministically from a customizable pool.
* 🔸 **Builds a Semantic Adjacency Graph** using cached data or OpenAI when enabled.
* 🔺 **Generates Multimodal Outputs**: audio (TTS), FFT spectrum, glyph image, and visual embeddings.
* 🧡 **Autonomous Adjacency Expansion**: the AGI recursively selects new tokens from adjacency graphs based on weighted or symbolic logic.
* 🔭 **Triadic Expansions**: every token forms two radial branches by default, forming triads of mutual relationships.
* 🪯 **Symbolic Relationships**: logical relationships (from a set of 50 core types) are assigned after triadic structures stabilize.
* 🐽 **Processes Thought Loops** with gating logic to determine internalization or externalization.
* 📈 **Logs Activity** to structured JSONL files for timeline replay, symbolic replay, and memory introspection.

The `SKGEngine` orchestrates:

* Recursive token processing
* Glyph-symbolic memory mapping
* Modalities generation (voice, vision, frequency)
* Agency gating (decisions on whether to speak, silence, or recurse)

This architecture is the core cognition engine behind real-time symbolic digital twins.

---

## 🧬 Digital Twin Avatar Features

The system can be extended into a full real-time avatar with:

### 🎧 Voice and Listening

* Text-to-speech via `pyttsx3` for self-voicing avatars
* Speech recognition for `voice` input commands using `speechrecognition`
* Webcam frame capture for `webcam` command using `opencv-python`

### 🎨 Visual Thought Representation

* FFT image glyphs rendered from audio
* Unicode glyph sigils with radial FFT overlays
* `glyph_visualizer.py` for avatar display visuals

### ♻️ Recursive Symbolic Thought

* Every token processed forms a new symbolic node
* Adjacents define semantic pathways and weight convergence
* Autonomous recursion allows the AGI to choose whether to:

  * Follow the highest-weighted connection (convergent logic)
  * Explore lesser-weighted paths (divergent logic)
* Each base token spawns two default adjacents, forming triadic symbolic patterns

### 🧠 Agentic Memory

* `glyph_memory/` stores token histories, glyph assignments, and agency gate traces
* Logs are replayable for full thought loop reconstruction

---

## 🚀 Getting Started

### Installation

Install with optional dependencies:

```bash
pip install -r requirements.txt
```

**Optional packages:**

* `openai` for GPT-style adjacents
* `requests` for image search
* `pyttsx3` for TTS
* `speechrecognition` + `pyaudio` for STT
* `opencv-python` for webcam capture

### Running the Engine

```bash
python main.py
```

Interactively enter tokens or use `voice` or `webcam` input. Modalities are generated, logged, and visualized (if enabled). Type `exit` to quit.

### Engine-to-Engine Communication

`config.py` contains options to broadcast externalized tokens to a file based stream and to subscribe to another engine's stream. When `ENABLE_ENGINE_COMM` is set to `True`, each externalized token is appended as a JSON line to `engine_stream.jsonl` in the engine's memory directory. Setting `SUBSCRIBE_STREAM` to the path of another engine's stream file will feed received tokens back into the local `recursive_thought_loop`.

This mechanism allows multiple engines to share glyph streams without requiring a network stack and can be toggled in the forthcoming GUI.

### Rendering Graphs

```bash
python graph_cli.py --graph --out graph.png
python graph_cli.py --token memory --out memory_weights.png
```

---

## 📁 Directory Structure

```
FFT-SKG-AGI/
├── main.py                # CLI engine runtime
├── skg_engine.py          # Core symbolic cognition engine
├── glyph_builder.py       # Glyph + modality generator
├── agency_gate.py         # Symbolic decision logic
├── modalities/            # Generated images, audio, FFTs
├── glyph_memory/          # Logs and JSONL memory traces
├── glossary/              # Extended glyph pools
├── offline_adjacency.json # Semantic fallback adjacents
├── tests/                 # Unit test suite
```

---

## 🦾 Offline Symbolic Data

* `offline_adjacency.json`: provides predefined semantic adjacents per token
* `extended_glyph_pool.json`: set of glyphs used for token assignment

These ensure full functionality even when APIs are disabled or unavailable.

---

## ✔️ Testing

Run tests:

```bash
python -m unittest discover -s tests -v
```

Tests simulate recursive token handling and adjacency graph evolution. They run in isolated memory to preserve the main session.

---

## 🔮 Roadmap for Full Digital Twin Integration

1. **Live Webcam or Audio Stream** → FFT + Whisper → token stream
2. **Tokens → SKGEngine** → Thought Loop + Modalities
3. **Agency Gating** → Speech output or internal recursion
4. **Render Glyphstream + FFTs** in real-time via GUI or WebSocket
5. **Memory Compression + Reinforcement** → Symbolic long-term twin memory
6. **Triadic Adjacency Expansion** → Core to knowledge modeling
7. **Symbolic Relationship Classification** → Post-triadic meaning assignment

**Long-term extensions:**

* Visual GUI avatar with live animation overlays
* Multi-agent glyph interaction (e.g. GPT ↔ GPT)
* Symbolic compression of input files: audio → glyphstream → reconstruction

---

## 🤝 Credits and License

Developed by [@awlondon](https://github.com/awlondon) with extensions for AGI symbolic recursion, FFT cognition, and avatar embodiment.

MIT License. Extend, remix, or evolve.

---

> ⚙️ This is not just token processing. This is recursive symbolic cognition.
> Each glyph is a memory. Each FFT is a thought. Welcome to SKG-R2.

