import time
import json
from pathlib import Path

from lib.Waveform import Waveform
from lib.io.WaveformWriter import WaveformWriter
from lib.io.WaveformReader import WaveformReader

import numpy as np
import matplotlib.pyplot as plt


def main():

    # paths here
    path_to_data = Path(r"data\\1876954_7680KSPS_srsRAN_Project_gnb_short.sigmf-data")
    path_to_meta = Path(r"data\\1876954_7680KSPS_srsRAN_Project_gnb_short.sigmf-meta")

    with path_to_meta.open("r") as f:
        meta = json.load(f)

    # get the global configs
    global_configs = meta["global"]
    capture_configs = meta["captures"][0]

    # parsing
    fs = global_configs["core:sample_rate"]
    fc = capture_configs["core:frequency"]

    # ci32_le = little-endian signed int32 I and Q components
    raw = np.fromfile(path_to_data, dtype="<i4")
    # reshape the i and the q
    iq_int = raw.reshape(-1, 2)
    # convert to complex and keep intended precision
    iq = iq_int[:, 0].astype(np.float32) + 1j * iq_int[:, 1].astype(np.float32)

    # make waveform
    wf_original = Waveform(iq, fs, fc)

    # based on the metadata should be more samples but in the blog post it says 143 msec
    # capture which is what I'm seeing here
    if 0:
        plt.figure(1)
        wf.visualizer.plot_spectrogram(4096, 8192, "msec", "mhz")
        plt.show()

    # now write the waveform out
    WaveformWriter.write_mf_bin_file(Path("5g_example.mfbin"), wf_original)

    wf = WaveformReader.read_mf_bin_file(Path("5g_example.mfbin"))
    if 0:
        plt.figure(1)
        wf.visualizer.plot_spectrogram(4096, 8192, "msec", "mhz")

    # might have introduced some quantization noise
    plt.figure(1)
    plt.plot(np.abs(wf_original.samples - wf.samples))
    plt.show()

    return


if __name__ == "__main__":
    print(f"\nRunning File: {Path(__file__).name}\n")
    start_time = time.perf_counter()

    main()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nElapsed time: {elapsed_time:.6f} seconds\n")
