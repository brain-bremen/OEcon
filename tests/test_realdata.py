from pathlib import Path
from open_ephys.analysis import Session
import pytest
from openephys_to_dh.dh_from_oe_recording import dh_from_oe_recording as oerec2dh

session_name = "Kobi_2025-03-31_11-48-13"

# Define the relative path to the data folder
data_folder = Path(__file__).parent / "data" / session_name

# Check if the data folder exists
skip_tests = not (data_folder.exists() and data_folder.is_dir())


@pytest.mark.skipif(skip_tests, reason="Data folder does not exist")
def test_load_data():
    session = Session(str(data_folder))
    assert session is not None, "Failed to load session data"

    recording_index = 0
    recording = session.recordnodes[0].recordings[recording_index]

    oerec2dh(
        recording,
        session_name,
        recording_index=0,
    )
