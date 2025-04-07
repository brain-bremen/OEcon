from openephys_to_dh.config import RawConfig
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording, Continuous
from open_ephys.analysis.recording import ContinuousMetadata
from dh5io import DH5File
import dh5io
import numpy as np


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


def process_raw_data(config: RawConfig, recording: BinaryRecording, dh5file: DH5File):

    # continuous raw data
    global_channel_index = 0
    for cont in recording.continuous:
        # cont: Continuous
        metadata: ContinuousMetadata = cont.metadata

        cont_group: ContGroups | None = config.oe_processor_cont_group_map.get(
            metadata.stream_name
        )
        if cont_group is None:
            raise ValueError(
                f"Unknown continuous stream name: {metadata.stream_name}. "
                f"Available stream names are {(config.oe_processor_cont_group_map.keys())}."
            )
        group_range_start_index: int = config.cont_ranges[cont_group][0]
        start_cont_id = global_channel_index + group_range_start_index

        nSamples, nChannels = cont.samples.shape
        if config.split_channels_into_cont_blocks:
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
