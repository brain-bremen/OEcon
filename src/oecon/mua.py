from dataclasses import dataclass

import dh5io
import dh5io.cont
import dh5io.operations
import numpy as np
import numpy.typing as npt
import scipy.signal as signal
from dh5io import DH5File
from dhspec.cont import create_channel_info, create_empty_index_array
from open_ephys.analysis.recording import Recording as OERecording

import oecon.default_mappings as default
from oecon.decimation import DecimationConfig, decimate_np_array


@dataclass
class FilterConfigBA:
    b: list[float] | None | npt.NDArray[np.float64]
    a: list[float] | None | npt.NDArray[np.float64]


@dataclass
class ContinuousMuaConfig:
    highpass_cutoff_hz: float = 300.0
    filter_coecfficients_b_a: FilterConfigBA | None = None
    included_channel_names: list[str] | None = None  # None for all
    start_block_id: int = default.DEFAULT_CONT_GROUP_RANGES[default.ContGroups.ESA][0]


def extract_continuous_mua(
    config: ContinuousMuaConfig,
    decimation_config: DecimationConfig,
    recording: OERecording,
    dh5file: DH5File,
) -> ContinuousMuaConfig:
    assert recording.continuous is not None, (
        "No continuous data found in the recording."
    )

    global_channel_index = 0
    dh5_cont_id = config.start_block_id

    for oe_cont in recording.continuous:
        oe_metadata = oe_cont.metadata

        assert oe_metadata.channel_names is not None, (
            "Channel names are not set in OE data."
        )

        if config.included_channel_names is None:
            config.included_channel_names = oe_metadata.channel_names

        decimation_config.included_channel_names = config.included_channel_names

        for channel_index, channel_name in enumerate(oe_metadata.channel_names):
            if channel_name not in config.included_channel_names:
                continue

            samples = oe_cont.get_samples(
                start_sample_index=0,
                end_sample_index=-1,
                selected_channels=None,
                selected_channel_names=[channel_name],
            )

            # High-pass filter
            if config.filter_coecfficients_b_a is None:
                b, a = signal.butter(
                    N=4,
                    Wn=config.highpass_cutoff_hz,
                    btype="highpass",
                    fs=oe_metadata.sample_rate,
                )
                config.filter_coecfficients_b_a = FilterConfigBA(b=b, a=a)
            filtered = signal.filtfilt(
                b=np.array(config.filter_coecfficients_b_a.b),
                a=np.array(config.filter_coecfficients_b_a.a),
                x=samples,
                axis=0,
            )

            # Rectify
            rectified = np.abs(filtered)

            # Decimate
            decimated_samples = decimate_np_array(
                data=rectified,
                downsampling_factor=decimation_config.downsampling_factor,
                filter_order=decimation_config.filter_order,
                filter_type=decimation_config.ftype,
                axis=0,
                zero_phase=decimation_config.zero_phase,
            )

            channel_info = create_channel_info(
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
                index=create_empty_index_array(1),
                sample_period_ns=np.int32(
                    1.0
                    / oe_metadata.sample_rate
                    * 1e9
                    * decimation_config.downsampling_factor
                ),
                name=f"{oe_metadata.stream_name}/{channel_name}/MUA",
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

    return config
