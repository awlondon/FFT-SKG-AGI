# FFT-SKG-AGI

FFT-SKG-AGI is a prototype symbolic cognition engine. It maps text tokens to glyphs and generates multimodal artifacts such as audio, FFT visuals and images. The system uses lightweight agency gates to decide whether to explore or externalize thoughts.

## Setup

1. Install Python 3.10 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys.

## Environment Variables

- `OPENAI_API_KEY` – required for generating adjacencies and glyph choices.
- `SERPAPI_API_KEY` – optional for image search results.

## Usage

Run the demo loop:
```bash
python main.py
```
Enter tokens and the engine will create glyph data under `glyph_memory/`.

## Development

Run tests with:
```bash
pytest -q
```

Contributions are welcome! See `CONTRIBUTING.md` for guidelines.
