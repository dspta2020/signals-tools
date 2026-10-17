from lib.Waveform import Waveform

from numpy import ndarray


class Channelizer:

    def __init__(self, sample_rate_hz: float, M: int, D: int) -> None:
        from scipy.fft import fftfreq, fftshift

        self.sample_rate_hz = sample_rate_hz  # input sample rate
        self.M = int(M)  # Number of channels
        self.D = int(D)  # Decimation factor

        # channel centers are evenly spaced based on the sample rate and the desired number of output channels
        self.channel_spacing_hz = self.sample_rate_hz / self.M
        self.channel_centers_hz = fftshift(fftfreq(self.M, 1 / self.sample_rate_hz))

        # simple channel bandwidth calculation here because its simply based on the sample rate
        self.channel_bandwidth_hz = sample_rate_hz / self.D

        # for holding onto state
        self.channels = None
        self.channel_centers = None

    def generate_channels(self, data_in: ndarray | Waveform, filter_in: ndarray) -> None:
        """
        General pseudo-WOLA polyphase channelizer architecture.

        Initial pass where input waveform is split into M evenly spaced channels,
        each decimated by a factor of D.
        """
        from numpy import pad, empty, result_type, exp
        from scipy.fft import fft
        from scipy.constants import pi

        # support either waveform objects coming in or also just numpy arrays
        if isinstance(data_in, Waveform):
            x = data_in.samples
        elif isinstance(data_in, ndarray):
            x = data_in
        else:
            raise (TypeError, "@Channelizer::generate_channelsI() - Invalid input datatype.")

        # length of the filter
        h = filter_in
        num_taps = len(h)
        if num_taps % self.M != 0:
            raise ValueError(f"@Channelizer::generate_channelsI() - Invalid filter length ({num_taps}), must be divisible by M ({self.M}).")

        # can pad the input here to fully charge the filter, for example if M = 4
        # and h is 256 taps the first window w_0 = [0, 0, ... 1, 2, 3, 4] where
        # len(w_0) is 256 next window will be advance 4 samples [0, ... 1, 2, 3, 4, 5, 6, 7, 8]
        x = pad(x, (num_taps - self.M, 0), constant_values=0)

        # the number of frames that come out, is the input samples decimated..
        # floor division ensures number of full frames
        num_frames = (len(x) - num_taps) // self.D + 1

        # buffer to store the output channels
        self.channels = empty((num_frames, self.M), dtype=result_type(x, h))

        # iterate over each frame which advances D samples i.e. we produce one output
        # sample in every subband for each D sample advance
        for r in range(num_frames):

            # extract the current frame
            start = r * self.D

            # for now just using the prototype filter as the window function
            frame = x[start : start + num_taps] * h

            # reshape into polyphase components and sum to apply convolution
            folded_frame = frame.reshape(num_taps // self.M, self.M).sum(0)

            # phase correction needs to be applied to baseband the channel output
            phase_corr = exp(-1j * 2 * pi * self.channels.reshape(1, -1) * r / (self.sample_rate_hz / self.D))

            # channelize
            self.channels[r, :] = fft(folded_frame, axis=0) * phase_corr

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
    def _delay_signal(samples_in: ndarray, delay: int) -> ndarray:
        """
        Delays a sample vector, truncating its output.
        """
        from numpy import roll

        samples_out = roll(samples_in, delay, axis=0)
        samples_out[:delay] = 0

        return samples_out
