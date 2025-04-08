import dh5io
from dh5io import DH5File
import numpy as np
import scipy.signal as signal
from openephys_to_dh.config import DecimationConfig
from open_ephys.analysis.recording import Recording


def decimate_raw_data(config: DecimationConfig, recording: Recording, dh5file: DH5File):

    assert (
        recording.continuous is not None
    ), "No continuous data found in the recording."

    global_channel_index = 0
    dh5_cont_id = config.start_block_id

    for cont in recording.continuous:
        metadata = cont.metadata

        assert (
            metadata.channel_names is not None
        ), "Channel names are not set in OE data."

        if config.channel_names is None:
            included_channel_names = metadata.channel_names
        else:
            included_channel_names = config.channel_names

        # TODO: Use chunks of channels in parallel
        for channel_index, channel_name in enumerate(metadata.channel_names):

            # skip channel if not in included channels
            if channel_name not in included_channel_names:
                continue

            samples = cont.get_samples(
                start_sample_index=0,
                end_sample_index=-1,
                selected_channels=None,
                selected_channel_names=[channel_name],
            )
            # samples x channels

            identifier = "some_identifier"
            decimated_samples = signal.decimate(
                x=samples,
                q=config.downsampling_factor[identifier],
                n=config.filter_order,
                ftype=config.ftype,
                axis=0,
                zero_phase=config.zero_phase,
            )

            channel_info = dh5io.cont.create_channel_info(
                GlobalChanNumber=global_channel_index,
                BoardChanNo=channel_index,
                ADCBitWidth=16,
                MaxVoltageRange=10.0,
                MinVoltageRange=10.0,
                AmplifChan0=0,
            )

            dh5io.cont.create_cont_group_from_data_in_file(
                file=dh5file,
                cont_group_id=dh5_cont_id,
                data=decimated_samples,
                index=dh5io.cont.create_empty_index_array(1),
                sample_period_ns=np.int32(1.0 / metadata.sample_rate * 1e9),
                name=channel_name,
                channels=channel_info,
                calibration=metadata.bit_volts[channel_index],
            )

            dh5_cont_id += 1
            global_channel_index += 1
