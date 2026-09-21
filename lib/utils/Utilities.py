from typing import NamedTuple


class Utilities:

    FREQ_UNIT_DATA = [
        ("THz", 1e12),
        ("GHz", 1e9),
        ("MHz", 1e6),
        ("kHz", 1e3),
        ("Hz", 1.0),
    ]

    TIME_UNIT_DATA = [
        ("ps", 1e-12),
        ("ns", 1e-9),
        ("us", 1e-6),
        ("ms", 1e-3),
        ("s", 1.0),
    ]

    # internal class to return a named tuple
    class ScaledResult(NamedTuple):
        value: float
        unit: str

    @staticmethod
    def auto_scale_frequency(freq_hz: float) -> "Utilities.ScaledResult":
        """
        Scales a frequency to the largest appropriate unit.
        Rounds to 3 significant digits or 2 decimal places for readability.
        """
        abs_val = abs(freq_hz)

        if abs_val == 0:
            return Utilities.ScaledResult(value=0, unit="Hz")

        # Iterate from largest unit down to find the first bucket the value fits in
        for unit_name, threshold in Utilities.FREQ_UNIT_DATA:
            if abs_val > threshold:
                scaled = freq_hz / threshold
                # Round to avoid floating point errors (e.g. 0.9999 instead of 1.0)
                return Utilities.ScaledResult(value=round(scaled, 4), unit=unit_name)

        return Utilities.ScaledResult(value=round(abs_val, 4), unit="Hz")

    @staticmethod
    def auto_scale_time(time_sec: float) -> "Utilities.ScaledResult":
        """
        Scales a time value to the largest appropriate unit.
        Rounds to 3 significant digits or 2 decimal places for readability.
        """
        abs_val = abs(time_sec)

        if abs_val == 0:
            return Utilities.ScaledResult(value=0, unit="s")

        # Iterate from largest unit down to find the first bucket the value fits in
        for unit_name, threshold in Utilities.TIME_UNIT_DATA:
            if abs_val < threshold:
                scaled = time_sec / threshold
                # Round to avoid floating point errors (e.g. 0.9999 instead of 1.0)
                return Utilities.ScaledResult(value=round(scaled, 4), unit=unit_name)

        return Utilities.ScaledResult(value=round(abs_val, 4), unit="s")
