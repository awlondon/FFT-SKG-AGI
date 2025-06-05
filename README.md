# FFT-SKG-AGI

This project contains a collection of utilities for generating glyphs and Fourier-transform based visuals. Some features depend on the [Symbola](https://fontlibrary.org/en/font/symbola) font to render Unicode glyphs.

## Obtaining the Symbola font

The repository does not include the `Symbola.ttf` file. You can download it from the author's website or from a trusted font repository such as [Font Library](https://fontlibrary.org/en/font/symbola). After downloading, place `Symbola.ttf` somewhere accessible, for example in a directory named `_fonts` at the project root:

```bash
mkdir _fonts
mv /path/to/Symbola.ttf _fonts/
```

## Using the font with `generate_glyph_image`

The `generate_glyph_image` function in `glyph_visualizer.py` accepts a `font_path` argument. Pass the location of your downloaded font when calling it:

```python
from glyph_visualizer import generate_glyph_image

image_path = generate_glyph_image("A", font_path="_fonts/Symbola.ttf")
```

If `font_path` is omitted and the default path does not point to a valid file, the function falls back to the default Pillow font.
