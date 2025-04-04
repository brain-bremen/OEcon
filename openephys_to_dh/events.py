from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pprint
import os
import warnings


@dataclass
class EventMetadata:
    channel_name: str
    folder_name: str
    identifier: str
    sample_rate: float
    stream_name: str
    type: str
    description: str
    source_processor: str
    initial_state: int = 0


@dataclass
class Messages:
    metadata: EventMetadata
    text: np.ndarray  # of str
    sample_numbers: np.ndarray
    timestamps: np.ndarray

    def __str__(self):
        metadata_str = pprint.pformat(self.metadata)
        return (
            f"Messages Data: {self.metadata.folder_name}')\n"
            f"├─── Text: {self.text.shape}\n"
            f"├─── Sample Numbers: {self.sample_numbers.shape}\n"
            f"└─── {metadata_str}\n"
        )

    @staticmethod
    def from_folder(full_event_folder_path: str | Path, metadata: EventMetadata):
        return Messages(
            metadata=metadata,
            text=np.load(os.path.join(full_event_folder_path, "text.npy")),
            sample_numbers=np.load(
                os.path.join(full_event_folder_path, "sample_numbers.npy")
            ),
            timestamps=np.load(os.path.join(full_event_folder_path, "timestamps.npy")),
        )


@dataclass
class Event:
    metadata: EventMetadata
    full_words: np.ndarray
    timestamps: np.ndarray
    states: np.ndarray
    sample_numbers: np.ndarray

    @staticmethod
    def from_folder(full_event_folder_path: str | Path, metadata=EventMetadata):
        return Event(
            metadata=metadata,
            full_words=np.load(os.path.join(full_event_folder_path, "full_words.npy")),
            timestamps=np.load(os.path.join(full_event_folder_path, "timestamps.npy")),
            states=np.load(os.path.join(full_event_folder_path, "states.npy")),
            sample_numbers=np.load(
                os.path.join(full_event_folder_path, "sample_numbers.npy")
            ),
        )

    def __str__(self):
        metadata_str = pprint.pformat(self.metadata)
        return (
            f"Event Data: {self.metadata.folder_name}')\n"
            f"├─── Full Words: {self.full_words.shape}\n"
            f"├─── Timestamps: {self.timestamps.shape}\n"
            f"├─── States: {self.states.shape}\n"
            f"├─── Sample Numbers: {self.sample_numbers.shape}\n"
            f"└─── {metadata_str}\n"
        )


def event_from_eventfolder(
    recording_directory: str | Path, metadata: EventMetadata
) -> Event | Messages:
    # full_event_folder_path = os.path.join(path, "events", metadata.folder_name)
    full_event_folder_path = (
        Path(recording_directory) / "events" / Path(metadata.folder_name)
    )

    assert os.path.exists(
        full_event_folder_path
    ), f"Events folder {full_event_folder_path} does not exist"

    # return data based on metadata.source_processor
    match metadata.source_processor:
        case "Network Events":
            return Event.from_folder(full_event_folder_path, metadata)
        case "Message Center":
            return Messages.from_folder(full_event_folder_path, metadata)
        case "NI-DAQmx":
            return Event.from_folder(full_event_folder_path, metadata)
        case _:
            warnings.warn(
                f"Unsupported source processor: {metadata.source_processor}. Attempting generic Event loading..."
            )
            return Event.from_folder(full_event_folder_path, metadata)
