import logging
import os
import cv2
import numpy as np
from PIL import Image as PilImage
import matplotlib.pyplot as plt
from datetime import datetime

def generate_fft_from_image(image):
    """Generate FFT from an image and return the normalized result."""
    arr = np.array(image)
    fft_result = np.fft.fftshift(np.fft.fft2(arr))
    magnitude = np.abs(fft_result)
    norm = (magnitude / np.max(magnitude)) * 255 if np.max(magnitude) else magnitude
    return np.uint8(norm)

def normalize_and_generate_fft(input_path, output_path, max_dim=512, colormap=None):
    """
    Normalize an image and generate its FFT, saving it as a white-on-black radial image.
    """
    from PIL import Image
    import numpy as np
    import os

    try:
        # Ensure the input image exists
        if not os.path.exists(input_path):
            logging.error(f"[ERROR] Input image not found: {input_path}")
            return
        logging.debug(f"[DEBUG] Input image exists: {input_path}")

        # Load the input image
        img = Image.open(input_path).convert("L")  # Ensure grayscale
        logging.debug(f"[DEBUG] Input image loaded successfully. Image size: {img.size}, mode: {img.mode}")

        # Resize the image
        logging.debug(f"[DEBUG] Resizing image to max dimensions: {max_dim}x{max_dim}")
        img = img.resize((max_dim, max_dim), Image.ANTIALIAS)

        # Perform FFT
        logging.debug(f"[DEBUG] Performing FFT on the image...")
        img_array = np.array(img)
        fft = np.fft.fftshift(np.fft.fft2(img_array))  # Shift zero frequency to the center
        magnitude = np.abs(fft)  # Get the magnitude spectrum
        logging.debug(f"[DEBUG] FFT computed. Magnitude shape: {magnitude.shape}")

        # Apply logarithmic scaling
        logging.debug(f"[DEBUG] Applying logarithmic scaling to the magnitude spectrum...")
        magnitude = np.log1p(magnitude)

        # Normalize to 0-255
        logging.debug(f"[DEBUG] Normalizing magnitude to 0-255...")
        if np.max(magnitude) == 0:
            logging.warning(f"[WARNING] Maximum magnitude is 0. Skipping normalization.")
            return
        magnitude = (magnitude / np.max(magnitude) * 255).astype(np.uint8)

        # Invert the colors to make it white on black
        logging.debug(f"[DEBUG] Inverting colors to make the image white on black...")
        magnitude = 255 - magnitude

        # Apply radial fading
        logging.debug(f"[DEBUG] Applying radial fading...")
        center = (magnitude.shape[0] // 2, magnitude.shape[1] // 2)
        y, x = np.ogrid[:magnitude.shape[0], :magnitude.shape[1]]
        distance = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        max_distance = np.max(distance)
        fade = 1 - (distance / max_distance)
        magnitude = (magnitude * fade).astype(np.uint8)

        # Ensure the output directory exists
        logging.debug(f"[DEBUG] Ensuring output directory exists for: {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the FFT spectral image
        logging.debug(f"[DEBUG] Saving FFT image to: {output_path}")
        fft_img = Image.fromarray(magnitude, mode="L")  # Grayscale mode
        fft_img.save(output_path)
        logging.info(f"[INFO] FFT image saved successfully to: {output_path}")

    except Exception as e:
        logging.error(f"[ERROR] Failed to generate FFT for {input_path}: {e}", exc_info=True)

def handle_missing_fft_images(missing_tokens):
    import logging
    if missing_tokens:
        logging.warning(f"FFT images not found for tokens: {', '.join(missing_tokens)}")