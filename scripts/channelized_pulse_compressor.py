"""
Quick script to show that the Channelizer can also be used as an efficient
pulse compressor if the anti-alias filter is convolved with a match filter.

In this case will just use a simple linear FM.
"""

import time
from pathlib import Path

from scipy.fft import fft, ifft
from scipy.signal import firwin, convolve
import numpy as np
import matplotlib.pyplot as plt


from lib.Waveform import Waveform
from lib.channelize.Channelizer import Channelizer


def _make_complex_noise(shape, mu: float = 0, sigma: float = 0.25) -> np.ndarray:
    # make some complex noise
    noise_i = np.random.normal(loc=mu, scale=sigma, size=shape)
    noise_q = np.random.normal(loc=mu, scale=sigma, size=shape)

    # make it iq and normalize it
    return (noise_i + 1j * noise_q) / np.sqrt(np.pi / 2)


def _linear_conv_same(data_in, filter_in):

    N = len(data_in)
    L = len(filter_in)

    nfft = N + L - 1

    filter_f = fft(filter_in, nfft, axis=0)
    data_f = fft(data_in, nfft, axis=0)

    conv = ifft(data_f * filter_f, nfft, axis=0)

    return conv[:N]


def main():

    # basic params
    fs = 100e3
    rx_duration = 1
    rx_duration_samples = int(np.round(fs * rx_duration))

    # sweep over some specific bandwidth centered on a channel center in this case for convenience
    f0 = 18e3 + 5e3
    f1 = 22e3 + 5e3
    f_center = (f0 + f1) / 2
    bandwidth = f1 - f0

    # lfm timing parameters
    t0 = 0.5  # delay the FM a bit
    lfm_length_samples = 2048  # just want the duration to be a specified amount
    t1 = lfm_length_samples / fs + t0
    t0_samples = int(np.round(t0 * fs))
    t1_samples = int(np.round(t1 * fs))
    duration_samples = t1_samples - t0_samples
    duration = duration_samples / fs

    # setup for calculating the LFM phase
    k = bandwidth / duration
    t = np.arange(duration_samples) / fs

    # convert fm phase into complex exponential
    sig = np.exp(1j * (0.5 * k * t**2 + t * f0) * 2 * np.pi)

    # simulate a receive signal with some complex noise
    rx_signal = _make_complex_noise((rx_duration_samples, 1))

    # add in the lfm to the rx signal
    rx_signal[t0_samples:t1_samples, 0] += sig

    # plot here
    if 1:
        fig, ax = plt.subplots()
        Waveform(rx_signal, fs, 0).visualizer.plot_spectrogram(256, 8192)

    # roughly 8192 taps to make a prototype low pass filter
    num_taps = duration_samples * 4
    h_prototype = firwin(num_taps, 1 / (bandwidth * 1.2))[:, None]

    # now make a cascaded filter that also does pulse compression
    h = convolve(h_prototype, np.conj(sig[::-1, None]), "same")
    # h = _linear_conv_same(rx_signal, h_prototype)

    # setup for the channelizer
    num_channels = np.round(fs / f_center)
    decimation = np.round(fs / (bandwidth * 1.2))

    # pulse compressor/channelizer
    chan = Channelizer(fs, num_channels, decimation)
    chan.print_setup()
    print()

    # now generate the channels
    tic = time.perf_counter()
    chan.generate_channels(rx_signal, h)
    toc = time.perf_counter()
    print(f"Generated channels in {toc - tic:.6f} seconds\n")

    # now plot make 3 subplots
    fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(2, 2, tight_layout=True)
    axes = [ax0, ax1, ax2, ax3]
    max_val = np.max(np.abs(chan.channels))
    for n in range(chan.M):
        axes[n].plot(np.abs(chan.channels[:, n]))
        axes[n].set_ylim([0, max_val])

    plt.show()


if __name__ == "__main__":
    print(f"\nRunning File: {Path(__file__).name}\n")
    start_time = time.perf_counter()

    main()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nElapsed time: {elapsed_time:.6f} seconds\n")
