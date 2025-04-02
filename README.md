# Tools for preprocessing of Open Ephys data into DAQ-HDF (DH5) format

- For now, each Open Ephys "Recording" will result in a DH5 file (data folder is created on OpenEphys startup, experiment is incremented each time acquisition is started, )

**TODO** 

- [x] Add CONT blocks from OE recordings
- [ ] Add TTL events to DH5 file (into EV02)
- [ ] Add Network Events as Markers
- [ ] Add Text messages as Markers
- [ ] Handle online/offline synchronization of streams
- [ ] Add creating TRIALMAP from TDR

## Channel Mapping

| Group Prefix   | Block start | Block id end (incl.) | Purpose
| -------------- | ----------- | -------------------- | --------------
| CONT           |           1 |                 1600 | Raw neural data, fits 4 x 384 = 1536 Neuropixel channels
| CONT           |        1601 |                 2000 | Analog data, e.g. eye data, 50 Hz, flicker
| CONT           |        2001 |                 3600 | Downsampled LFP, corresponding to 1-1600
| CONT           |        3601 |                 4000 | Downsamples/Preprocessed analog data, corresponding to 1601-2000
| CONT           |        4001 |                 5600 | Downsampled MUA/ESA, corresponding to 1-1600
| CONT           |        6001 |                 7600 | High-pass filtered raw data (potentially unnecessary)
| SPIKE          |           1 |                 1000 | Sorted spikes

