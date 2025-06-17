from dataclasses import dataclass, field
from os import PathLike
import os
from enum import StrEnum
import logging
from vstim.network_event_codes import VStimEventCode

VERSION = 1

logger = logging.getLogger(__name__)


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
    config_version: int = VERSION
    oecon_version: str = field(
        default_factory=lambda: __import__(
            "oecon.version"
        ).version.get_version_from_pyproject(),
        init=False,
    )


def save_config_to_file(config_filename: PathLike, config: OpenEphysToDhConfig) -> None:
    import json
    from dataclasses import asdict

    logger.info(f"Saving configration to {config_filename}")
    jsonstringconf = json.dumps(asdict(config), indent=True)
    with open(config_filename, mode="w") as config_file:
        config_file.write(jsonstringconf)


def load_config_from_file(config_path: PathLike) -> OpenEphysToDhConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    logger.info(f"Loading configuration from {config_path}")
    with open(config_path, "r") as f:
        import json

        config_data = json.load(f)

    if "config_version" not in config_data:
        logger.warning(
            "Configuration file does not contain a version. Assuming version {VERSION}. This may fail."
        )
        config_data["config_version"] = VERSION

    if config_data["config_version"] > VERSION:
        raise ValueError(
            f"Configuration file version {config_data['config_version']} is newer than supported version {VERSION}."
        )

    raw_config = config_data.get("raw_config", None)
    if raw_config is not None:
        raw_config = RawConfig(**raw_config)

    decimation_config = config_data.get("decimation_config", None)
    if decimation_config is not None:
        decimation_config = DecimationConfig(**decimation_config)
    event_config = config_data.get("event_config", None)
    if event_config is not None:
        event_config = EventPreprocessingConfig(**event_config)
    trialmap_config = config_data.get("trialmap_config", None)
    if trialmap_config is not None:
        trialmap_config = TrialMapConfig(**trialmap_config)
    spike_cutting_config = config_data.get("spike_cutting_config", None)
    if spike_cutting_config is not None:
        spike_cutting_config = SpikeCuttingConfig(**spike_cutting_config)

    # TODO: properly handle enums in dicts

    return OpenEphysToDhConfig(
        raw_config=raw_config,
        decimation_config=decimation_config,
        event_config=event_config,
        trialmap_config=trialmap_config,
        spike_cutting_config=spike_cutting_config,
    )
