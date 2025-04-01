from pathlib import Path
from open_ephys.analysis import Session
import pytest

session_name = "Kobi_2025-03-31_11-48-13"

# Define the relative path to the data folder
data_folder = Path(__file__).parent / "data" / session_name

# Check if the data folder exists
skip_tests = data_folder.exists() and data_folder.is_dir()


@pytest.mark.skipif(skip_tests, reason="Data folder does not exist")
def test_load_data():
    session = Session(data_folder)
    assert session is not None, "Failed to load session data"
