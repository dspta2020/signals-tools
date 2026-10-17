"""
Script I used to fix up the Channelizer. If in the scripts folder move it into the
current working dir, one level up from lib.
"""

from time import perf_counter
from pathlib import Path

from lib.channelize.Channelizer import Channelizer
from lib.Waveform import Waveform

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin, convolve


def _make_complex_noise(shape: tuple[int, int], mu: float = 0, sigma: float = 0.25) -> np.ndarray:
    # make some complex noise
    noise_i = np.random.normal(loc=mu, scale=sigma, size=shape)
    noise_q = np.random.normal(loc=mu, scale=sigma, size=shape)

    # make it iq and normalize it
    return (noise_i + 1j * noise_q) / np.sqrt(np.pi / 2)


def _make_tone(sample_rate, duration, freq):
    # makes a tone based on above
    tone_duration_samples = sample_rate * duration
    t = np.arange(tone_duration_samples) / sample_rate

    return np.exp(1j * 2 * np.pi * freq * t)[:, None]


def main():

    # setup here
    fs = 120e3  # hz
    rx_duration_sec = 1
    rx_duration_samples = int(np.round(rx_duration_sec * fs))

    # simulate a receive signal with some complex noise
    rx_signal = _make_complex_noise((rx_duration_samples, 1))

    # setup the channelizer with some ratio that evaluates to a rational non-integer
    num_channels = 4
    decimation_factor = 3

    # init the channelizer
    chan = Channelizer(fs, num_channels, decimation_factor)
    chan.print_setup()
    print()
    chan.print_channel_list()
    print()

    # make some tones and add them to the rx signal
    tone_offset_hz = np.array([5, 15, 25]) * 1e3
    num_tones = len(tone_offset_hz)

    # window the tone so that its clear what tone is which even if the frequency axis gets
    # rotated somewhere along the way
    tone_duration_sec = rx_duration_sec / num_tones
    tone_delay_sec = np.arange(num_tones) * tone_duration_sec

    # add the tones to the simulated rx data
    for n, _ in enumerate(tone_offset_hz):
        # get the nth offset and delay
        f = tone_offset_hz[n]
        d = tone_delay_sec[n]

        # tone sample gates
        start = int(np.round(d * fs))
        end = int(np.round(start + tone_duration_sec * fs))

        # make the tone and add it to the signal
        rx_signal[start:end] += _make_tone(fs, tone_duration_sec, f)

    # plotting
    if 0:
        fig, ax = plt.subplots()
        plt.sca(ax)
        Waveform(rx_signal, fs, 0).visualizer.plot_spectrogram(128, 8192, "msec", "khz")
        ax.set_title("'rx_signal'")

        fig, ax = plt.subplots()
        Waveform(rx_signal, fs, 0).visualizer.plot_spectrogram(128, 8192, "msec", "khz")

        # is specific to this example only plot the channels where the tones are and overlap
        color_code = ["k", "r"]
        for n, c in enumerate(chan.channel_centers_hz[:-2]):
            upper_edge = (c + chan.channel_bandwidth_hz / 2) * 1e-3
            center = (c) * 1e-3
            lower_edge = (c - chan.channel_bandwidth_hz / 2) * 1e-3
            ax.axhline(upper_edge, color=color_code[n], linestyle="--")
            ax.axhline(lower_edge, color=color_code[n], linestyle="--")
            ax.axhline(center, color=color_code[n], linestyle="-")

        ax.set_title("'rx_signal' -- channels overlaid")
        plt.show()

    # next gotta make a fir filter
    num_taps = 64
    cutoff = (fs / 2) / chan.D
    h = firwin(num_taps, cutoff, fs=fs)[:, None]

    # now generate the channels
    tic = perf_counter()
    chan.generate_channels(rx_signal, h)
    toc = perf_counter()
    print(f"Generated channels in {toc - tic:.6f} seconds\n")

    # more plot
    if 0:
        # plot channel 1 here
        fig, ax = plt.subplots()
        channel_ind = 0
        Waveform(chan.channels[:, channel_ind], chan.channel_bandwidth_hz, chan.channel_centers_hz[channel_ind]).visualizer.plot_spectrogram(
            128,
            8192,
            "msec",
            "khz",
            add_center=True,
        )
        ax.axhline(tone_offset_hz[channel_ind] * 1e-3, color="r")
        ax.axhline(tone_offset_hz[channel_ind + 1] * 1e-3, color="r")
        ax.set_title(f"Channel {channel_ind}")

        # plot channel 2 here
        fig, ax = plt.subplots()
        channel_ind = 1
        Waveform(chan.channels[:, channel_ind], chan.channel_bandwidth_hz, chan.channel_centers_hz[channel_ind]).visualizer.plot_spectrogram(
            128,
            8192,
            "msec",
            "khz",
            add_center=True,
        )
        ax.axhline(tone_offset_hz[channel_ind] * 1e-3, color="r")
        ax.axhline(tone_offset_hz[channel_ind + 1] * 1e-3, color="r")
        ax.set_title(f"Channel {channel_ind}")
        plt.show()

    # now compare to the brute force way to channelize.. modulate the data down to
    # baseband and then low pass filter
    wf = Waveform(rx_signal, fs, 0)

    # lets say we test channel 2 so the 30 kHz center
    channel_ind = 1
    wf = wf.mix_data(-chan.channel_centers_hz[channel_ind])

    # now low pass filter the data
    filtered_x = convolve(wf.samples[:, None], h)  # full conv

    # need to pull out the samples that correspond to the correct frame
    first_sample_out = chan.M - 1
    last_sample_out = first_sample_out + chan.num_frames * chan.D
    modulated_out = filtered_x[first_sample_out : last_sample_out : chan.D]

    print(f"Channel {channel_ind:d} - IQ Comparison")
    for i in range(5):
        chan_i = np.real(chan.channels[i, channel_ind])
        chan_q = np.imag(chan.channels[i, channel_ind])
        mod_i = np.real(modulated_out[i, 0])
        mod_q = np.imag(modulated_out[i, 0])
        print(f"    Sample {i:d}: Channelizer = {chan_i: 3.6f} + ({chan_q: 3.6f})i, Modulation = {mod_i: 3.6f} + ({mod_q: 3.6f})i")


if __name__ == "__main__":
    from pathlib import Path

    print(f"\nRunning File: {Path(__file__).name}\n")
    start_time = perf_counter()

    try:
        main()
    except KeyboardInterrupt:
        pass

    end_time = perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nElapsed time: {elapsed_time:.6f} seconds\n")
