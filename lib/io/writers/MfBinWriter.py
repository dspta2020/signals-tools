from typing import BinaryIO, List

from lib.Waveform import Waveform
from lib.io.writers.BaseWriter import BaseWriter


class MfBinWriter(BaseWriter):

    HEADER_PRECISION = "I"
    SAMPLE_PRECISION = "i"
    HEADER_LEN_DWORDS = 3

    def __init__(self, endianness: str = ">"):
        super().__init__(endianness)

    def write(self, p_file: BinaryIO, waveform_obj: Waveform) -> None:
        # file headers
        sample_rate_hz = int(waveform_obj.sample_rate_hz)
        center_frequency_hz = int(waveform_obj.center_frequency_hz)
        num_samples_interleaved = int(waveform_obj.num_samples_interleaved)

        header_data = [sample_rate_hz, center_frequency_hz, num_samples_interleaved]
        header_format_str = f"{self.endianness}{len(header_data)}{self.HEADER_PRECISION}"
        header_bytes = self._pack(header_data, header_format_str)

        sample_format_str = f"{self.endianness}{num_samples_interleaved}{self.SAMPLE_PRECISION}"
        sample_bytes = self._pack(waveform_obj.iq_interleaved.astype(int), sample_format_str)

        p_file.write(header_bytes + sample_bytes)

    @staticmethod
    def _pack(data: List, format_spec: str) -> bytes:
        """Helper method for packing structured binary data."""
        from struct import pack

        return pack(format_spec, *data)
