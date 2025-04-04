from pathlib import Path
import os
import open_ephys.analysis as oe
from open_ephys.analysis.formats import BinaryRecording
import pytest
from openephys_to_dh.dh_from_oe_recording import dh_from_oe_recording as oerec2dh
from openephys_to_dh.events import (
    EventMetadata,
    Event,
    Messages,
    FullWordEvent,
    event_from_eventfolder,
)

session_name = "Kobi_2025-03-31_11-48-13"
# session_name = "Test_2025-04-03_12-48-58"
# session_name = "Test_2025-04-03_12-55-07"
# Define the relative path to the data folder
data_folder = Path(__file__).parent / "data" / session_name

# Check if the data folder exists
skip_real_data_tests = not (data_folder.exists() and data_folder.is_dir())


@pytest.fixture()
def recording() -> BinaryRecording:
    session = oe.Session(str(data_folder))
    assert session is not None, "Failed to load session data"

    recording_index = 0
    recording = session.recordnodes[0].recordings[recording_index]
    return recording


@pytest.mark.skipif(skip_real_data_tests, reason="Data folder does not exist")
def test_load_data(recording):

    oerec2dh(
        recording,
        session_name,
        recording_index=0,
    )


@pytest.mark.skipif(skip_real_data_tests, reason="Data folder does not exist")
def test_load_events(recording):
    events = recording.info["events"]
    for event in events:
        metadata = EventMetadata(**event)
        event_data = event_from_eventfolder(
            recording_directory=recording.directory,
            metadata=metadata,
        )
        assert isinstance(event_data, (Event, Messages, FullWordEvent))
