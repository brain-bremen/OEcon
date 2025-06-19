# Conversion tools for preprocessing of Open Ephys data into DAQ-HDF (DH5) format

**`OEcon`** provides a cli tool and a Python library to convert and preprocess data recorded
using the [OpenEphys GUI](https://open-ephys.github.io/gui-docs/index.html) into the
in-house [DAQ-HDF5](https://github.com/cog-neurophys-lab/DAQ-HDF5) file format. The
conversion at the moment includes the following configurable steps

- Place raw data in DH5 file
- Decimate (downsample) raw data into LFP
- Extract TTL triggers and store as events
- Process network events sent from [VStim](http://vstim.brain.uni-bremen.de)
- Extract trialmap from messages sent from [VStim](http://vstim.brain.uni-bremen.de)

The resulting DH5 files can be opened with any HDF5 software such as the
[HDFView](https://www.hdfgroup.org/download-hdfview). Specialized tools for reading the data
are available for MATLAB ([dhfun](https://github.com/cog-neurophys-lab/dhfun2)) and Python
([dh5io](https://github.com/cog-neurophys-lab/dh5io)). Each Open Ephys "Recording" will
result in a DH5 file (data folder is created on OpenEphys startup, experiment is incremented
each time acquisition is started)

Future versions may include spike sorting and time-frequency estimation.

## Use OEcon as cli tool

To run the cli tool, use [uv]()
```
uvx https://github.com/brain-bremen/OEcon.git
```

Alternatively use a [binary release](https://github.com/brain-bremen/OEcon/releases).

## Use OEcon as a library

To use OEcon as a library, install it via pip into your virtual environment.
```
pip git+https://github.com/brain-bremen/OEcon.git
```

Then you can use it in your Python code:
```python
...
```


## Default CONT block ranges

| Group Prefix   | Block start | Block id end (incl.) | Purpose
| -------------- | ----------- | -------------------- | --------------
| CONT           |           1 |                 1600 | Raw neural data, fits 4 x 384 = 1536 Neuropixel channels
| CONT           |        1601 |                 2000 | Analog data, e.g. eye data, 50 Hz, flicker
| CONT           |        2001 |                 3600 | Downsampled LFP, corresponding to 1-1600
| CONT           |        3601 |                 4000 | Downsamples/Preprocessed analog data, corresponding to 1601-2000
| CONT           |        4001 |                 5600 | Downsampled MUA/ESA, corresponding to 1-1600
| CONT           |        6001 |                 7600 | High-pass filtered raw data (potentially unnecessary)
| SPIKE          |           1 |                 1000 | Sorted spikes

