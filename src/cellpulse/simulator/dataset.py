"""Build the full dataset: every cell, every time step."""

from __future__ import annotations

import numpy as np
import pandas as pd

from cellpulse.simulator.kpis import cell_kpis
from cellpulse.simulator.load import daily_load

START = "2026-01-05 00:00"
SITE_LETTERS = "abcdefgh"


def simulate(
    n_days: int, interval_s: int, seed: int, n_sites: int = 3, cells_per_site: int = 4
) -> pd.DataFrame:
    """Return one row per cell per time step with the eight KPIs."""
    rng = np.random.default_rng(seed)
    frames = []
    for site in range(n_sites):
        for cell in range(cells_per_site):
            max_ues = int(rng.integers(150, 300))
            sinr_mean = float(rng.uniform(10, 20))
            busyness = float(rng.uniform(0.8, 1.2))
            load = np.clip(daily_load(n_days, interval_s, rng) * busyness, 0, 1)
            frame = pd.DataFrame(cell_kpis(load, max_ues, sinr_mean, rng))
            frame.insert(0, "cell_id", f"site-{SITE_LETTERS[site]}/cell-{cell + 1:03d}")
            times = pd.date_range(START, periods=len(load), freq=f"{interval_s}s", tz="UTC")
            frame.insert(1, "observed_at", times)
            frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    result["active_ues"] = result["active_ues"].astype("uint32")
    return result
