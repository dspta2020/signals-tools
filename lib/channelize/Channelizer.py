from lib.Waveform import Waveform

from numpy import ndarray


class Channelizer:

    def __init__(self, sample_rate_hz: float) -> None:
        self.sample_rate_hz = sample_rate_hz

        # for holding onto state
        self.channels = None
        self.channel_centers = None

    def critical_channelize(self, waveform_in: Waveform, filter_in: ndarray, num_output_channels: int) -> None:
        """
        Minimal implementation of a polyphase channelizer.

        Follows the commutator model by decomposing both the signal and filter into branches.
        """
        from scipy.signal import convolve
        from scipy.fft import fft
        from numpy import arange, size, empty_like

        # keeping namespace consistent with the derivation
        M = num_output_channels

        # decompose the signal
        X = self._polyphase_decompose(waveform_in.samples, waveform_in.num_samples_complex, M)
        # decompose the filter
        H = self._polyphase_decompose(filter_in, size(filter_in, 0), M)

        # array to store the output samples should be same size as decomposed signal
        channels_out = empty_like(X)

        # first are the undelayed 0th branches of the signal and the filter
        channels_out[:, 0] = convolve(X[:, 0], H[:, 0], mode="same")

        # then filter each compatible
        for n in arange(1, M):
            filtered_branch = convolve(X[:, n], H[:, M - n], mode="same")
            channels_out[:, n] = self._delay_signal(filtered_branch, 1)

        # final step is FFT/IFFT
        channels_out = fft(channels_out, axis=1)

        # calculate the channel centers
        channel_centers = ((arange(M) * self.sample_rate_hz / M) + self.sample_rate_hz / 2) % self.sample_rate_hz - (self.sample_rate_hz / 2)

        # assign to properties to maintain persistent state for now
        self.channels = channels_out
        self.channel_centers = channel_centers

        return None

    @staticmethod
    def _polyphase_decompose(samples_in: ndarray, num_samples_in: int, num_channels_out: int) -> ndarray:
        """
        Decomposes data stream of [L x 1] or [L x 0] into `N` phases.

        Output array will be [N x L/N].
        """
        from numpy import pad, reshape

        # assignments to keep the code clean
        L = num_samples_in
        N = num_channels_out

        # needs be square when reshaped
        pad_size = N - (L % N)
        if pad_size != 0:
            samples_in = pad(samples_in, [0, pad_size], "constant", constant_values=0)

        # use Fortran style reshaping hence the rows will be the phases and the columns will be
        # the sample in each phase
        return reshape(samples_in, (-1, N), order="C")

    @staticmethod
    def _delay_signal(samples_in: ndarray, delay: int):
        """
        Delays a sample vector, truncating its output.
        """
        from numpy import roll

        samples_out = roll(samples_in, delay, axis=0)
        samples_out[:delay] = 0

        return samples_out
