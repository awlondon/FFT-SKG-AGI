import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import os


def generate_fft_from_audio(audio_path: str, fft_data_path: str, fft_image_path: str) -> None:
    """
    Compute the FFT spectrum of an audio file and save both the raw data and a
    plotted image.  Any errors during processing are printed and silently
    ignored.
    """
    try:
        print(f"[FFT] Processing FFT from audio: {audio_path}")
        rate, data = wav.read(audio_path)
        # If stereo, reduce to mono
        if len(data.shape) == 2:
            data = data.mean(axis=1)
        # Compute FFT
        fft_spectrum = np.fft.fft(data)
        freq = np.fft.fftfreq(len(fft_spectrum), d=1 / rate)
        magnitude = np.abs(fft_spectrum)
        # Save raw FFT data
        np.save(fft_data_path, magnitude)
        # Plot FFT spectrum
        plt.figure(figsize=(12, 4))
        plt.plot(freq[: len(freq) // 2], magnitude[: len(magnitude) // 2])
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