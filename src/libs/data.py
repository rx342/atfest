"""Data functions."""

import datetime as dt
import json
import logging
from pathlib import Path

import pandas as pd
import questionary

log = logging.getLogger(__name__)


def convert_string_to_date(date: str) -> dt.datetime:
    """Convert a date to a `dt.datetime` object.

    Parameters
    ----------
    date : str
        Date with the format "DD/MM/YY HH:MM"

    Returns
    -------
    dt.datetime
        Date converted to a `dt.datetime` object

    """
    from zoneinfo import ZoneInfo

    result = dt.datetime.strptime(date, "%d/%m/%Y %H:%M").astimezone(
        ZoneInfo("Europe/Paris")
    )
    log.debug(f"Convert {date} to `datetime`: {result:%Y-%m-%d %H:%M:%S%z}")

    return result


def check_date(s: str) -> bool:
    """Check if the string `s` is correctly formatted as a date

    Parameters
    ----------
    s : str
        String to check

    Returns
    -------
    bool
        `True` if correct else `false`

    """
    try:
        dt.datetime.strptime(s, "%d/%m/%Y %H:%M").astimezone(dt.UTC)
        return True
    except ValueError:
        return False


def convert_string_to_duration(time: str) -> dt.timedelta:
    """Convert a date to a `dt.timedelta` object.

    Parameters
    ----------
    time : str
        Time duration with the format "HH:MM"

    Returns
    -------
    dt.timedelta
        Time duration converted to a `dt.timedelta` object

    """

    hour, min = (int(x) for x in time.split(":"))
    result = dt.timedelta(hours=hour, minutes=min)
    log.debug(f"Convert {time} to `timedelta`: {result}")

    return result


def check_duration(s: str) -> bool:
    """Check if the string `s` is correctly formatted as a time duration

    Parameters
    ----------
    s : str
        String to check

    Returns
    -------
    bool
        `True` if correct else `False`

    """
    try:
        hour_str, min_str = s.split(":")

        _, min = int(hour_str), int(min_str)
        return 0 <= min <= 59
    except ValueError:
        return False


def compute_end_time(start: dt.datetime, duration: dt.timedelta) -> dt.datetime:
    """Compute the end time of an event

    Parameters
    ----------
    start : dt.date
        Starting time of the event
    duration : dt.timedelta
        Duration of the event

    Returns
    -------
    dt.date
        End time of the event

    """
    result = start + duration
    log.debug(f"End time is: {result:%Y-%m-%d %H:%M:%S%z}")

    return result


def create_schedule(output_path: Path):
    """Create a new schedule into a file.

    Parameters
    ----------
    output_path : Path
        Path to the new schedule

    """
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
