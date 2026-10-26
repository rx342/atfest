"""Test `libs.priority` functions."""

import random

from libs.priority import Priority


def test_get_priority_vector():
    """Test `get_priority_vector`"""

    import pandas as pd

    from libs.priority import convert_priority_to_float, get_priority_vector

    def create_data() -> pd.DataFrame:
        """Return a `pd.DataFrame` containing random valid data."""

        events = [f"event_{random.randint(0, 5)}" for _ in range(100)]
        num_events = len(events)
        start = [random.randint(1767225600, 1798675200) for _ in range(num_events)]
        end = [x + random.randint(3600, 3 * 3600) for x in start]
        df = pd.DataFrame(data={"event": events, "start": start, "end": end})

        return df

    def create_user_choices(data: pd.DataFrame) -> list[str]:
        """Return a list of events random chosen from `data`.

        Parameters
        ----------
        data : pd.DataFrame
            Data containing the schedule

        Returns
        -------
        list[str]
            List of events randomly picked

        """
        num_events = len(set(data["event"]))
        num_choices = random.randint(1, num_events - 1)
        return random.sample(list(set(data["event"])), num_choices)

    def create_user_priorities(user_choices: list[str]) -> dict[str, Priority]:
        return {choice: random.choice([p for p in Priority]) for choice in user_choices}

    for _ in range(100):
        data = create_data()
        user_choices = create_user_choices(data)
        user_priorities = create_user_priorities(user_choices)

        vector_priorities = get_priority_vector(data, user_priorities)

        for i, row in data.iterrows():
            event = row["event"]
            if event in user_priorities:
                priority_float = convert_priority_to_float(user_priorities[event])  # type: ignore
                assert priority_float == vector_priorities[i]
            else:
                assert vector_priorities[i] == 0
