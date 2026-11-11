from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage._filters import _gaussian_kernel1d
from scipy.signal import convolve

from modulators.FSKModulator import FSKModulator


class GFSKModulator(FSKModulator):

    def __init__(self, sample_rate_hz: float, bit_rate_hz: float, frequency_deviation_hz: float, filter_symbols: int) -> None:
        super().__init__(sample_rate_hz, bit_rate_hz, frequency_deviation_hz)

        # basically the number of symbols that gets smeared
        self.filter_symbols = filter_symbols

    def modulate(self, data: bytes) -> NDArray[np.float32]:
        bytes_data = self._buffer_to_bytes(data)
        bits_data = self._bytes_to_bits(bytes_data)
        antipodal_data = self._bits_to_antipodal(bits_data)
        upsampled_data = self._upsample(antipodal_data, self.upsample_factor)

        # guassian filter here?
        h = _gaussian_kernel1d(sigma=512 * 0.25, order=0, radius=self.filter_symbols * self.upsample_factor).astype(np.float32, copy=False)
        filtered_data = convolve(upsampled_data, h, "same")

        phase_masked_data = self._phase_mask(filtered_data, self.phase_increment_per_sample)
        phi = self._accumulate_phase(phase_masked_data)

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(phi)

        fig, ax = plt.subplots()
        plt.plot(h)
        plt.show()

        return phi
