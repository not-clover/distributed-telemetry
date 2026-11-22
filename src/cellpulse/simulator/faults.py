"""Faults that can be injected into the simulated cells, and their ground truth."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from cellpulse.simulator.load import FloatArray

SLEEPING_CELL = "sleeping_cell"
MIN_MINUTES = 30
MAX_MINUTES = 240
MIN_SEVERITY = 0.6
MAX_SEVERITY = 1.0
GROUND_TRUTH_COLUMNS = ["kind", "cell_id", "start", "end", "severity"]


@dataclass(frozen=True)
class Fault:
    """One injected fault: what kind, which cell, when, and how strong."""

    kind: str
    cell_id: str
    start: pd.Timestamp
    end: pd.Timestamp
    severity: float


def apply_sleeping_cell(load: FloatArray, times: pd.DatetimeIndex, fault: Fault) -> FloatArray:
    """Return a copy of load where the cell loses a share (severity) of its load in the window."""
    in_window = (times >= fault.start) & (times < fault.end)
    result = load.copy()
    result[in_window] = result[in_window] * (1 - fault.severity)
    return result


def random_faults(
    n_faults: int, cell_ids: list[str], times: pd.DatetimeIndex, seed: int
) -> list[Fault]:
    """Place n_faults sleeping-cell faults at random in the second half of the time axis.

    Faults on the same cell never overlap. They use their own random generator,
    so adding faults does not change the normal data.
    """
    rng = np.random.default_rng([seed, 1])
    step = times[1] - times[0]
    first_step = len(times) // 2
    min_steps = pd.Timedelta(minutes=MIN_MINUTES) // step
    max_steps = pd.Timedelta(minutes=MAX_MINUTES) // step
    faults: list[Fault] = []
    attempts = 0
    while len(faults) < n_faults:
        attempts += 1
        if attempts > 100 * n_faults:
            raise ValueError("could not place all faults without overlap")
        cell_id = str(rng.choice(cell_ids))
        length = int(rng.integers(min_steps, max_steps + 1))
        start_step = int(rng.integers(first_step, len(times) - length + 1))
        severity = round(float(rng.uniform(MIN_SEVERITY, MAX_SEVERITY)), 2)
        start = times[start_step]
        fault = Fault(SLEEPING_CELL, cell_id, start, start + length * step, severity)
        overlaps = any(
            f.cell_id == cell_id and f.start < fault.end and fault.start < f.end for f in faults
        )
        if not overlaps:
            faults.append(fault)
    return sorted(faults, key=lambda f: f.start)


def ground_truth_table(faults: list[Fault]) -> pd.DataFrame:
    """Return one row per fault, to be saved next to the dataset (never inside it)."""
    return pd.DataFrame([asdict(f) for f in faults], columns=GROUND_TRUTH_COLUMNS)
