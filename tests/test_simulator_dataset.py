"""Tests for the KPI formulas and the simulated dataset."""

from __future__ import annotations

import numpy as np

from cellpulse.simulator.dataset import simulate
from cellpulse.simulator.kpis import ideal_kpis

KPI_COLUMNS = [
    "dl_throughput_mbps",
    "ul_throughput_mbps",
    "prb_utilisation_pct",
    "latency_ms",
    "active_ues",
    "call_drop_rate_pct",
    "rrc_success_rate_pct",
    "sinr_db",
]


def test_shape_and_columns() -> None:
    df = simulate(2, 60, seed=42)
    assert len(df) == 2 * 1440 * 12
    assert list(df.columns) == ["cell_id", "observed_at", *KPI_COLUMNS]


def test_twelve_different_cells() -> None:
    df = simulate(1, 60, seed=42)
    assert df["cell_id"].nunique() == 12


def test_same_seed_gives_same_dataset() -> None:
    first = simulate(1, 60, seed=42)
    second = simulate(1, 60, seed=42)
    assert first.equals(second)


def test_different_seed_gives_different_dataset() -> None:
    first = simulate(1, 60, seed=1)
    second = simulate(1, 60, seed=2)
    assert not first.equals(second)


def test_percentages_stay_between_0_and_100() -> None:
    df = simulate(2, 60, seed=42)
    for name in ("prb_utilisation_pct", "call_drop_rate_pct", "rrc_success_rate_pct"):
        assert df[name].between(0, 100).all()


def test_busier_cell_is_slower_and_more_delayed() -> None:
    kpis = ideal_kpis(np.array([0.2, 0.8]), max_ues=200)
    assert kpis["dl_throughput_mbps"][0] > kpis["dl_throughput_mbps"][1]
    assert kpis["latency_ms"][0] < kpis["latency_ms"][1]


def test_rates_only_move_when_overloaded() -> None:
    kpis = ideal_kpis(np.array([0.3, 0.6, 1.0]), max_ues=200)
    rrc = kpis["rrc_success_rate_pct"]
    assert rrc[0] == rrc[1]
    assert rrc[2] < rrc[1]
