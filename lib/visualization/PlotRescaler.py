class PlotRescaler:

    @staticmethod
    def get_time_scaling(unit_str: str):
        """
        Retrieve the scaling factor and label for an input time unit string.

        NOTE: Assumes conversions are implicitly assumed to always be FROM seconds i.e.
              the input data being scaled is in units of seconds.
        """
        unit_switch = unit_str.strip().lower()
        if unit_switch in ["sec", "seconds", "s"]:
            factor = 1
            label_str = "seconds"
            return factor, label_str
        elif unit_switch in ["msec", "milliseconds", "ms"]:
            factor = 1e3
            label_str = "milliseconds"
            return factor, label_str
        elif unit_switch in ["usec", "microseconds", "us"]:
            factor = 1e6
            label_str = "microseconds"
            return factor, label_str
        else:
            raise ValueError(f"PlotRescalar::InValidTimeUnit Unknown time unit {unit_str}")

    @staticmethod
    def get_frequency_scaling(unit_str: str):
        """
        Retrieve the scaling factor and label for an input time unit string.

        NOTE: Assumes conversions are implicitly assumed to always be FROM seconds i.e.
              the input data being scaled is in units of seconds.
        """
        unit_switch = unit_str.strip().lower()
        if unit_switch in ["hz", "hertz"]:
            factor = 1
            label_str = "Hz"
            return factor, label_str
        elif unit_switch in ["khz", "kilohertz"]:
            factor = 1e-3
            label_str = "kHz"
            return factor, label_str
        elif unit_switch in ["mhz", "megahertz"]:
            factor = 1e-6
            label_str = "MHz"
            return factor, label_str
        elif unit_switch in ["ghz", "gigahertz"]:
            factor = 1e-9
            label_str = "GHz"
            return factor, label_str
        else:
            raise ValueError(f"PlotRescalar::InValidFrequencyUnit Unknown frequency unit {unit_str}")
