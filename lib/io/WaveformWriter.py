from pathlib import Path

from lib.Waveform import Waveform
from lib.io.writers.BinWriter import BinWriter
from lib.io.writers.BaseWriter import BaseWriter


class WaveformWriter:

    @staticmethod
    def execute_write(outfile_path: Path, waveform_obj: Waveform, writer_strategy: BaseWriter) -> None:

        try:

            with open(outfile_path, "wb") as p_file:
                writer_strategy.write(p_file, waveform_obj)

        except FileNotFoundError:
            print(f"File path not found or inaccessible: {outfile_path}")
            raise  # Re-raise to stop execution if file doesn't exist

        except PermissionError:
            print(f"Permission denied when writing to: {outfile_path}")
            raise

        except (IOError, OSError) as e:
            # Catch general IO issues (disk full, write errors)
            print(f"Failed to write {outfile_path}: {type(e).__name__} - {e}")  # Includes traceback if logging level is debug/info
            raise

        except Exception as e:
            # Catch anything else specific to the writer logic
            print(f"Unexpected error writing {outfile_path}: {e}")
            raise

    @staticmethod
    def write_bin_file(outfile_path: Path, waveform_obj: Waveform, endianness: str = ">") -> None:

        # setup the strategy
        write_strategy = BinWriter(endianness)

        WaveformWriter.execute_write(outfile_path, waveform_obj, write_strategy)
