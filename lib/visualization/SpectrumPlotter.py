import matplotlib.pyplot as plt

from lib.visualization.BasePlotter import BasePlotter
from lib.visualization.PlotRescaler import PlotRescaler


class SpectrumPlotter(BasePlotter):

    def __init__(self, waveform):
        super().__init__(waveform)

    def plot(self, nfft: int, x_units: str = "hz", y_units: str = "dB", **kwargs):

        # import fft tools
        from scipy.fft import fft, fftshift, fftfreq
        from numpy import log10

        # sanitize nfft
        nfft = int(nfft)

        # handle scaling of the x-axis (frequency)
        freq_factor, freq_label = PlotRescaler.get_frequency_scaling(x_units)

        y_switch = y_units.strip().lower()
        if y_switch == "linear":
            y_data = abs(fftshift(fft(self.waveform.samples, nfft))) ** 2
        elif y_switch == "db":
            y_data = 20 * log10(abs(fftshift(fft(self.waveform.samples, nfft))))
        else:
            print(f"SpectrumPlotter: Invalid y_units ({y_switch}), defaulting to `dB`")
            y_data = 20 * log10(abs(fftshift(fft(self.waveform.samples, nfft))))

        # get the bin label vector now
        x_data = fftshift(fftfreq(nfft, self.waveform.sample_spacing_sec) * freq_factor)

        # parse kwargs
        linewidth = kwargs.get("linewidth", 2)
        linestyle = kwargs.get("linestyle", "-")
        grid = kwargs.get("grid", False)
        color = kwargs.get("color", "k")
        title = kwargs.get("title", "Spectrum")

        # plotting
        plt.title(title)
        plt.plot(x_data, y_data, color=color, linewidth=linewidth, linestyle=linestyle)
        plt.grid(grid)
        plt.xlabel(f"Time ({freq_label.title()})")
        plt.ylabel(f"Amplitude ({y_switch.title()})")
        plt.xlim([x_data[0], x_data[-1]])
