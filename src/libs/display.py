"""Display functions."""

import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd
from rich import print
from rich.table import Table


def print_dataframe(data: pd.DataFrame, num_elements: int = 5):
    """Pretty print a `pd.Dataframe` schedule.

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the schedule
    num_elements : int
        Number of elements to pretty print

    """

    table = Table(show_header=True)
    table.add_column("Event", style="bold cyan")
    table.add_column("Start", style="green")
    table.add_column("End", style="magenta")

    for i, row in data.iterrows():
        if i < num_elements:  # type: ignore
            date_start = dt.datetime.fromtimestamp(
                int(row["start"]),  # type: ignore
                tz=ZoneInfo("Europe/Paris"),
            )
            date_end = dt.datetime.fromtimestamp(
                int(row["end"]),  # type: ignore
                tz=ZoneInfo("Europe/Paris"),
            )

            table.add_row(
                row["event"],  # type: ignore
                f"{date_start:%Y-%m-%d (%H:%M)}",
                f"{date_end:%Y-%m-%d (%H:%M)}",
            )
        else:
            break

    print(table)


def print_solution(solution: pd.DataFrame, choices: list[str]):
    """Print the solution in a nice table.

    Parameters
    ----------
    solution : pd.DataFrame
        DataFrame containing all the possible events to attend to
    choices : list[str]
        User choices

    """
    print(f"Found {len(solution)} possible events out of {len(choices)}")

    table = Table(show_header=True)
    table.add_column("Event", style="bold cyan")
    table.add_column("Start", style="green")
    table.add_column("End", style="magenta")

    for i, row in solution.iterrows():
        date_start = dt.datetime.fromtimestamp(
            int(row["start"]),  # type: ignore
            tz=ZoneInfo("Europe/Paris"),
        )
        date_end = dt.datetime.fromtimestamp(
            int(row["end"]),  # type: ignore
            tz=ZoneInfo("Europe/Paris"),
        )

        table.add_row(
            row["event"],  # type: ignore
            f"{date_start:%H:%M (%d-%m-%Y)}",
            f"{date_end:%H:%M (%d-%m-%Y)}",
        )

    print(table)

    missing = set(choices) - set(solution["event"])
    formatted_missing = [f"[bold cyan]{m}[/bold cyan]" for m in missing]

    if len(formatted_missing):
        print(
            f"The [bold red]missing[/bold red] events are: {', '.join(formatted_missing)}"
        )
