from pathlib import Path
import logging

from lib.Waveform import Waveform
from lib.io.parsers.BinParser import BinParser
from lib.io.parsers.BaseParser import BaseParser


class WaveformReader:
    @staticmethod
    def execute_read(infile_path: Path, parser_strategy: BaseParser) -> Waveform:
        """Open infile_path and parse it using parser_strategy, returning a Waveform.

        parser_strategy must implement BaseParser.parse and return a Waveform.
        """
        if not isinstance(parser_strategy, BaseParser):
            raise TypeError("parser_strategy must be an instance of BaseParser")

        try:
            with infile_path.open("rb") as p_file:
                return parser_strategy.parse(p_file)

        except FileNotFoundError:
            print(f"File path not found or inaccessible: {infile_path}")
            raise  # Re-raise to stop execution if file doesn't exist

        except PermissionError:
            print(f"Permission denied when writing to: {infile_path}")
            raise

        except (IOError, OSError) as e:
            # Catch general IO issues (disk full, write errors)
            print(f"Failed to write {infile_path}: {type(e).__name__} - {e}")  # Includes traceback if logging level is debug/info
            raise

        except Exception as e:
            # Catch anything else specific to the writer logic
            print(f"Unexpected error writing {infile_path}: {e}")
            raise

    @staticmethod
    def read_bin_file(infile_path: Path) -> Waveform:
        """Convenience helper that reads a binary waveform file using BinParser."""
        parsing_strategy = BinParser()
        return WaveformReader.execute_read(infile_path, parsing_strategy)
