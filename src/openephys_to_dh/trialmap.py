import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Callable
import dhspec
import dh5io
import numpy as np
from dh5io import DH5File
import dh5io.trialmap
from open_ephys.analysis.formats.BinaryRecording import BinaryRecording
from vstim.tdr import TrialOutcome

from openephys_to_dh.config import TrialMapConfig
from openephys_to_dh.events import EventMetadata, Messages, event_from_eventfolder
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrialStartMessage:
    trial_index: int
    trial_type_number: int
    time_sequence_index: int
    frame_number: int


@dataclass
class TrialEndMessage:
    trial_index: int
    trial_type_number: int
    frame_number: int
    outcome: TrialOutcome


def parse_trial_start_message(message_string: str) -> TrialStartMessage:
    """Extract trial start properties from TRIAL_START message such as

    `TRIAL_START 1 TRIALTYPE 0 TIMESEQUENCE 0 FRAME 1032`

    """

    if "TRIAL_START" not in message_string:
        raise ValueError(f"Message is not a TRIAL_START message: {message_string}")

    message_string = message_string.strip()
    parts = message_string.split()

    if len(parts) < 8 or len(parts) % 2 != 0:
        raise ValueError(
            f"Cannot extract trial from trial start message: {message_string}"
        )

    trial_index: int | None = None
    trial_type: int | None = None
    time_sequence_index: int | None = None
    frame_number: int | None = None

    for i in range(0, len(parts), 2):
        key, value = parts[i], parts[i + 1]
        match key:
            case "TRIAL_START":
                trial_index = int(value)
            case "TRIALTYPE":
                trial_type = int(value)
            case "TIMESEQUENCE":
                time_sequence_index = int(value)
            case "FRAME":
                frame_number = int(value)
            case _:
                warnings.warn(
                    f"Unsupported key {key}={value} in message: {message_string}"
                )

    if (
        trial_index is None
        or trial_type is None
        or time_sequence_index is None
        or frame_number is None
    ):
        raise ValueError(
            f"Cannot extract trial from trial start message: {message_string}"
        )

    return TrialStartMessage(
        trial_index=trial_index,
        trial_type_number=trial_type,
        time_sequence_index=time_sequence_index,
        frame_number=frame_number,
    )


def parse_trial_end_message(message_string: str) -> TrialEndMessage:
    """Extract trial end properties from TRIAL_END message such as

    `TRIAL_END 1 TRIALTYPE 0 TIMESEQUENCE 0 FRAME 2048 OUTCOME 4`

    """

    if "TRIAL_END" not in message_string:
        raise ValueError(f"Message is not a TRIAL_END message: {message_string}")

    parts = message_string.split()

    if len(parts) < 8 or len(parts) % 2 != 0:
        raise ValueError(
            f"Cannot extract trial from trial end message: {message_string}"
        )

    trial_index: int | None = None
    trial_type: int | None = None
    frame_number: int | None = None
    outcome: TrialOutcome | None = None

    for i in range(0, len(parts), 2):
        key, value = parts[i], parts[i + 1]
        match key:
            case "TRIAL_END":
                trial_index = int(value)
            case "TRIALTYPE":
                trial_type = int(value)
            case "FRAME":
                frame_number = int(value)
            case "OUTCOME":
                outcome = TrialOutcome(int(value))
            case _:
                warnings.warn(
                    f"Unsupported key {key}={value} in message: {message_string}"
                )

    if (
        trial_index is None
        or trial_type is None
        or frame_number is None
        or outcome is None
    ):
        raise ValueError(
            f"Cannot extract trial from trial end message: {message_string}"
        )

    return TrialEndMessage(
        trial_index=trial_index,
        trial_type_number=trial_type,
        frame_number=frame_number,
        outcome=outcome,
    )


class MessageType(Enum):
    TRIAL_START = "TRIAL_START"
    TRIAL_END = "TRIAL_END"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


message_type_parser_map: dict[MessageType, Callable] = {
    MessageType.TRIAL_START: parse_trial_start_message,
    MessageType.TRIAL_END: parse_trial_end_message,
    MessageType.UNKNOWN: lambda x: None,
}


def parse_message(
    message: str, accept_without_vstim_prefix: bool = True
) -> TrialStartMessage | TrialEndMessage | None:
    message = message.strip()
    if message.startswith("VSTIM:"):
        message = message[len("VSTIM:") :]
    message = message.strip()

    message_type = MessageType(message.split(sep=" ")[0])

    return message_type_parser_map[message_type](message)


def find_message_source(oeinfo: dict) -> EventMetadata | None:
    for event in oeinfo["events"]:
        if event["source_processor"] == "Message Center":
            return EventMetadata(**event)
    return None


def get_messages_from_recording(
    recording: BinaryRecording,
) -> Messages:
    message_source = find_message_source(recording.info)
    assert message_source is not None

    messages = event_from_eventfolder(
        recording_directory=recording.directory, metadata=message_source
    )

    assert isinstance(messages, Messages)
    return messages


def process_oe_trialmap(
    config: TrialMapConfig, recording: BinaryRecording, dh5file: DH5File
):
    oe_messages = get_messages_from_recording(recording)
    trial_start_messages: list[TrialStartMessage] = []
    trial_start_timestamps = []
    trial_end_messages: list[TrialEndMessage] = []
    trial_end_timestamps = []
    for msg in oe_messages:
        parsed_message = parse_message(msg["text"])
        if isinstance(parsed_message, TrialStartMessage):
            trial_start_messages.append(parsed_message)
            trial_start_timestamps.append(msg["timestamp"])
        if isinstance(parsed_message, TrialEndMessage):
            trial_end_messages.append(parsed_message)
            trial_end_timestamps.append(msg["timestamp"])

    if len(trial_start_messages) != len(trial_end_messages):
        logger.warning(
            f"Number of trial start messages ({len(trial_start_messages)}) does not match number of trial end messages ({len(trial_end_messages)})"
        )
        if len(trial_start_messages) == len(trial_end_messages) + 1:
            logger.warning("Attempting correcting by removing last trial start message")
            trial_start_messages.pop()
            trial_start_timestamps.pop()

            assert len(trial_start_timestamps) == len(trial_end_messages)

    for i, (start_msg, end_msg) in enumerate(
        zip(trial_start_messages, trial_end_messages)
    ):
        if start_msg.trial_index != end_msg.trial_index:
            raise ValueError(
                f"Trial index mismatch at position {i}: start={start_msg.trial_index}, end={end_msg.trial_index}"
            )

    new_trialmap = np.recarray(
        shape=(len(trial_start_messages)),
        dtype=dhspec.trialmap.TRIALMAP_DATASET_DTYPE,
    )

    for iTrial, msg in enumerate(trial_start_messages):
        end_message = trial_end_messages[iTrial]

        assert msg.trial_index == end_message.trial_index

        new_trialmap[iTrial].TrialNo = msg.trial_index
        new_trialmap[iTrial].StimNo = msg.trial_type_number
        new_trialmap[iTrial].Outcome = trial_end_messages[iTrial].outcome.value
        new_trialmap[iTrial].StartTime = np.int64(trial_start_timestamps[iTrial] * 1e9)
        new_trialmap[iTrial].EndTime = np.int64(trial_end_timestamps[iTrial] * 1e9)

    dh5io.trialmap.add_trialmap_to_file(dh5file.file, new_trialmap)
