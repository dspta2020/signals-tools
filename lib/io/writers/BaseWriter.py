from abc import ABC, abstractmethod
from typing import BinaryIO

from lib.Waveform import Waveform


class BaseWriter(ABC):

    # Class-level constants for default expectations
    DEFAULT_ENDIANNESS = ">"
    DEFAULT_SAMPLE_PRECISION = "h"
    DEFAULT_HEADER_PRECISION = "I"

    def __init__(self, endianness: str = ">") -> None:
        self.sample_precision = self.DEFAULT_SAMPLE_PRECISION
        self.header_precision = self.DEFAULT_HEADER_PRECISION
        self._validate_endianness(endianness)

    def _validate_endianness(self, endianness: str) -> None:
        """Validates and sets the byte order. Raises ValueError if invalid."""
        # Normalize input (strip spaces usually expected but validate explicitly)
        normalized = endianness.strip()

        if normalized not in ["<", ">"]:
            print(f"Invalid endianness '{endianness}' detected. " f"Falling back to default: {self.DEFAULT_ENDIANNESS}")
            self.endianness = self.DEFAULT_ENDIANNESS

        # Store the validated value
        self.endianness = normalized

    @abstractmethod
    def write(self, p_file: BinaryIO, waveform_obj: Waveform) -> None:
        """
        Executes specific file writing logic.
        """
        pass

    def get_config_summary(self) -> str:
        return f"Endian: {self.endianness}, " f"Header: {self.header_precision}, " f"Sample: {self.sample_precision}"
