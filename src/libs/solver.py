import logging

import cvxpy as cp
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def get_user_choice_vector(data: pd.DataFrame, user_choices: list[str]) -> np.ndarray:
    """Return the user choice vector (referred as `c`) as an `np.array`.

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the scheduile
    user_choices : list[str]
        List of string containing the event names chose by the user

    Returns
    -------
    np.ndarray
        User choice vector

    """
    result = np.array(data["event"].isin(user_choices), dtype=bool)
    return result


def get_event_matrix(data: pd.DataFrame) -> np.ndarray:
    """Return the event matrix (referred as `E`).

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the schedule

    Returns
    -------
    np.ndarray
        Event matrix

    """
    result = np.array(data[["start", "end"]])
    return result


def convert_solution_to_pandas(x_star: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
    """Convert the solution to a `pd.Dataframe`

    Parameters
    ----------
    x_star : np.ndarray
        Solution found by the solver
    data : pd.DataFrame
        Data containing the schedule

    Returns
    -------
    pd.DataFrame
        Solution as a `pd.DataFrame`

    """
    result = data[x_star.astype(bool)]
    return result  # type: ignore


def init_x(dim: int) -> cp.Variable:
    """Return the variable object to optimize.

    Parameters
    ----------
    dim : int
        Dimension of the vector

    Returns
    -------
    cp.Variable
        Object to optimize

    """
    return cp.Variable(dim, boolean=True)


def init_y(dim: int) -> cp.Variable:
    """Return the slack variable object for inequalities.

    Parameters
    ----------
    dim : int
        Dimension of the square matrix

    Returns
    -------
    cp.Variable
        Slack variable matrix

    """
    return cp.Variable((dim, dim), boolean=True)


def get_inequality_non_overlap(
    x: cp.Variable, y: cp.Variable, e: np.ndarray, upper_bound_value: int = int(2e9)
) -> list[cp.Constraint]:
    """Return the list of inequalities to have non overlapping events.

    Parameters
    ----------
    x : cp.Variable
        Variable to optimize
    y : cp.Variable
        Slack variable to optimize
    e : np.ndarray
        Event matrix
    upper_bound_value : int
        Upper bound value

    Returns
    -------
    list[cp.Constraint]
        List of inequality constraints

    """
    num_events = x.size
    x_hadamard_e = cp.multiply(cp.vstack((x, x)).T, e)

    ineq_non_overlap_first = [
        x_hadamard_e[i, 1] <= x_hadamard_e[j, 0] + y[i, j] * upper_bound_value
        for i in range(num_events)
        for j in range(num_events)
        if i > j
    ]
    ineq_non_overlap_second = [
        x_hadamard_e[j, 1] <= x_hadamard_e[i, 0] + (1 - y[i, j]) * upper_bound_value
        for i in range(num_events)
        for j in range(num_events)
        if i > j
    ]
    ineqs = ineq_non_overlap_first + ineq_non_overlap_second

    return ineqs  # type: ignore


def get_inequality_same_event(
    x: cp.Variable, data: pd.DataFrame
) -> list[cp.Constraint]:
    """Return the list of inequalities to attend an event only once at best.

    Parameters
    ----------
    x : cp.Variable
        Variable to optimize
    data : pd.DataFrame
        Data containing the schedule

    Returns
    -------
    list[cp.Constraint]
        List of inequality constraints

    """
    event_names = data["event"].unique()
    ineqs = [cp.sum(x[data["event"] == event_name]) <= 1 for event_name in event_names]

    return ineqs  # type: ignore


def solve(data: pd.DataFrame, user_choices: list[str]) -> np.ndarray:
    """Solve the optimization problem

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the schedule
    user_choices : list[str]
        List of events the user want to attend

    Returns
    -------
    np.ndarray
        Optimal solution

    """
    c = get_user_choice_vector(data, user_choices)
    e = get_event_matrix(data)

    num_events = c.size
    x = init_x(num_events)
    y = init_y(num_events)

    objective = cp.Maximize(cp.vdot(x.T, c))

    i_1 = get_inequality_non_overlap(x, y, e)
    i_2 = get_inequality_same_event(x, data)
    prob = cp.Problem(objective, i_1 + i_2)
    result = prob.solve()

    log.debug(f"Optimal value is {result}")
    log.debug(f"Optimal variable is {x.value}")
    log.debug(f"Optimal slack variable is {y.value}")

    return x.value  # type: ignore
