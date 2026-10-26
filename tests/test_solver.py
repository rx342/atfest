"""Test `libs.solver` functions."""

import itertools
import random

import numpy as np
import pandas as pd


def test_get_user_choice_vector():
    """Test `get_user_choice_vector`"""

    from libs.solver import get_user_choice_vector

    def check_values(user_choices: np.ndarray) -> bool:
        """Check if every values is either 0 or 1 (binary vector).

        Parameters
        ----------
        user_choices : np.ndarray
            Vector to check

        Returns
        -------
        bool
            `True` if binary vector else `False`

        """
        return all(x in (0, 1) for x in user_choices)

    def is_chosen_by_user(event: str, choices: list[str]) -> bool:
        """Check if an event is chosen by the user.

        Parameters
        ----------
        event : str
            Event to check
        choices : list[str]
            User choices

        Returns
        -------
        bool
            `True` if `event` belongs in `choices`

        """
        return event in choices

    def default_case():
        """Default case."""

        events = [f"event_{random.randint(0, 5)}" for _ in range(100)]
        num_unique_events = len(set(events))
        num_choices = random.randint(3, num_unique_events - 1)
        choices = random.sample(list(set(events)), num_choices)
        data = pd.DataFrame(data={"event": events})

        c = get_user_choice_vector(data, choices)

        groundtruth = [is_chosen_by_user(x, choices) for x in events]

        assert check_values(c)
        assert all(c == groundtruth)

    def no_choice_case():
        """User choice is empty hence we should get an empty vector."""

        data = pd.DataFrame(data={"event": []})
        assert len(get_user_choice_vector(data, [])) == 0

    def no_data_choice():
        """User chooses an event that does not exist, we should get an empty vector."""

        data = pd.DataFrame(data={"event": []})
        assert len(get_user_choice_vector(data, ["test"])) == 0

    for _ in range(100):
        default_case()

    no_choice_case()
    no_data_choice()


def test_uncompact_vector():
    """Test `uncompact_vector`."""
    from libs.solver import compact_vector, get_compacter_indices, uncompact_vector

    def create_binary_vector(dim: int) -> np.ndarray:
        """Return a random binary vector.

        Parameters
        ----------
        dim : int
            Dimension of the vector

        Returns
        -------
        np.ndarray
            Binary vector

        """
        vector = [random.randint(0, 1) for _ in range(dim)]
        return np.array(vector)

    for _ in range(100):
        dim = random.randint(10, 30)
        c = create_binary_vector(dim)

        compact_indices = get_compacter_indices(c)

        x = create_binary_vector(dim)
        x_tilde = compact_vector(x, compact_indices)
        result = uncompact_vector(x_tilde, compact_indices, dim)

        assert len(result) == dim
        assert all(x * c == result)


def test_solve():
    """Test `solve`."""
    from libs.priority import Priority
    from libs.solver import solve

    def check_values(x_star: np.ndarray) -> bool:
        """Check if every values is either 0 or 1 (binary vector).

        Parameters
        ----------
        x_star : np.ndarray
            Vector to check

        Returns
        -------
        bool
            `True` if binary vector else `False`

        """
        return all(x in (0, 1) for x in x_star)

    def time_overlap(time_1: tuple[int, int], time_2: tuple[int, int]) -> bool:
        """Check if `time_1` and `time_2` overlap.

        Parameters
        ----------
        time_1 : tuple[int, int]
            Tuple (start, end) event time for the first event
        time_2 : tuple[int, int]
            Tuple (start, end) event time for the second event

        Returns
        -------
        bool
            `True` if both event times overlap, else `False`

        """
        time_1_start, time_1_end = time_1
        time_2_start, time_2_end = time_2

        return time_1_start <= time_2_end and time_2_start <= time_1_end

    def check_event_time(x_star: np.ndarray, data: pd.DataFrame) -> bool:
        """Check if solution has overlapping events.

        Parameters
        ----------
        x_star : np.ndarray
            Optimal solution found by the solver

        data : pd.DataFrame
            Data containing the schedule

        Returns
        -------
        bool
            `True` if events are non overlapping, else `False`

        """
        from libs.solver import convert_binary_vector_to_pandas

        x_star_df = convert_binary_vector_to_pandas(x_star, data)
        timestamps = x_star_df[["start", "end"]]
        timestamps = list(
            x_star_df[["start", "end"]].itertuples(index=False, name=None)
        )

        all_combinations = itertools.pairwise(timestamps)

        return all(not time_overlap(t1, t2) for (t1, t2) in all_combinations)  # type: ignore

    def check_unique_event(x_star: np.ndarray, data: pd.DataFrame) -> bool:
        """Check if events name are unique in the solution (no duplicate).

        Parameters
        ----------
        x_star : np.ndarray
            Optimal solution found by the solver

        data : pd.DataFrame
            Data containing the schedule

        Returns
        -------
        bool
            `True` if events have unique name, else `False`

        """
        from libs.solver import convert_binary_vector_to_pandas

        x_star_df = convert_binary_vector_to_pandas(x_star, data)
        all_combinations = itertools.permutations(x_star_df["event"], 2)
        return all(e_1 != e_2 for (e_1, e_2) in all_combinations)

    def check_max_number_of_events_per_day(
        x_star: np.ndarray, data: pd.DataFrame, max_num_events_per_day: int
    ) -> bool:
        """Check if events respect the maximum number of events per day.

        Parameters
        ----------
        x_star : np.ndarray
            Optimal solution found by the solver

        data : pd.DataFrame
            Data containing the schedule

        max_num_events_per_day : int
            Maximum number of events per day

        Returns
        -------
        bool
            `True` if events respect the maximum number of events, else `False`

        """

        from libs.date import convert_timestamp_to_day
        from libs.solver import convert_binary_vector_to_pandas

        x_star_df = convert_timestamp_to_day(
            convert_binary_vector_to_pandas(x_star, data)
        )

        days = x_star_df["start"].unique()

        return all(
            len(x_star_df[x_star_df["start"] == day]) <= max_num_events_per_day
            for day in days
        )

    def create_max_number_of_events_per_day() -> int:
        """Return a random value for the maximum number of events per day."""
        return random.randint(1, 5)

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

    def default_case():
        """Default case."""

        data = create_data()
        user_choices = create_user_choices(data)
        user_priorities = create_user_priorities(user_choices)
        max_num_events_per_day = create_max_number_of_events_per_day()

        x_star = solve(data, user_choices, user_priorities, max_num_events_per_day)

        assert check_values(x_star)
        assert check_event_time(x_star, data)
        assert check_unique_event(x_star, data)
        assert check_max_number_of_events_per_day(x_star, data, max_num_events_per_day)

    def no_choice_case():
        """User choice is empty hence we should get an empty vector."""

        data = create_data()
        x_star = solve(data, [], {})

        assert all(x == 0 for x in x_star)

    for _ in range(30):
        default_case()
        no_choice_case()
