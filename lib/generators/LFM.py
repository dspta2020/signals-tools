class LinearFM:

    def __init__(self, sample_rate_hz: float) -> None:
        self.sample_rate_hz = sample_rate_hz
        return

    def from_endpoints(self, time_start: float, time_stop: float, freq_start: float, freq_stop: float):
        from numpy import exp, arange, pi

        # get the bandwidth over time
        bandwidth = freq_stop - freq_start
        duration = time_stop - time_start

        # LFM slope
        slope = bandwidth / duration

        # time vector - makes only the LFM so time shifting will have
        # to happen after synthesis here
        time = arange(0, duration, 1 / self.sample_rate_hz)

        # f(t) = kt + f0
        phi = (0.5 * slope * time**2 + freq_start * time) * 2 * pi

        return exp(1j * phi)

    def from_freq_points_and_slope(self, freq_start: float, freq_stop: float, slope: float):
        from numpy import exp, arange, pi

        # get bandwidth and calculate duration
        bandwidth = freq_stop - freq_start
        duration = bandwidth / slope  # slope is f / t and bandwidth is f

        # time vector - makes only the LFM so time shifting will have
        # to happen after synthesis here
        time = arange(0, duration, 1 / self.sample_rate_hz)

        # f(t) = kt + f0
        phi = (0.5 * slope * time**2 + freq_start * time) * 2 * pi

        return exp(1j * phi)
