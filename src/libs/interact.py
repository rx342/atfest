"""Functions to interact with the user."""

import logging

import pandas as pd
import questionary

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
