from dataclasses import dataclass

import dh5io
import dh5io.operations
import dh5io.cont
import numpy as np
import scipy.signal as signal
from dh5io import DH5File
from open_ephys.analysis.recording import Recording as OERecording

from oecon.decimation import DecimationConfig, decimate_np_array


@dataclass
class MuaConfig:
    highpass_cutoff_hz: float = 300.0


def extract_continuous_mua(
    config: MuaConfig,
    decimation_config: DecimationConfig,
    recording: OERecording,
    dh5file: DH5File,
):
    assert recording.continuous is not None, (
        "No continuous data found in the recording."
    )

    global_channel_index = 0
    dh5_cont_id = decimation_config.start_block_id

    # Default high-pass cutoff if not set in config
    highpass_cutoff = config.highpass_cutoff_hz

    for oe_cont in recording.continuous:
        oe_metadata = oe_cont.metadata

        assert oe_metadata.channel_names is not None, (
            "Channel names are not set in OE data."
        )

        if decimation_config.channel_names is None:
            included_channel_names = oe_metadata.channel_names
        else:
            included_channel_names = decimation_config.channel_names

        for channel_index, channel_name in enumerate(oe_metadata.channel_names):
            if channel_name not in included_channel_names:
                continue

            samples = oe_cont.get_samples(
                start_sample_index=0,
                end_sample_index=-1,
                selected_channels=None,
                selected_channel_names=[channel_name],
            )

            # High-pass filter
            sos = signal.butter(
                N=4,
                Wn=config.highpass_cutoff_hz,
                btype="highpass",
                fs=oe_metadata.sample_rate,
                output="sos",
            )
            filtered = signal.sosfiltfilt(sos, samples, axis=0)

            # Rectify
            rectified = np.abs(filtered)

            # Decimate
            decimated_samples = decimate_np_array(
                x=rectified,
                q=decimation_config.downsampling_factor,
                n=decimation_config.filter_order,
                ftype=decimation_config.ftype,
                axis=0,
                zero_phase=decimation_config.zero_phase,
            )

            channel_info = dhspec.cont.create_channel_info(
                GlobalChanNumber=global_channel_index,
                BoardChanNo=channel_index,
                ADCBitWidth=16,
                MaxVoltageRange=10.0,
                MinVoltageRange=10.0,
                AmplifChan0=0,
            )

            dh5io.cont.create_cont_group_from_data_in_file(
                file=dh5file.file,
                cont_group_id=dh5_cont_id,
                data=decimated_samples,
                index=dhspec.cont.create_empty_index_array(1),
                sample_period_ns=np.int32(1.0 / oe_metadata.sample_rate * 1e9),
                name=channel_name,
                channels=channel_info,
                calibration=np.array(oe_metadata.bit_volts[channel_index]),
            )

            dh5_cont_id += 1
            global_channel_index += 1

    dh5io.operations.add_operation_to_file(
        dh5file.file,
        "extract_continuous_mua",
        "oecon_mua_extraction",
    )
