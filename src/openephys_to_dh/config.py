from dataclasses import dataclass, field
from os import PathLike
import os
from enum import StrEnum

from vstim.network_event_codes import VStimEventCode


class ContGroups(StrEnum):
    RAW = "RAW"
    ANALOG = "ANALOG"
    LFP = "LFP"
    ESA = "ESA"
    AP = "AP"


DEFAULT_OE_STREAM_MAPPING = {
    "PXIe-6341": ContGroups.RAW,
    "PCIe-6341": ContGroups.RAW,
    "example_data": ContGroups.RAW,
    "Neuropix-PXI": ContGroups.RAW,
}


DEFAULT_CONT_GROUP_RANGES = {
    ContGroups.RAW: (
        1,
        1600,
    ),  # room for 4 x 384 = 1536 channels from Neuropixel probe
    ContGroups.ANALOG: (1601, 2000),
    # downsampled signals
    ContGroups.LFP: (2001, 4000),
    ContGroups.ESA: (4001, 6000),
    # high-pass filtered signals (not downsamples, should not be used for long-term storage)
    ContGroups.AP: (6001, 8000),
}


# @dataclass_json
@dataclass
class RawConfig:
    split_channels_into_cont_blocks: bool = True
    cont_ranges: dict[ContGroups, tuple] = field(
        default_factory=lambda: DEFAULT_CONT_GROUP_RANGES.copy()
    )

    oe_processor_cont_group_map: dict[str, ContGroups] = field(
        default_factory=lambda: DEFAULT_OE_STREAM_MAPPING.copy()
    )


# @dataclass_json
@dataclass
class EsaMuaConfig:
    pass


# @dataclass_json
@dataclass
class EventPreprocessingConfig:
    network_events_offset: int = 1000
    network_events_code_name_map: dict[str, int] | None = field(
        default_factory=lambda: VStimEventCode.asdict()
    )
    ttl_line_names: dict[str, int] | None = None


@dataclass
class TrialMapConfig:
    use_message_center_messages: bool = True
    trial_start_ttl_line: int | None = None


@dataclass
class SpikeCuttingConfig:
    pass


@dataclass
class DecimationConfig:
    downsampling_factor: int = 30
    ftype: str = "fir"
    zero_phase: bool = True
    filter_order: int | None = 600
    channel_names: list[str] | None = None  # doall if None
    start_block_id: int = 2001


@dataclass
class OpenEphysToDhConfig:
    raw_config: RawConfig | None
    decimation_config: DecimationConfig | None
    event_config: EventPreprocessingConfig | None
    trialmap_config: TrialMapConfig | None
    spike_cutting_config: SpikeCuttingConfig | None


def save_config_to_file(config_filename: PathLike, config: OpenEphysToDhConfig) -> None:
    import json
    from dataclasses import asdict

    jsonstringconf = json.dumps(asdict(config), indent=True)
    with open(config_filename, mode="w") as config_file:
        config_file.write(jsonstringconf)


def load_config_from_file(config_path: PathLike) -> OpenEphysToDhConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        import json

        config_data = json.load(f)

    return OpenEphysToDhConfig(**config_data)
