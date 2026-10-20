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


def convert_binary_vector_to_pandas(x: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
    """Convert a binary vector to a `pd.Dataframe`

    Parameters
    ----------
    x : np.ndarray
        Binary vector
    data : pd.DataFrame
        Data containing the schedule

    Returns
    -------
    pd.DataFrame
        Solution as a `pd.DataFrame`

    """
    result = data[x.astype(bool)]
    return result  # type: ignore


def get_compacter_indices(c: np.ndarray) -> list[int]:
    """Return indices to transform a vector to a compact one.
    The compact vector has elements where `c` is equal to 1.

    Parameters
    ----------
    c : np.ndarray
        User choice vector

    Returns
    -------
    list[int]
        Indices where `c` is equal to 1

    """
    indices = [i for i, x in enumerate(c) if x == 1]

    return indices


def compact_vector(x: np.ndarray, compact_indices: list[int]) -> np.ndarray:
    """Transform a vector to the compact version.

    Parameters
    ----------
    x : np.ndarray
        Vector to transform
    compact_indices : list[int]
        Indices coming from `get_compacter_indices`

    Returns
    -------
    np.ndarray
        Compact version of the vector `x`

    """
    result = np.array([e for i, e in enumerate(x) if i in compact_indices])

    return result


def uncompact_vector(
    x_tilde: np.ndarray, compact_indices: list[int], dim: int
) -> np.ndarray:
    """Transform the compact vector back to its original form.

    Parameters
    ----------
    x_tilde : np.ndarray
        Compact vector to transform back
    compact_indices : list[int]
        Indices coming from `get_compacter_indices`
    dim : int
        Original dimension of the vector

    Returns
    -------
    np.ndarray
        Vector in the original form

    """
    uncompact_indices = {x: i for i, x in enumerate(compact_indices)}

    result = []
    for i in range(dim):
        if i in compact_indices:
            result.append(x_tilde[uncompact_indices[i]])
        else:
            result.append(0)

    return np.array(result)


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
    if len(user_choices) == 0:
        return np.array([])

    c = get_user_choice_vector(data, user_choices)
    init_dim = c.size

    compact_indices = get_compacter_indices(c)
    c_tilde = compact_vector(c, compact_indices)

    num_events = c_tilde.size
    x_tilde = init_x(num_events)
    y_tilde = init_y(num_events)
    data_tilde = convert_binary_vector_to_pandas(c, data)
    e_tilde = get_event_matrix(data_tilde)

    objective = cp.Maximize(cp.vdot(x_tilde.T, c_tilde))

    i_1 = get_inequality_non_overlap(x_tilde, y_tilde, e_tilde)
    i_2 = get_inequality_same_event(x_tilde, data_tilde)
    prob = cp.Problem(objective, i_1 + i_2)
    result = prob.solve()

    log.debug(f"Optimal value is {result}")

    x_star = uncompact_vector(x_tilde.value, compact_indices, init_dim)  # type: ignore
    log.debug(f"Optimal variable is {x_star}")

    return x_star
