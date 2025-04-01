from pathlib import Path
from open_ephys.analysis import Session
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording, Continuous
from open_ephys.analysis.recording import ContinuousMetadata

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

    recording: BinaryRecording = session.recordnodes[0].recordings[0]
    for cont in recording.continuous:
        cont :Continuous
        metadata : ContinuousMetadata = cont.metadata
        start_cont_id = contstart[metadata.stream_name]

        for index, name in enumerate(cont.metadata.channel_names):
            id = start_cont_id + index
            shape = cont.samples.shape

    # assert recording is not None, "Failed to load recording data"
