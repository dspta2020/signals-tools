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

    def channelize(self, waveform_in: Waveform, M: int, D: int, h: ndarray):
        """
        General psudo-WOLA polyphase channelizer architecture.

        Initial pass where input waveform is split into M evenly spaced channels,
        each decimated by a factor of D.
        """
        from numpy import asarray, pad, empty, result_type, exp
        from scipy.fft import fftfreq, fft
        from scipy.constants import pi

        # length of the filter
        P = len(h)

        # x is the input vector here
        x = asarray(waveform_in.samples)

        # can pad the input here to fully charge the filter, for example if M = 4
        # and h is 256 taps the first window w_0 = [0, 0, ... 1, 2, 3, 4] where
        # len(w_0) is 256 next window will be advance 4 samples [0, ... 1, 2, 3, 4, 5, 6, 7, 8]
        x = pad(x, (P - M, 0), constant_values=0)

        if P % M != 0:
            raise ValueError("Prototype length must be divisible by M")

        # the number of frames that come out, is the input samples decimated..
        # floor division ensures number of full frames
        num_frames = (len(x) - P) // D + 1

        # store the channel output
        channel_centers = fftfreq(M, d=1 / self.sample_rate_hz)
        channel_output = empty((num_frames, M), dtype=result_type(x, h))

        # iterate over each frame which advances D samples i.e. we produce one output
        # sample in every subband for each D sample advance
        for r in range(num_frames):
            start = r * D
            # for now just using the prototype filter as the window function
            frame = x[start : start + P] * h

            # reshape into polyphase components and sum to apply convolution
            folded_frame = frame.reshape(P // M, M).sum(0)

            # channelize
            channel_output[r, :] = fft(folded_frame, axis=0) * exp(-1j * 2 * pi * channel_centers.reshape(1, -1) * r / (self.sample_rate_hz / D))

        self.channels = channel_output
        self.channel_centers = channel_centers

    @staticmethod
    def _make_prototype_fir_filter(sample_rate, decimation_factor, num_taps):
        from scipy.signal import firwin

        cutoff = (sample_rate / 2) / decimation_factor
        return firwin(num_taps, cutoff, fs=sample_rate)
