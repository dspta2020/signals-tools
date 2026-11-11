import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from modulators.FSKModulator import FSKModulator
from lib.Waveform import Waveform


def main():

    # sampling configs
    data_rate = 32e3
    sample_rate_hz = data_rate * 512
    frequency_deviation = 800e3

    mod = FSKModulator(sample_rate_hz, data_rate, frequency_deviation)

    # setup some random byte data
    buffer_in = bytes([128, 255, 1])
    num_bytes = len(buffer_in)
    num_bytes = 255
    buffer_in = np.random.bytes(num_bytes)

    # modulate this buffer
    samples = mod.modulate(buffer_in)

    fig, ax = plt.subplots()
    mod.plot_phase(buffer_in)

    wf = Waveform(samples, sample_rate_hz, 0)

    fig, ax = plt.subplots()
    wf.visualizer.plot_spectrogram(512, 8192, "us", "khz")
    plt.show()

    return


if __name__ == "__main__":
    print(f"\nRunning File: {Path(__file__).name}\n")
    start_time = time.perf_counter()

    main()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nElapsed time: {elapsed_time:.6f} seconds\n")
