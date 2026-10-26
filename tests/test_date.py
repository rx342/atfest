"""Test `libs.date` functions."""

import datetime as dt
import random

import pandas as pd


def test_remove_morning_events():
    """Test `remove_morning_events`."""
    from uuid import uuid4
    from zoneinfo import ZoneInfo

    from libs.date import remove_morning_events

    def create_morning_event(starting_hour: int) -> tuple[str, float, float]:
        """Create a event that occurs in the morning.

        Parameters
        ----------
        starting_hour : int
            Minimum starting hour even (24h format)

        Returns
        -------
        tuple[str, float, float]
            Return the (event name, starting time, ending time) of the vent

        """
        event = uuid4()

        start = dt.datetime(
            year=random.randint(2020, 2026),
            month=random.randint(1, 12),
            day=random.randint(1, 27),
            hour=random.randint(0, starting_hour - 1),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            tzinfo=ZoneInfo("Europe/Paris"),
        )
        end = start + dt.timedelta(
            hours=random.randint(1, 3),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )

        return (str(event), start.timestamp(), end.timestamp())

    def create_non_morning_event(starting_hour: int) -> tuple[str, float, float]:
        """Create a event that does not occur in the morning.

        Parameters
        ----------
        starting_hour : int
            Minimum starting hour even (24h format)

        Returns
        -------
        tuple[str, float, float]
            Return the (event name, starting time, ending time) of the vent

        """
        event = uuid4()

        start = dt.datetime(
            year=random.randint(2020, 2026),
            month=random.randint(1, 12),
            day=random.randint(1, 27),
            hour=random.randint(starting_hour, 19),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            tzinfo=ZoneInfo("Europe/Paris"),
        )
        end = start + dt.timedelta(
            hours=random.randint(1, 3),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )

        return (str(event), start.timestamp(), end.timestamp())

    def create_data(starting_hour: int) -> tuple[pd.DataFrame, int]:
        """Return a `pd.DataFrame` containing random valid data.

        Parameters
        ----------
        starting_hour : int
            Minimum starting hour even (24h format)

        Returns
        -------
        tuple[pd.DataFrame, int]
            Return the data structure with the number of non morning events

        """
        num_events = 100
        num_morning_events = random.randint(10, num_events - 20)
        num_non_morning_events = num_events - num_morning_events

        events, start, end = [], [], []
        for _ in range(num_morning_events):
            event, event_start, event_end = create_morning_event(starting_hour)

            events.append(event)
            start.append(event_start)
            end.append(event_end)

        for _ in range(num_morning_events, num_events):
            event, event_start, event_end = create_non_morning_event(starting_hour)

            events.append(event)
            start.append(event_start)
            end.append(event_end)

        df = pd.DataFrame(data={"event": events, "start": start, "end": end})

        return (df, num_non_morning_events)

    for _ in range(100):
        starting_hour = random.randint(1, 14)
        data, groundtruth = create_data(starting_hour)

        result = remove_morning_events(data, starting_hour)

        assert len(result) == groundtruth
