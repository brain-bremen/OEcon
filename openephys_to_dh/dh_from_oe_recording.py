import enum
import time
import dh5io
import dh5io.create
import dh5io.cont
import dh5io.event_triggers
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording, Continuous
from open_ephys.analysis.recording import ContinuousMetadata
import numpy as np
from openephys_to_dh.network_event_codes import VStimEventCode

from openephys_to_dh.events import (
    EventMetadata,
    FullWordEvent,
    event_from_eventfolder,
    Event,
)


class ContGroups(enum.IntEnum):
    RAW = 1
    ANALOG = 1601
    LFP = 2001
    ESA = 4001
    AP = 6001


# including endpoints for each group
CONT_GROUP_RANGES = {
    # room for 4 x 384 = 1536 channels from Neuropixel probe
    ContGroups.RAW: (1, 1600),
    ContGroups.ANALOG: (1601, 2000),
    # downsampled signals
    ContGroups.LFP: (2001, 4000),
    ContGroups.ESA: (4001, 6000),
    # high-pass filtered signals (not downsamples, should not be used for long-term storage)
    ContGroups.AP: (6001, 8000),
}

OE_PROCESSOR_CONT_GROUP_MAP = {
    "PXIe-6341": ContGroups.RAW,
    "PCIe-6341": ContGroups.RAW,
    "example_data": ContGroups.RAW,
    "Neuropix-PXI": ContGroups.RAW,
}


def find_ev02_source(oeinfo: dict):
    for event in oeinfo["events"]:
        if (
            event["source_processor"] == "NI-DAQmx"
            and event["stream_name"] == "PXIe-6341"
        ):
            return EventMetadata(**event)
    return None


def find_marker_source(oeinfo: dict):
    """Network Events for Markers"""
    for event in oeinfo["events"]:
        if event["source_processor"] == "Network Events":
            return EventMetadata(**event)


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

    # continuous raw data
    global_channel_index = 0

    for cont in recording.continuous:
        # cont: Continuous
        metadata: ContinuousMetadata = cont.metadata

        cont_group: ContGroups | None = OE_PROCESSOR_CONT_GROUP_MAP.get(
            metadata.stream_name
        )
        if cont_group is None:
            raise ValueError(
                f"Unknown continuous stream name: {metadata.stream_name}. "
                f"Available stream names are {(OE_PROCESSOR_CONT_GROUP_MAP.keys())}."
            )
        group_range_start_index: int = CONT_GROUP_RANGES[cont_group][0]
        start_cont_id = global_channel_index + group_range_start_index

        nSamples, nChannels = cont.samples.shape
        if split_channels_into_cont_blocks:
            create_cont_group_per_channel(
                oe_continuous=cont,
                dh5file=dh5file,
                metadata=metadata,
                start_cont_id=start_cont_id,
                first_global_channel_index=global_channel_index,
            )
            global_channel_index += nChannels
        else:
            create_cont_group_per_continuous_stream(
                oe_continuous=cont,
                dh5file=dh5file,
                metadata=metadata,
                start_cont_id=start_cont_id,
            )

    # events
    ev02_source_metadata = find_ev02_source(recording.info)
    timestamps_ns = np.array([], dtype=np.int64)
    event_codes = np.array([], dtype=np.int32)
    if ev02_source_metadata is not None:
        network_events_words = event_from_eventfolder(
            recording_directory=recording.directory,
            metadata=ev02_source_metadata,
        )
        assert isinstance(network_events_words, Event)

        timestamps_ns = np.array(network_events_words.timestamps * 1e9, dtype=np.int64)
        event_codes = network_events_words.states

    network_events_offset = 1000
    network_events_source = find_marker_source(recording.info)
    if network_events_source is not None:
        network_events_words = event_from_eventfolder(
            recording_directory=recording.directory,
            metadata=network_events_source,
        )
        assert isinstance(network_events_words, FullWordEvent)

        # append to timesatamps_ns and event_codes
        timestamps_ns = np.concatenate(
            (timestamps_ns, network_events_words.timestamps * 1e9)
        ).astype(np.int64)
        event_codes = np.concatenate(
            (event_codes, network_events_words.full_words + network_events_offset)
        ).astype(np.int32)

    # sort event_codes and timesamps_ns according to timestamps_ns
    sort_indices = np.argsort(timestamps_ns)
    timestamps_ns = timestamps_ns[sort_indices]
    event_codes = event_codes[sort_indices]

    assert all(np.diff(timestamps_ns) >= 0)

    dh5io.event_triggers.add_event_triggers_to_file(
        dh5file.file, timestamps_ns=timestamps_ns, event_codes=event_codes
    )

    if network_events_source is not None:
        # add names of events as attributes to dataset
        ev02_dataset = dh5file.file["EV02"]
        for event_code in VStimEventCode:
            ev02_dataset.attrs[str(event_code.name)] = np.int32(
                event_code.value + network_events_offset
            )


def create_cont_group_per_channel(
    oe_continuous: Continuous,
    dh5file: dh5io.DH5File,
    metadata: ContinuousMetadata,
    start_cont_id: int,
    first_global_channel_index: int,
):
    global_channel_index = first_global_channel_index
    index = dh5io.cont.create_empty_index_array(1)
    # split channels into CONT block per channel (TODO: make this optional)
    for channel_index, name in enumerate(metadata.channel_names):
        dh5_cont_id = start_cont_id + channel_index

        channel_info = dh5io.cont.create_channel_info(
            GlobalChanNumber=global_channel_index,
            BoardChanNo=channel_index,
            ADCBitWidth=16,
            MaxVoltageRange=10.0,
            MinVoltageRange=10.0,
            AmplifChan0=0,
        )

        data = oe_continuous.samples[:, channel_index : channel_index + 1]

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


def create_cont_group_per_continuous_stream(
    oe_continuous: Continuous,
    dh5file: dh5io.DH5File,
    metadata: ContinuousMetadata,
    start_cont_id: int,
    last_global_channel_index: int = 0,
):
    # create a CONT group for the entire continuous stream
    dh5_cont_id = start_cont_id

    # TODO: This should be an array of channel info objects, one for each channel
    # but for now, we just create one channel info object for the entire stream
    channel_info = dh5io.cont.create_channel_info(
        GlobalChanNumber=last_global_channel_index,
        BoardChanNo=0,
        ADCBitWidth=16,
        MaxVoltageRange=10.0,
        MinVoltageRange=10.0,
        AmplifChan0=0,
    )

    # TODO: add streaming data if too large for memory
    data = oe_continuous.samples
    index = dh5io.cont.create_empty_index_array(1)

    dh5io.cont.create_cont_group_from_data_in_file(
        file=dh5file,
        cont_group_id=dh5_cont_id,
        data=data,
        index=index,
        sample_period_ns=np.int32(1.0 / metadata.sample_rate * 1e9),
        name=metadata.source_node_name,
        channels=channel_info,
        calibration=metadata.bit_volts,
    )
