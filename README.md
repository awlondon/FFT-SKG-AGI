# FFT-SKG-AGI

This project explores a minimal symbolic cognition loop. The `SKGEngine` maps tokens to glyphs and recursively walks their adjacencies. When a token is externalized the console is cleared and a compressed view of the last thought loop is displayed.

## Usage

Run the main script and enter tokens at the prompt:

```bash
python main.py
```

Externalization events are indicated with a clear screen followed by the most recent tokens processed.

During these events `main.py` clears the terminal with `cls` or `clear` and prints a concise list of the latest thought loop tokens.

### Engine messages

`assign_glyph_to_token` now prints whether a glyph was reused or newly assigned and shows the current weight. `externalize_token` reports the glyph and weight being externalized.
