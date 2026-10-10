from lib.generators.LFM import LinearFM


class WaveformGenerator:

    @staticmethod
    def make_LFM_from_endpoints(sample_rate_hz: float, time_start: float, time_stop: float, freq_start: float, freq_stop: float):
        gen = LinearFM(sample_rate_hz)
        return gen.make_from_endpoints(time_start, time_stop, freq_start, freq_stop)

    @staticmethod
    def make_LFM_from_freq_and_slope(sample_rate_hz: float, freq_start: float, freq_stop: float, slope: float):
        gen = LinearFM(sample_rate_hz)
        return gen.from_freq_points_and_slope(freq_start, freq_stop, slope)

    @staticmethod
    def make_complex_noise(shape, mu: float, sigma: float, normalization: float = 1):
        from numpy.random import Generator, MT19937

        gen = Generator(MT19937())

        noise_i = gen.standard_normal(shape)
        noise_q = gen.standard_normal(shape)

        return ((noise_i + 1j * noise_q) * sigma + mu) / normalization
