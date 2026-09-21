import numpy as np


class Waveform:

    def __init__(self, samples: np.ndarray, sample_rate_hz: float, center_frequency_hz: float, **kwargs):
        # construct instance of a signal, waveform, etc.
        self.samples = samples
        self.sample_rate_hz = sample_rate_hz
        self.center_frequency_hz = center_frequency_hz

        self.initial_time_offset_sec = kwargs.pop("initial_time_offset_sec", 0)

        # coerce the input data to be a 1D row vector if possible
        self._normalize_dimensions()

        # some derived constants
        self.num_samples_complex = self.samples.shape[0]  # already coerced to 1D
        self.num_samples_interleaved = self.num_samples_complex * 2
        self.total_duration_sec = self.num_samples_complex / self.sample_rate_hz
        self.sample_spacing_sec = 1 / self.sample_rate_hz

    @property
    def duration_samples(self):
        return np.arange(self.num_samples_complex)

    @property
    def duration_sec(self):
        return (self.duration_samples / self.sample_rate_hz) + self.initial_time_offset_sec

    @property
    def real_part(self):
        return np.real(self.samples)

    @property
    def imag_part(self):
        return np.imag(self.samples)

    @property
    def iq_interleaved(self):
        # leave the interleaved as float and only cast to ints if quantizing
        iq_interleaved = np.empty((self.num_samples_interleaved, 1))
        iq_interleaved[::2] = self.real_part[:, np.newaxis]
        iq_interleaved[1::2] = self.imag_part[:, np.newaxis]
        return iq_interleaved.reshape(-1)

    @property
    def linear_mags(self):
        return np.abs(self.samples)

    @property
    def visualizer(self):
        from lib.WaveformVisualizer import WaveformVisualizer

        return WaveformVisualizer(self)

    def _normalize_dimensions(self):
        samples = self.samples

        # Ensure we handle arrays properly
        if not isinstance(samples, np.ndarray):
            samples = np.asarray(samples)

        # Logic to normalize the shape
        if samples.ndim == 2 and samples.shape[1] == 1:
            # Reshape column vector (N, 1) -> row vector (N,)
            self.samples = samples.reshape(-1)
        elif samples.ndim != 2 and samples.ndim != 1:
            # Covers 0D scalars or other invalid cases
            raise ValueError(f"Invalid shape for normalization requires (N x 1) or (N, ). Got {samples.shape}")
        else:
            # If ndim == 1, no action needed; array stays as-is
            return self.samples

    def print_waveform_info(self):
        from lib.utils.Utilities import Utilities

        sr_converted = Utilities.auto_scale_frequency(self.sample_rate_hz)
        ss_converted = Utilities.auto_scale_time(self.sample_spacing_sec)
        dur_converted = Utilities.auto_scale_time(self.total_duration_sec)
        start_converted = Utilities.auto_scale_time(self.duration_sec[0])
        end_converted = Utilities.auto_scale_time(self.duration_sec[-1])
        cf_converted = Utilities.auto_scale_frequency(self.center_frequency_hz)

        print(f"{'-'*30}BEGIN PRINTING WAVEFORM INFO{'-'*30}")
        print(f"Sample Rate: {sr_converted.value:.3f} {sr_converted.unit}")
        print(f"Sample Spacing: {ss_converted.value:.3f} {ss_converted.unit}")
        print(f"Sample Duration: {dur_converted.value:.3f} {dur_converted.unit}")
        print(f"Signal Start: {start_converted.value:.3f} {start_converted.unit}")
        print(f"Signal End: {end_converted.value:.3f} {end_converted.unit}")
        print(f"Number Samples Complex: {self.num_samples_complex} samples")
        print(f"Number Samples Interleaved: {self.num_samples_interleaved} samples")
        print(f"Center Frequency Absolute: {cf_converted.value:.3f} {cf_converted.unit}")
        print(f"{'-'*30}END PRINTING WAVEFORM INFO{'-'*30}")

    def mix_data(self, lo_freq_hz):

        # call reshape to make vector N x 1
        digital_lo = np.exp(1j * 2 * np.pi * lo_freq_hz * self.duration_sec)[:, np.newaxis]

        # also N x 1
        mixed_iq = self.samples * digital_lo

        return Waveform(mixed_iq, self.sample_rate_hz, self.center_frequency_hz, initial_time_offset_sec=self.initial_time_offset_sec)

    def integer_quantize(self, num_bits: int = 16):

        # first normalize the interleaved IQ to unity
        normalized_samples = self.iq_interleaved / np.max(np.abs(self.iq_interleaved))

        # simple twos-complement quantization more or less
        return np.round(normalized_samples * (2 ** (num_bits - 1) - 1)).astype(np.int32)

    def resample_poly(self, desired_rate_hz: float, **kwargs):
        # import modules specifically for this
        from fractions import Fraction
        from scipy.signal import resample_poly

        denominator_limit = kwargs.get("denominator_limit", 10e3)
        recalculate_rate = kwargs.get("recalculate_rate", False)

        # calculate a rational approximation of the up and down factors
        up, down = Fraction(desired_rate_hz / self.sample_rate_hz).limit_denominator(denominator_limit).as_integer_ratio()

        # call resample poly
        iq_resampled = resample_poly(self.samples, up, down)

        if not recalculate_rate:
            return Waveform(iq_resampled, desired_rate_hz, self.center_frequency_hz, initial_time_offset_sec=self.initial_time_offset_sec)
        else:
            new_rate = self.sample_rate_hz * (up / down)
            return Waveform(iq_resampled, new_rate, self.center_frequency_hz, initial_time_offset_sec=self.initial_time_offset_sec)
