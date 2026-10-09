from typing import BinaryIO, Tuple
import struct
from os import SEEK_END, SEEK_SET

import numpy as np

from lib.Waveform import Waveform
from lib.io.parsers.BaseParser import BaseParser


class BinParser(BaseParser):
    HEADER_LEN_DWORDS = 3
    HEADER_PRECISION_BYTES = 4
    SAMPLE_PRECISION_BYTES = 2

    # canonical numpy element type for 16-bit signed ints
    NUMPY_DATATYPE = "i2"
    HEADER_PRECISION = "I"

    def __init__(self, endianness: str = ">"):
        super().__init__(endianness)

    def parse(self, p_file: BinaryIO) -> Waveform:
        """Parse binary IQ file into a Waveform.

        File layout:
        - Header: 3 x uint32 (sample_rate_hz, center_frequency_hz, num_samples_interleaved)
        - Payload: num_samples_interleaved x int16 (interleaved I,Q,I,Q,...)
        """
        # read file header
        header_format = f"{self.endianness}{self.HEADER_PRECISION * self.HEADER_LEN_DWORDS}"
        header_size = struct.calcsize(header_format)

        # validate the size of the file
        header_bytes = p_file.read(header_size)
        if len(header_bytes) != header_size:
            raise EOFError("Unexpected end of file while reading header.")

        # unpack the header values
        sample_rate_hz, center_frequency_hz, num_samples_interleaved = self._unpack(header_bytes, header_format)

        # must have dropped a sample
        if num_samples_interleaved % 2 != 0:
            raise ValueError("Number of interleaved samples must be even (IQ pairs).")

        # if the file size doesnt match the number of expected samples, it might be corrupted
        expected_bytes = int(num_samples_interleaved) * self.SAMPLE_PRECISION_BYTES
        file_bytes = self._validate_sample_buffer(p_file)
        if file_bytes != expected_bytes:
            raise BufferError(f"File buffer mismatch: expected {expected_bytes} bytes for {num_samples_interleaved} samples, " f"found {remaining_bytes} bytes.")

        # read the samples
        samples_bytes = p_file.read(expected_bytes)
        if len(samples_bytes) != expected_bytes:
            raise EOFError("Unexpected end of file while reading samples.")

        # numpy dtype string uses '>' or '<' followed by 'i' for 16-bit signed integers
        numpy_dtype = f"{self.endianness}{self.NUMPY_DATATYPE}"
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

    @staticmethod
    def _validate_sample_buffer(p_file: BinaryIO):
        # validate file size and make sure it matches the sample count
        start_offset = p_file.tell()
        p_file.seek(0, SEEK_END)
        end_offset = p_file.tell()
        remaining_bytes = end_offset - start_offset
        p_file.seek(start_offset, SEEK_SET)  # rewind to payload start and read samples
        return remaining_bytes
