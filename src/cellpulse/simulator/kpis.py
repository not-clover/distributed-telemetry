"""Turn the hidden load into the eight KPIs of one cell."""

from __future__ import annotations

import numpy as np

from cellpulse.simulator.load import FloatArray, drifting_noise

OVERLOAD_START = 0.85


def ideal_kpis(load: FloatArray, max_ues: int) -> dict[str, FloatArray]:
    """Return the seven load-driven KPIs with no measurement noise. It is the translator."""
    overload = np.clip((load - OVERLOAD_START) / (1 - OVERLOAD_START), 0, 1)
    dl_throughput = 100 - 80 * load
    return {
        "dl_throughput_mbps": dl_throughput,
        "ul_throughput_mbps": dl_throughput / 2,
        "prb_utilisation_pct": 5 + 90 * load,
        "latency_ms": 5 + 15 * load**4,
        "active_ues": np.round(load * max_ues),
        "call_drop_rate_pct": 0.3 + 2.7 * overload,
        "rrc_success_rate_pct": 99.5 - 4.5 * overload,
    }


def cell_kpis(
    load: FloatArray, max_ues: int, sinr_mean: float, rng: np.random.Generator
) -> dict[str, FloatArray]:
    """Return all eight KPIs for one cell, with measurement noise."""
    n = len(load)
    kpis = ideal_kpis(load, max_ues)
    for name in ("dl_throughput_mbps", "ul_throughput_mbps", "prb_utilisation_pct", "latency_ms"):
        kpis[name] = kpis[name] * (1 + rng.normal(0, 0.03, size=n))
    kpis["call_drop_rate_pct"] = kpis["call_drop_rate_pct"] + rng.normal(0, 0.05, size=n)
    kpis["rrc_success_rate_pct"] = kpis["rrc_success_rate_pct"] + rng.normal(0, 0.1, size=n)
    kpis["sinr_db"] = sinr_mean + 50 * drifting_noise(n, rng)
    for name in ("prb_utilisation_pct", "call_drop_rate_pct", "rrc_success_rate_pct"):
        kpis[name] = np.clip(kpis[name], 0, 100)
    return kpis
