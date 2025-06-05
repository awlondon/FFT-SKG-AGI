# FFT-SKG-AGI

This project contains various utilities for experimenting with symbolic knowledge graph (SKG) ideas. Glyphs are associated with tokens and expanded into different modalities like audio, FFT visualizations and images.

## Requirements

The code expects the following Python packages:

- `openai`
- `requests`
- `numpy`
- `scipy`
- `matplotlib`
- `Pillow`
- `pyttsx3`

You will also need API keys for OpenAI and SerpAPI available in the `OPENAI_API_KEY` and `SERPAPI_API_KEY` environment variables.

## Usage

Run the interactive loop with:

```bash
python main.py
```

Enter a token to generate its glyph and modalities. Generated data is stored under the `modalities/` directory and `glyph_memory/` JSON files.  The scripts use local text‑to‑speech and FFT generation, so running them may take a few moments per token.

