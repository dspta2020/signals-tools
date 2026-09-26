Repo primary focus is for Python digital signal processing tooling.

Current codebase centers around:
1. **`lib/Waveform`**: A domain model encapsulating digital signals (complex & real), derived physical and signal properties, some math transformations and 
some file serializations (which are TODO).
2. **`lib/WaveformVisualizer`**: Encapsulated plotting utilities providing standard time-domain, spectral (TODO), and spectrogram visualizations of
`Waveform` instances. 
3. **`lib/utils/Utilites`**: General purpose helper functions mapping data types.
4. **`lib/io/WaveformReader`**: Peripheral to read waveforms out of bin files. Currently only supports file format of header 3x int32s and interleaved I and Q sample data as int16s. 
5. **`lib/io/WaveformWriter`**: Peripheral to write waveform into bin files. Currently only supports file format of header 3x int32s and interleaved I and Q sample data as int16s. 