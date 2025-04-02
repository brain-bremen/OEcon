from pathlib import Path
import dh5io.cont
import dh5io.create
from open_ephys.analysis import Session
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording, Continuous
from open_ephys.analysis.recording import ContinuousMetadata
import dh5io
import numpy as np
import pytest

session_name = "Kobi_2025-03-31_11-48-13"

# Define the relative path to the data folder
data_folder = Path(__file__).parent / "data" / session_name

# Check if the data folder exists
skip_tests = not (data_folder.exists() and data_folder.is_dir())

# map stream_name to start CONT block id
contstart = {"PXIe-6341": 1601, "example_data": 1}


@pytest.mark.skipif(skip_tests, reason="Data folder does not exist")
def test_load_data():
    session = Session(str(data_folder))
    assert session is not None, "Failed to load session data"

    recording_index = 0
    recording: BinaryRecording = session.recordnodes[0].recordings[recording_index]
    board_names = [
        f"{cont.metadata.source_node_name}:{cont.metadata.source_node_id}"
        for cont in recording.continuous
    ]
    dh5filename = f"{session_name}_{recording_index}.dh5"
    dh5file = dh5io.create.create_dh_file(
        dh5filename, overwrite=True, boards=board_names
    )
    global_channel_index = 0
    for cont in recording.continuous:
        cont: Continuous
        metadata: ContinuousMetadata = cont.metadata
        start_cont_id = contstart[metadata.stream_name]
        nSamples, nChannels = cont.samples.shape

        # split channels into CONT block per channel (TODO: make this optional)
        for channel_index, name in enumerate(cont.metadata.channel_names):
            dh5_cont_id = start_cont_id + channel_index

            channel_info = dh5io.cont.create_channel_info(
                GlobalChanNumber=global_channel_index,
                BoardChanNo=channel_index,
                ADCBitWidth=16,
                MaxVoltageRange=10.0,
                MinVoltageRange=10.0,
                AmplifChan0=0,
            )

            data = cont.samples[:, channel_index : channel_index + 1]
            index = dh5io.cont.create_empty_index_array(1)

            dh5io.cont.create_cont_group_from_data_in_file(
                file=dh5file,
                cont_group_id=dh5_cont_id,
                data=data,
                index=index,
                sample_period_ns=np.int32(1.0 / metadata.sample_rate * 1e9),
                name=name,
                channels=channel_info,
                calibration=metadata.bit_volts,
            )

            global_channel_index += 1
