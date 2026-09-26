from abc import ABC, abstractmethod

from lib.Waveform import Waveform


class BasePlotter(ABC):

    def __init__(self, waveform: Waveform):
        super().__init__()
        # waveform object containing signal data
        self.waveform = waveform

    @abstractmethod
    def plot(self, **kwargs):
        """
        Executes specific plotting logic. Subclasses must override this method.
        """
        pass
