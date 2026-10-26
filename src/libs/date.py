"""Functions related to date."""

import datetime as dt
import logging
from zoneinfo import ZoneInfo

import pandas as pd

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


def date_from_timestamp(ts: int) -> dt.datetime:
    """Convert a timestamp to a `dt.datetime` object.

    Parameters
    ----------
    ts : int
        Timestamp to convert

    Returns
    -------
    dt.datetime
        Converted timestamp

    """
    result = dt.datetime.fromtimestamp(
        ts,
        tz=ZoneInfo("Europe/Paris"),
    )

    return result


def convert_timestamp_to_datetime(data: pd.DataFrame) -> pd.DataFrame:
    """Convert timestamp columns in the `pd.DataFrame` data in a datetime string.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to convert fields

    Returns
    -------
    pd.DataFrame
        New DataFrame with datetime columns

    """

    def converter(column: pd.Series) -> pd.Series:
        return pd.to_datetime(column, unit="s", utc=True).dt.tz_convert("Europe/Paris")

    result = data.copy()
    result["start"] = converter(result["start"])  # type: ignore
    result["end"] = converter(result["end"])  # type: ignore

    return result


def convert_timestamp_to_day(data: pd.DataFrame) -> pd.DataFrame:
    """Convert timestamp columns in the `pd.DataFrame` data to keep only the day of the event.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to convert fields

    Returns
    -------
    pd.DataFrame
        New DataFrame with datetime columns

    """

    result = convert_timestamp_to_datetime(data)
    result["start"] = result["start"].dt.date
    result["end"] = result["end"].dt.date

    return result
