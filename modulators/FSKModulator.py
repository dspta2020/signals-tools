import numpy as np
from numpy.typing import NDArray


class FSKModulator:

    def __init__(self, sample_rate_hz: float, bit_rate_hz: float, frequency_deviation_hz: float) -> None:
        self.sample_rate_hz = float(sample_rate_hz)
        self.bit_rate_hz = float(bit_rate_hz)
        self.frequency_deviation_hz = float(frequency_deviation_hz)

        # can calculate the necessary upsample factor here
        self.upsample_factor = int(self.sample_rate_hz // self.bit_rate_hz)
        self.phase_increment_per_sample = 2 * np.pi * self.frequency_deviation_hz / self.sample_rate_hz

    def modulate(self, data: bytes) -> NDArray[np.complex64]:
        """
        Continuous phase FSK modulation.
        """
        bytes_data = self._buffer_to_bytes(data)
        bits_data = self._bytes_to_bits(bytes_data)
        antipodal_data = self._bits_to_antipodal(bits_data)
        upsampled_data = self._upsample(antipodal_data, self.upsample_factor)
        phase_masked_data = self._phase_mask(upsampled_data, self.phase_increment_per_sample)
        phi = self._accumulate_phase(phase_masked_data)
        return self._exponentiate(phi)

    @staticmethod
    def _buffer_to_bytes(buffer_in: bytes) -> NDArray[np.uint8]:
        return np.frombuffer(buffer_in, np.uint8, len(buffer_in))

    @staticmethod
    def _bytes_to_bits(bytes_in: NDArray[np.uint8]) -> NDArray[np.int8]:
        return np.unpackbits(bytes_in).astype(np.int8, copy=False)

    @staticmethod
    def _bits_to_antipodal(bits_in: NDArray[np.int8]) -> NDArray[np.int8]:
        return bits_in * 2 - 1

    @staticmethod
    def _upsample(antipodal_in: NDArray[np.int8], upsample_factor: int) -> NDArray[np.float32]:
        # casts the data to float to prepare for phase modulation
        return np.repeat(antipodal_in, upsample_factor).astype(np.float32, copy=False)

    @staticmethod
    def _phase_mask(upsampled_in: NDArray[np.float32], phase_increment: float) -> NDArray[np.float32]:
        return upsampled_in * phase_increment

    @staticmethod
    def _accumulate_phase(phase_masked_data: NDArray[np.float32]):
        return np.cumsum(phase_masked_data)

    @staticmethod
    def _exponentiate(phi: NDArray[np.float32]) -> NDArray[np.complex64]:
        result = np.empty(phi.shape, dtype=np.complex64)
        np.cos(phi, out=result.real)
        np.sin(phi, out=result.imag)
        return result

    # seems to be slower than computing sin and cos
    # @staticmethod
    # def _exponentiate(phi: NDArray[np.float32]) -> NDArray[np.complex64]:
    #     return np.exp(1j * phi).astype(np.complex64)
