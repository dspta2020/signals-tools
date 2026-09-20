import matplotlib.pyplot as plt

from lib.visualization.BasePlotter import BasePlotter
from lib.visualization.PlotRescaler import PlotRescaler


class TimeDomainPlotter(BasePlotter):

    def __init__(self, waveform):
        super().__init__(waveform)

    def plot(self, x_units: str = "msec", y_units: str = "real", **kwargs) -> None:

        # no switch cases in python
        # process x data
        x_switch = x_units.strip().lower()
        if x_switch == "samples":
            x_data = self.waveform.duration_samples
            x_label_string = "samples"
        else:
            time_factor, time_label = PlotRescaler.get_time_scaling(x_switch)
            x_data = self.waveform.duration_sec * time_factor
            x_label_string = f"{time_label}"

        # process y data
        y_switch = y_units.strip().lower()
        if y_switch == "real":
            y_data = self.waveform.real_part
            y_label_string = y_switch
        elif y_switch == "imag":
            y_data = self.waveform.imag_part
            y_label_string = y_switch
        elif y_switch in ["abs", "linear", "mags"]:
            y_data = self.waveform.linear_mags
            y_label_string = "linear mags"
        else:
            print(f"TimeDomainPlotter: Invalid y_units ({y_switch}), defaulting to `real`")
            y_data = self.waveform.real_part
            y_label_string = "real"

        # parse kwargs
        linewidth = kwargs.get("linewidth", 2)
        linestyle = kwargs.get("linestyle", "-")
        grid = kwargs.get("grid", False)
        color = kwargs.get("color", "k")
        title = kwargs.get("title", "Time Domain")

        # plotting
        plt.title(title)
        plt.plot(x_data, y_data, color=color, linewidth=linewidth, linestyle=linestyle)
        plt.grid(grid)
        plt.xlabel(f"Time ({x_label_string.title()})")
        plt.ylabel(f"Amplitude ({y_label_string.title()})")
        plt.xlim([x_data[0], x_data[-1]])
