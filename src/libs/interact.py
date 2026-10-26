"""Functions to interact with the user."""

import logging

import pandas as pd
import questionary

from libs.priority import Priority

log = logging.getLogger(__name__)


def ask_events(data: pd.DataFrame) -> list[str]:
    """Ask the user which events they want to attend to.

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the schedule

    Returns
    -------
    list[str]
        User answer

    """
    from libs.data import get_all_events

    events = list(set(get_all_events(data)))
    answer = questionary.checkbox(
        "Which events do you want to attend to?", choices=events
    ).ask()
    log.info(f"Chosen events: {answer}")

    return answer


def ask_priorities(events: list[str]) -> dict[str, Priority]:
    """For each event we ask the user its priority and return a list of all priorities in `float`.

    Parameters
    ----------
    events : list[str]
        Events chosen by the user

    Returns
    -------
    dict[str, Priority]
        Priorities for each event

    """
    from libs.priority import Priority

    result = {}
    for event in events:
        priority_str = questionary.select(
            f'What is the priority for "{event}"?',
            choices=[p.value for p in Priority],
            default=Priority.MEDIUM.value,
        ).ask()
        log.debug(f'Priority for event "{event}": {priority_str}')

        priority = Priority(priority_str)
        result[event] = priority

    return result
