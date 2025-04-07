import dh5io
import dh5io.create
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording
from openephys_to_dh.events import process_oe_events
from openephys_to_dh.config import EventPreprocessingConfig, RawConfig
from openephys_to_dh.raw import process_raw_data


def dh_from_oe_recording(
    recording: BinaryRecording,
    session_name: str,
    recording_index: int = 0,
    split_channels_into_cont_blocks: bool = True,
):
    assert (
        recording.continuous is not None
    ), "No continuous data found in the recording."

    if len(recording.continuous) == 0:
        raise ValueError(
            "No continuous data found in the recording. This is not supported."
        )

    board_names = [
        f"{cont.metadata.source_node_name}:{cont.metadata.source_node_id}"
        for cont in recording.continuous
    ]
    dh5filename = f"{session_name}_{recording_index}.dh5"
    dh5file = dh5io.create.create_dh_file(
        dh5filename, overwrite=True, boards=board_names
    )

    raw_config = RawConfig(split_channels_into_cont_blocks=True)
    process_raw_data(raw_config, recording, dh5file)

    event_config = EventPreprocessingConfig(network_events_offset=1000)
    process_oe_events(event_config, recording=recording, dh5file=dh5file)


if __name__ == "__main__":
    pass
