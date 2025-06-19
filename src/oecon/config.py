import logging
import os
from dataclasses import dataclass, field
from os import PathLike

from oecon.decimation import DecimationConfig
from oecon.events import EventPreprocessingConfig
from oecon.raw import RawConfig
from oecon.trialmap import TrialMapConfig
from oecon.mua import ContinuousMuaConfig

VERSION = 1

logger = logging.getLogger(__name__)


@dataclass
class SpikeCuttingConfig:
    pass


@dataclass
class OpenEphysToDhConfig:
    raw_config: RawConfig | None
    decimation_config: DecimationConfig | None
    event_config: EventPreprocessingConfig | None
    trialmap_config: TrialMapConfig | None
    spike_cutting_config: SpikeCuttingConfig | None
    continuous_mua_config: ContinuousMuaConfig | None
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

    continuous_mua_config = config_data.get("continuous_mua_config", None)
    if continuous_mua_config is not None:
        continuous_mua_config = ContinuousMuaConfig(**continuous_mua_config)

    # TODO: properly handle enums in dicts

    return OpenEphysToDhConfig(
        raw_config=raw_config,
        decimation_config=decimation_config,
        event_config=event_config,
        trialmap_config=trialmap_config,
        spike_cutting_config=spike_cutting_config,
        continuous_mua_config=continuous_mua_config,
    )
