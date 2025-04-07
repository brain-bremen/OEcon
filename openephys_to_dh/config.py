from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from enum import Enum


class ContGroups(Enum):
    RAW = "RAW"
    ANALOG = "ANALOG"
    LFP = "LFP"
    ESA = "ESA"
    AP = "AP"


@dataclass_json
@dataclass
class RawConfig:
    split_channels_into_cont_blocks: bool = True
    cont_ranges: dict[ContGroups, tuple] = field(
        default_factory=lambda: {
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
    )

    oe_processor_cont_group_map: dict[str, ContGroups] = field(
        default_factory=lambda: {
            "PXIe-6341": ContGroups.RAW,
            "PCIe-6341": ContGroups.RAW,
            "example_data": ContGroups.RAW,
            "Neuropix-PXI": ContGroups.RAW,
        }
    )


@dataclass_json
@dataclass
class EventPreprocessingConfig:
    network_events_offset: int = 1000


@dataclass_json
@dataclass
class SpikeCuttingConfig:
    pass


@dataclass_json
@dataclass
class DecimationConfig:
    pass


@dataclass_json
@dataclass
class OpenEphysToDhConfig:
    raw_config: RawConfig | None
    decimation_config: DecimationConfig | None
    event_config: EventPreprocessingConfig | None
    spike_cutting_config: SpikeCuttingConfig | None
