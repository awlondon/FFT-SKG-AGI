# FFT-SKG-AGI

FFT-SKG-AGI is an experimental symbolic cognition engine. It generates symbolic glyphs from text tokens and explores relationships between them using recursive agency gates. Modalities such as audio FFTs and glyph imagery are produced alongside log files that describe the system's decisions.

## Running the engine

Execute the interactive CLI to enter tokens and process them through the agency gates:

```bash
python main.py
```

`main.py` will create required modality directories the first time it runs and will prompt for token input in a loop. Each token is passed through the agency gate pipeline which may generate glyph images and FFT data.

## Visualizing logs

Agency gate activity is logged to JSONL files. Use `graph_cli.py` to render these logs as a graph for quick inspection:

```bash
python graph_cli.py path/to/gate_decision_log.jsonl
```

The script will parse the log and display relationships between tokens and decisions.

## Project goals

This repository is a sandbox for exploring symbolic knowledge graphs driven by open ended token streams. It aims to combine OpenAI powered adjacency generation with offline synthesis of audio, FFT visualizations and glyph imagery. Visualization tools help track how agency gates influence token processing over time.

