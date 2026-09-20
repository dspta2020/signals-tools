import matplotlib.pyplot as plt
import numpy as np

from lib.visualization.BasePlotter import BasePlotter
from lib.visualization.PlotRescaler import PlotRescaler


class SpectrogramPlotter(BasePlotter):

    def __init__(self, waveform):
        super().__init__(waveform)

    def plot(self, window_len: int, nfft: int, x_units: str = "sec", y_units: str = "hz", **kwargs):

        # handle scipy import here
        from scipy.signal import ShortTimeFFT
        from scipy.signal.windows import blackmanharris

        # parameter setup
        win = blackmanharris(window_len)
        overlap = kwargs.get("overlap", 0.5)
        hop = int(window_len * (1 - overlap))
        fft_mode = "centered"
        fs = self.waveform.sample_rate_hz

        # construct STFT object
        STFT = ShortTimeFFT(win=win, hop=hop, fs=fs, fft_mode=fft_mode, mfft=nfft)

        # perform the actual STFT
        stft_array = STFT.stft(self.waveform.samples)
        [t0, t1, f0, f1] = STFT.extent(self.waveform.num_samples_complex)

        # plotting kwargs
        title = kwargs.get("title", "Spectrogram")
        cmap = kwargs.get("cmap", "viridis")
        add_color_bar = kwargs.get("colorbar", False)

        # process the units
        time_factor, time_label = PlotRescaler.get_time_scaling(x_units)
        freq_factor, freq_label = PlotRescaler.get_frequency_scaling(y_units)

        # since using the stft object to get the extent the time data needs to be rescaled by the
        # initial time offset as well as the time factor
        extent = []
        extent.append((t0 + self.waveform.initial_time_offset_sec) * time_factor)
        extent.append((t1 + self.waveform.initial_time_offset_sec) * time_factor)
        extent.append(f0 * freq_factor)
        extent.append(f1 * freq_factor)

        # calculate power in dB
        stft_power = 20 * np.log10(np.abs(stft_array))

        im = plt.imshow(
            stft_power,
            origin="lower",
            aspect="auto",
            cmap=cmap,
            extent=extent,
            vmin=kwargs.get("zmin", None),
            vmax=kwargs.get("zmax", None),
        )

        if add_color_bar:
            cbar = plt.colorbar(im, ax=plt.gca())  # attaches to current axes obj
            cbar.set_label("Power (dB)")

        plt.xlabel(f"Time ({time_label})")
        plt.ylabel(f"Frequency ({freq_label})")
        plt.title(title)
