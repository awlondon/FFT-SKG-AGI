import os
import numpy as np
from PIL import Image


def generate_fft_from_image(image_path: str, output_dir: str = "modalities/fft_visual", max_dim: int = 512) -> str | None:
    """
    Generate a normalized FFT image from the given file.  The result is saved
    into `output_dir` and the path to the generated image is returned.  If
    any errors occur during processing None is returned.
    """
    print(f"[FFT] Generating FFT from image: {image_path}")
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(image_path):
        print(f"[FFT] Image not found: {image_path}")
        return None
    try:
        img = Image.open(image_path).convert("L")
        img = img.resize((max_dim, max_dim), Image.ANTIALIAS)
        arr = np.array(img)
        fft = np.fft.fftshift(np.fft.fft2(arr))
        magnitude = np.abs(fft)
        magnitude = np.log1p(magnitude)
        if np.max(magnitude) == 0:
            print("[FFT] Warning: zero magnitude in FFT result")
            return None
        magnitude = (magnitude / np.max(magnitude) * 255).astype(np.uint8)
        magnitude = 255 - magnitude
        center = (magnitude.shape[0] // 2, magnitude.shape[1] // 2)
        y, x = np.ogrid[: magnitude.shape[0], : magnitude.shape[1]]
        distance = np.sqrt((x - center[1]) ** 2 + (y - center[0]) ** 2)
        fade = 1 - (distance / np.max(distance))
        magnitude = (magnitude * fade).astype(np.uint8)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        fft_filename = f"{base_name}_fft_spark.png"
        fft_output_path = os.path.join(output_dir, fft_filename)
        Image.fromarray(magnitude, mode="L").save(fft_output_path)
        print(f"[FFT] FFT image saved to: {fft_output_path}")
        return fft_output_path
    except Exception as e:
        print(f"[FFT] Error generating FFT from image: {e}")
        return None