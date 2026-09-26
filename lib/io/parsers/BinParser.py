from typing import BinaryIO, Tuple
from os import SEEK_END, SEEK_SET
import struct

import numpy as np

from lib.Waveform import Waveform
from lib.io.parsers.BaseParser import BaseParser


class BinParser(BaseParser):
    HEADER_LEN_DWORDS = 3
    HEADER_PRECISION_BYTES = 4
    SAMPLE_PRECISION_BYTES = 2

    def __init__(self, endianness: str = ">"):
        super().__init__(endianness)
        # canonical numpy element type for 16-bit signed ints
        self._numpy_sample_type = "i2"
        self.header_precision = "I"

    def parse(self, p_file: BinaryIO) -> Waveform:
        """Parse binary IQ file into a Waveform.

        File layout:
        - Header: 3 x uint32 (sample_rate_hz, center_frequency_hz, num_samples_interleaved)
        - Payload: num_samples_interleaved x int16 (interleaved I,Q,I,Q,...)
        """
        # read file header
        header_format = f"{self.endianness}{self.header_precision * self.HEADER_LEN_DWORDS}"
        header_size = struct.calcsize(header_format)

        header_bytes = p_file.read(header_size)
        if len(header_bytes) != header_size:
            raise EOFError("Unexpected end of file while reading header.")

        sample_rate_hz, center_frequency_hz, num_samples_interleaved = self._unpack(header_bytes, header_format)

        # validate file size and make sure it matches the sample count
        start_offset = p_file.tell()
        p_file.seek(0, SEEK_END)
        end_offset = p_file.tell()
        remaining_bytes = end_offset - start_offset

        expected_bytes = int(num_samples_interleaved) * self.SAMPLE_PRECISION_BYTES
        if remaining_bytes != expected_bytes:
            raise BufferError(f"File buffer mismatch: expected {expected_bytes} bytes for {num_samples_interleaved} samples, " f"found {remaining_bytes} bytes.")

        # rewind to payload start and read samples
        p_file.seek(start_offset, SEEK_SET)
        samples_bytes = p_file.read(expected_bytes)
        if len(samples_bytes) != expected_bytes:
            raise EOFError("Unexpected end of file while reading samples.")

        # must have dropped a sample
        if num_samples_interleaved % 2 != 0:
            raise ValueError("Number of interleaved samples must be even (IQ pairs).")

        # numpy dtype string uses '>' or '<' followed by 'i' for 16-bit signed integers
        numpy_dtype = f"{self.endianness}{self._numpy_sample_type}"
        samples = np.frombuffer(samples_bytes, dtype=numpy_dtype).astype(np.float32, copy=False)

        # deinterleave the raw IQ into complex
        iq_complex = self.deinterleave(samples)

        # leave as 0 for now
        initial_time_offset_sec = 0

        return Waveform(iq_complex, sample_rate_hz, center_frequency_hz, initial_time_offset_sec=initial_time_offset_sec)

    @staticmethod
    def _unpack(data: bytes, format_spec: str) -> Tuple:
        """Unpack structured binary data and return the resulting tuple."""
        return struct.unpack(format_spec, data)
