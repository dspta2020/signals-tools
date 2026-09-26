from abc import ABC, abstractmethod
from typing import BinaryIO

import numpy as np


class BaseParser(ABC):

    # Class-level constants for default expectations
    DEFAULT_ENDIANNESS = ">"
    DEFAULT_SAMPLE_PRECISION = "h"
    DEFAULT_HEADER_PRECISION = "I"

    def __init__(self, endianness: str = ">") -> None:
        self.sample_precision = self.DEFAULT_SAMPLE_PRECISION
        self.header_precision = self.DEFAULT_HEADER_PRECISION
        self._setup_endianness(endianness)

    def _setup_endianness(self, endianness: str) -> None:
        """Validates and sets the byte order. Raises ValueError if invalid."""
        # Normalize input (strip spaces usually expected but validate explicitly)
        normalized = endianness.strip()

        if normalized not in ["<", ">"]:

            if self.DEFAULT_ENDIANNESS == ">":
                print(f"Invalid endianness '{endianness}' detected. " f"Falling back to default: {self.DEFAULT_ENDIANNESS}")
                self.endianness = self.DEFAULT_ENDIANNESS
            else:
                # If this was a strict configuration error, we might want to raise here
                # For now, logging is safer for backward compatibility
                raise ValueError(f"Invalid endianness string provided: {endianness}")

        # Store the validated value
        self.endianness = normalized

    @abstractmethod
    def parse(self, p_file: BinaryIO):
        """
        Executes specific file parsing logic.
        """
        pass

    def get_config_summary(self) -> str:
        return f"Endian: {self.endianness}, " f"Header: {self.header_precision}, " f"Sample: {self.sample_precision}"

    @staticmethod
    def deinterleave(iq_raw: np.ndarray, dtype: type = np.float32) -> np.ndarray:
        arr = np.asarray(iq_raw)

        if arr.ndim != 1:
            raise ValueError("iq_raw must be a 1D array of interleaved samples.")

        if arr.size % 2 != 0:
            raise ValueError("iq_raw length must be even (IQ pairs).")

        # Ensure float for complex construction
        arr = arr.astype(dtype, copy=False)

        i_vals = arr[0::2]
        q_vals = arr[1::2]
        return i_vals + 1j * q_vals
