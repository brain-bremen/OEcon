import warnings
from dataclasses import dataclass
from typing import Callable
from vstim.tdr import TrialOutcome
from enum import Enum


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
