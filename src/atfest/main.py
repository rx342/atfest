"""Main script that will be called with `atfest`."""

import argparse
import logging
import sys
from pathlib import Path

from rich.logging import RichHandler


def main():
    """Execute main function."""
    global_parser = argparse.ArgumentParser(add_help=False)

    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest="command")
    parser.add_argument(
        "--input", type=Path, default=None, help="Path to the schedule", required=True
    )
    sub_parsers.add_parser("new", parents=[global_parser], help="Create a new schedule")
    show_parser = sub_parsers.add_parser(
        "show", parents=[global_parser], help="Pretty print schedule"
    )
    show_parser.add_argument(
        "--num_elements", type=int, default=5, help="Number of elements to pretty print"
    )
    solve_parser = sub_parsers.add_parser(
        "solve", parents=[global_parser], help="Solve the schedule"
    )
    solve_parser.add_argument(
        "--max_num_events_per_day",
        type=int,
        default=3,
        help="Maximum number of events per day",
    )

    p_args = parser.parse_args()

    if p_args.command is None:
        parser.print_help()
        sys.exit(0)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    logger = logging.getLogger(__name__)

    logger.debug(f"Subcommand: {p_args.command}")
    logger.info(f"Input file: {p_args.input}")

    if p_args.command == "new":
        from libs.data import create_schedule

        create_schedule(p_args.input)
    if p_args.command == "show":
        from libs.data import read_schedule
        from libs.display import print_dataframe

        data = read_schedule(p_args.input)
        print_dataframe(data, p_args.num_elements)
    if p_args.command == "solve":
        from libs.data import read_schedule
        from libs.date import remove_morning_events
        from libs.display import print_solution
        from libs.interact import ask_events, ask_priorities
        from libs.solver import convert_binary_vector_to_pandas, solve

        data = remove_morning_events(read_schedule(p_args.input))
        choices = ask_events(data)
        priorities = ask_priorities(choices)
        x_star = solve(data, choices, priorities, p_args.max_num_events_per_day)

        if x_star is not None:
            x_star_df = convert_binary_vector_to_pandas(x_star, data)
            print_solution(x_star_df, choices, priorities)
