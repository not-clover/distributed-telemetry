"""Turn the hidden load into the eight KPIs of one cell."""

from __future__ import annotations

import numpy as np

from cellpulse.simulator.load import FloatArray

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
