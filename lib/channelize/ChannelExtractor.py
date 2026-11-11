from lib.Waveform import Waveform

from numpy import ndarray


class ChannelExtractor:

    def __init__(self, sample_rate_hz: float, D: int, channel_center_hz: float) -> None:

        self.sample_rate_hz = sample_rate_hz
        self.D = int(D)

        # bandwidth of the output channel
        self.channel_bandwidth = sample_rate_hz / self.D

        # will need to make an LO to modulate the low pass filter in
        self.channel_center_hz = channel_center_hz

        # will be a single channel with this many samples out
        self.num_frames = None
        self.channel_out = None

    def extract_channel(self, data_in: ndarray | Waveform, filter_in: ndarray) -> None:
        """
        Efficiently extracts a single channel from some high rate data.

        `filter_in` assumed to be a prototype low pass filter, and `data_in` can be a
        numpy array or Waveform and the shape is assumed to be column vector.
        """
        from numpy import pad, empty, result_type, conj

        # support either waveform objects coming in or also just numpy arrays
        if isinstance(data_in, Waveform):
            x = data_in.samples
            N = data_in.num_samples_complex
        elif isinstance(data_in, ndarray):
            x = data_in
            N = data_in.shape[0]
        else:
            raise (TypeError, "@Channelizer::generate_channelsI() - Invalid input datatype.")

        # length of the filter will mostly always be smaller than the data so is more
        # efficient to modulate the filter than the data
        h = filter_in
        num_taps = len(h)

        # modulate the filter
        h = self._modulate_filter(num_taps, h)

        # pad x to change the filter
        # TODO: I'm not sure why but I need to have this "virtual channel spacing" sort of calculation here (fs / center) to
        # get the output to match the manually modulated filter... When I tried modifying this and the channelizer to use
        # `num_taps - self.D` which feels more intuitively accurate, I couldn't get them to match the manually modulated filters.
        x = pad(x, ((num_taps - int(self.sample_rate_hz // self.channel_center_hz), 0), (0, 0)), constant_values=0)

        # calculate the number of output frames
        self.num_frames = (len(x) - num_taps) // self.D + 1

        # allocate the output channel
        self.channel_out = empty((self.num_frames, 1), dtype=result_type(x, h))

        # now can start iterating over the samples
        for r in range(self.num_frames):

            # advance window D samples
            start = r * self.D
            frame = x[start : start + num_taps].T @ h

            # now apply phase correction to baseband
            phase_corr = self._generate_phase_corr(r)

            # now build the output channel
            self.channel_out[r] = frame * phase_corr

    def _modulate_filter(self, num_taps: int, filter: ndarray) -> ndarray:
        from numpy import exp, pi, arange

        # assumes the filter is [N x 1]
        return filter * exp(-1j * 2 * pi * self.channel_center_hz * arange(num_taps) / self.sample_rate_hz)[:, None]

    def _generate_phase_corr(self, frame_idx: int) -> ndarray:
        from numpy import exp, pi

        # should return a scalar
        return exp(-1j * 2 * pi * self.channel_center_hz * frame_idx / (self.sample_rate_hz / self.D))
