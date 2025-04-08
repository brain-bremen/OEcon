import dh5io
import dh5io.create
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording
from openephys_to_dh.events import process_oe_events
from openephys_to_dh.config import (
    EventPreprocessingConfig,
    OpenEphysToDhConfig,
    RawConfig,
    SpikeCuttingConfig,
    DecimationConfig,
)
from openephys_to_dh.raw import process_oe_raw_data
from openephys_to_dh.decimation import decimate_raw_data


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

    config = OpenEphysToDhConfig(
        raw_config=RawConfig(split_channels_into_cont_blocks=True),
        decimation_config=DecimationConfig(),
        event_config=EventPreprocessingConfig(network_events_offset=1000),
        spike_cutting_config=SpikeCuttingConfig(),
    )

    if config.raw_config is not None:
        process_oe_raw_data(config.raw_config, recording, dh5file)

    if config.event_config is not None:
        process_oe_events(config.event_config, recording=recording, dh5file=dh5file)

    if config.decimation_config is not None:
        decimate_raw_data(
            config.decimation_config, recording=recording, dh5file=dh5file
        )


if __name__ == "__main__":
    pass
