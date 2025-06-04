# generate_fft_from_image.py

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def generate_fft_from_image(image_path, output_dir="modalities/fft_visual"):
    print(f"[FFT] Generating FFT from image: {image_path}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    try:
        # Load and convert image to grayscale
        img = Image.open(image_path).convert("L")
        img_array = np.array(img)

        # Perform FFT
        fft_result = np.fft.fft2(img_array)
        fft_shifted = np.fft.fftshift(fft_result)
        magnitude_spectrum = 20 * np.log(np.abs(fft_shifted) + 1e-8)

        # Generate filename
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        fft_filename = f"{base_name}_fft_spark.png"
        fft_output_path = os.path.join(output_dir, fft_filename)

        # Save FFT visualization
        plt.figure(figsize=(4, 4), dpi=100)
        plt.imshow(magnitude_spectrum, cmap='gray')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(fft_output_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        print(f"[FFT] FFT image saved to: {fft_output_path}")
        return fft_output_path

    except Exception as e:
        print(f"[FFT] Error generating FFT from image: {e}")
        return None
