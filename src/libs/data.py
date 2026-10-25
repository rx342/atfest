"""Data functions."""

import json
import logging
from pathlib import Path

import pandas as pd
import questionary

log = logging.getLogger(__name__)


def create_schedule(output_path: Path):
    """Create a new schedule into a file.

    Parameters
    ----------
    output_path : Path
        Path to the new schedule

    """
    from libs.date import (
        check_date,
        check_duration,
        compute_end_time,
        convert_string_to_date,
        convert_string_to_duration,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = []
    while True:
        event = questionary.text("What's the event?").ask()
        log.debug(f"Event entered: {event}")

        date_start_str = questionary.text(
            "When does it start?", instruction="DD/MM/YYYY HH:MM", validate=check_date
        ).ask()
        log.debug(f"Starting date entered: {date_start_str}")
        date_start = convert_string_to_date(date_start_str)

        duration_str = questionary.text(
            "What is the duration?", instruction="HH:MM", validate=check_duration
        ).ask()
        log.debug(f"Duration entered: {duration_str}")
        date_end = compute_end_time(
            date_start, convert_string_to_duration(duration_str)
        )

        result.append(
            {
                "event": event,
                "start": date_start.timestamp(),
                "end": date_end.timestamp(),
            }
        )

        stop = questionary.confirm("Do you want to stop?", default=False).ask()
        if stop:
            break

    with open(output_path, "w") as f:
        json.dump(result, f)

    log.info(f"Schedule written in {output_path}")


def read_schedule(input_path: Path) -> pd.DataFrame:
    """Read a `.json` file and return a `pd.DataFrame`.

    Parameters
    ----------
    input_path : Path
        Path to `.json`

    Returns
    -------
    pd.DataFrame
        Dataframe containing the data from `.json` file

    """
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    with open(input_path, "r") as f:
        data = json.load(f)

    result = pd.json_normalize(data)
    result = result.astype({"event": "str", "start": "uint32", "end": "uint32"})
    result = result.sort_values(by=["start"])

    return result


def get_all_events(data: pd.DataFrame) -> list[str]:
    """Return all events into a list of string.

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the schedule

    Returns
    -------
    list[str]
        List of events

    """
    return data["event"].to_list()
