from enum import StrEnum

import pandas as pd


class Priority(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def convert_priority_to_float(p: Priority) -> float:
    """Convert a priority to a float value.

    If a priority value is not matched, it returns the default value of `MEDIUM`.

    Parameters
    ----------
    p : Priority
        Priority to convert to float

    Returns
    -------
    float
        Float value for the priority

    """

    default_value = 2.0
    match p:
        case Priority.LOW:
            return 1.0
        case Priority.MEDIUM:
            return default_value
        case Priority.HIGH:
            return 5
        case _:
            return default_value


def get_priority_vector(
    data: pd.DataFrame, priorities: dict[str, Priority]
) -> list[float]:
    """From a dictionary of priorities, return the full vector of priorities in float values.

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the schedule
    priorities : dict[str, Priority]
        Dictionary where each key is the event name and the value is the priority

    Returns
    -------
    list[float]
        Vector of priorities in float

    """
    result = []
    for _, row in data.iterrows():
        event = row["event"]
        if event in priorities:
            result.append(convert_priority_to_float(priorities[event]))  # type: ignore
        else:
            result.append(0)

    return result
