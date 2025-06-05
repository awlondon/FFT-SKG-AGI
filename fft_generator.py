try:
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.io.wavfile as wav
except Exception:
    np = None
    plt = None
    wav = None
import os

def generate_fft_from_audio(audio_path, fft_data_path, fft_image_path):
    if not (np and plt and wav):
        print("[FFT] Required libraries not available. Skipping FFT generation.")
        return
    try:
        print(f"[FFT] Processing FFT from audio: {audio_path}")

        # Read audio file
        rate, data = wav.read(audio_path)

        # If stereo, reduce to mono
        if len(data.shape) == 2:
            data = data.mean(axis=1)

        # Compute FFT
        fft_spectrum = np.fft.fft(data)
        freq = np.fft.fftfreq(len(fft_spectrum), d=1/rate)
        magnitude = np.abs(fft_spectrum)

        # Save raw FFT data
        np.save(fft_data_path, magnitude)

        # Plot FFT spectrum
        plt.figure(figsize=(12, 4))
        plt.plot(freq[:len(freq)//2], magnitude[:len(magnitude)//2])
        plt.title("FFT Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(fft_image_path)
        plt.close()

        print(f"[FFT] FFT image saved to: {fft_image_path}")

    except Exception as e:
        print(f"[FFT] Error processing FFT from {audio_path}: {e}")
