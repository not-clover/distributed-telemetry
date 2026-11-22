"""Build the full dataset: every cell, every time step."""

from __future__ import annotations

import numpy as np
import pandas as pd

from cellpulse.simulator.faults import SLEEPING_CELL, Fault, apply_sleeping_cell
from cellpulse.simulator.kpis import cell_kpis
from cellpulse.simulator.load import SECONDS_PER_DAY, daily_load

START = "2026-01-05 00:00"
SITE_LETTERS = "abcdefgh"


def cell_ids(n_sites: int = 3, cells_per_site: int = 4) -> list[str]:
    """Return the names of all cells, e.g. 'site-a/cell-001'."""
    return [
        f"site-{SITE_LETTERS[site]}/cell-{cell + 1:03d}"
        for site in range(n_sites)
        for cell in range(cells_per_site)
    ]


def time_axis(n_days: int, interval_s: int) -> pd.DatetimeIndex:
    """Return the timestamps of every step, starting at START (UTC)."""
    periods = n_days * SECONDS_PER_DAY // interval_s
    return pd.date_range(START, periods=periods, freq=f"{interval_s}s", tz="UTC")


def simulate(
    n_days: int,
    interval_s: int,
    seed: int,
    n_sites: int = 3,
    cells_per_site: int = 4,
    faults: list[Fault] | None = None,
) -> pd.DataFrame:
    """Return one row per cell per time step with the eight KPIs, with optional faults."""
    rng = np.random.default_rng(seed)
    times = time_axis(n_days, interval_s)
    frames = []
    for cell_id in cell_ids(n_sites, cells_per_site):
        max_ues = int(rng.integers(150, 300))
        sinr_mean = float(rng.uniform(10, 20))
        busyness = float(rng.uniform(0.8, 1.2))
        load = np.clip(daily_load(n_days, interval_s, rng) * busyness, 0, 1)
        for fault in faults or []:
            if fault.cell_id == cell_id and fault.kind == SLEEPING_CELL:
                load = apply_sleeping_cell(load, times, fault)
        frame = pd.DataFrame(cell_kpis(load, max_ues, sinr_mean, rng))
        frame.insert(0, "cell_id", cell_id)
        frame.insert(1, "observed_at", times)
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    result["active_ues"] = result["active_ues"].astype("uint32")
    return result
