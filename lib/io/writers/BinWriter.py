from typing import BinaryIO, List

from lib.Waveform import Waveform
from lib.io.writers.BaseWriter import BaseWriter


class BinWriter(BaseWriter):

    HEADER_PRECISION = "I"
    SAMPLE_PRECISION = "h"
    HEADER_LEN_DWORDS = 3

    def __init__(self, endianness: str = ">"):
        super().__init__(endianness)

    def write(self, p_file: BinaryIO, waveform_obj: Waveform) -> None:
        # file headers
        sample_rate_hz = int(waveform_obj.sample_rate_hz)
        center_frequency_hz = waveform_obj.center_frequency_hz
        num_samples_interleaved = waveform_obj.num_samples_interleaved

        header_data = [sample_rate_hz, center_frequency_hz, num_samples_interleaved]
        header_format_str = f"{self.endianness}{len(header_data)}{self.HEADER_PRECISION}"
        header_bytes = self._pack(header_data, header_format_str)

        # sample data - integer quantize returns an ndarray of type np.int16
        quantized_data = waveform_obj.integer_quantize()

        sample_format_str = f"{self.endianness}{num_samples_interleaved}{self.SAMPLE_PRECISION}"
        sample_bytes = self._pack(quantized_data, sample_format_str)

        p_file.write(header_bytes + sample_bytes)

    @staticmethod
    def _pack(data: List, format_spec: str) -> bytes:
        """Helper method for packing structured binary data."""
        from struct import pack

        return pack(format_spec, *data)
