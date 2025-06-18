from oecon.config import DecimationConfig
from dh5io import DH5File
from open_ephys.analysis.recording import Recording as OERecording

class MuaConfig:


def extract_continuous_mua(
    config: MuaConfig, decimation_config : DecimationConfig, recording: OERecording, dh5file: DH5File
):
    assert recording.continuous is not None, (
        "No continuous data found in the recording."
    )

    global_channel_index = 0
    dh5_cont_id = config.

