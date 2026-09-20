from lib.Waveform import Waveform
from lib.visualization.TimeDomainPlotter import TimeDomainPlotter
from lib.visualization.SpectrogramPlotter import SpectrogramPlotter


class WaveformVisualizer:

    def __init__(self, waveform: Waveform):
        # construct with instance of the waveform
        self.waveform = waveform

        # make the mutable waveform plot
        self.time_domain_plotter = TimeDomainPlotter(self.waveform)
        self.spectrogram_plotter = SpectrogramPlotter(self.waveform)

    def plot_time_domain(self, x_units: str = "sec", y_units: str = "real", **kwargs):
        """
        Plots the time domain representation of a waveform/signal.
        """
        self.time_domain_plotter.plot(x_units, y_units, **kwargs)

    def plot_spectrogram(self, window_len, nfft, x_units: str = "sec", y_units: str = "real", **kwargs):
        """
        Plots the time/frequency (spectrogram) representation of a waveform/signal.
        """
        self.spectrogram_plotter.plot(window_len, nfft, x_units, y_units, **kwargs)
