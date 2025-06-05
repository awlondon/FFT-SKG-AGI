# FFT-SKG-AGI

FFT-SKG-AGI is an experimental symbolic cognition engine. Tokens are expanded into glyphs and multiple modalities including audio, FFT data, and images. Some functionality relies on OpenAI APIs and image search via SerpAPI.

## Setup

1. Create a Python 3 environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set required environment variables:
   - `OPENAI_API_KEY` – used by modules that request completions from OpenAI.
   - `SERPAPI_API_KEY` – used for fetching reference images via SerpAPI.

## Usage

Run the interactive loop from the repository root:

```bash
python main.py
```

The program will prompt for tokens, generate glyphs and related data, and print agency gate decisions to the console.

