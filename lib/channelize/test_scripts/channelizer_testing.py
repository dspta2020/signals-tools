from lib.Waveform import Waveform
from lib.channelize.Channelizer import Channelizer

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin
from scipy.fft import fft, fftshift, fftfreq

if __name__ == "__main__":
    from time import perf_counter
    from pathlib import Path

    print(f"\nRunning File: {Path(__file__).name}\n")
    start_time = perf_counter()

    fs = 100e3  # decent sized so get narrow lobes
    total_duration = 0.3
    num_tones = 2
    M = 5
    tone_duration = total_duration / num_tones

    total_bandwidth = fs * 0.8
    tone_channel_centers = np.linspace(-total_bandwidth / 2, total_bandwidth / 2, num_tones)
    tone_channel_centers = np.array([1000, 750]) * 1e3

    total_duration_samples = np.floor(total_duration * fs).astype(int)
    tone_duration_samples = np.floor(tone_duration * fs).astype(int)

    nth_tone_delay = np.linspace(0, total_duration, num_tones, endpoint=False)
    nth_tone_delay_samples = nth_tone_delay * fs

    noise_i = np.random.normal(scale=0.25, size=int(total_duration_samples))
    noise_q = np.random.normal(scale=0.25, size=int(total_duration_samples))
    noisy_iq = (noise_i + 1j * noise_q) / np.sqrt(np.pi / 2)

    tone_t = np.arange(tone_duration_samples) / fs
    for n, d in enumerate(nth_tone_delay.astype(float)):
        f = tone_channel_centers[n]
        t = np.exp(1j * 2 * np.pi * f * (tone_t + d))

        tone_slice = slice(int(nth_tone_delay_samples[n]), int(nth_tone_delay_samples[n] + np.size(t, 0)))
        noisy_iq[tone_slice] += t

        print(f)

    wf = Waveform(noisy_iq, fs, 0)

    if 0:
        plt.figure(1)
        wf.visualizer.plot_spectrogram(2048, 8192)
        plt.show()

    chan = Channelizer(wf.sample_rate_hz)

    print("\n\n")
    channel_critical_bandwidth = fs / M
    print(channel_critical_bandwidth)

    cutoff = channel_critical_bandwidth / 2
    num_taps = 256
    h = firwin(num_taps, cutoff, fs=fs)

    if 0:
        fig, [ax0, ax1] = plt.subplots(2, 1)
        # upper subplot
        ax0.plot(h)
        # lower subplot
        nfft = 8192
        H = fftshift(fft(h, nfft))
        bins = fftshift(fftfreq(nfft, 1 / fs))
        ax1.plot(bins, 20 * np.log10(abs(H)))
        ax1.axvline(cutoff * 1e-3, c="r", linewidth=2)
        ax1.axvline(-cutoff * 1e-3, c="r", linewidth=2)

    # time the channelization
    t0 = perf_counter()
    chan.critical_channelize(wf, h, M)
    t1 = perf_counter()
    print(f"Channelization took ~{t1-t0:0.6f} Seconds")

    D = wf.sample_rate_hz / M

    channel_ind = 1
    test_wf = Waveform(chan.channels[:, channel_ind], D, chan.channel_centers[channel_ind])
    if 0:
        plt.figure(2)
        test_wf.visualizer.plot_spectrogram(512, 8192, x_units="msec", y_units="khz", add_center=True)
        plt.show()

    end_time = perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nElapsed time: {elapsed_time:.6f} seconds\n")
