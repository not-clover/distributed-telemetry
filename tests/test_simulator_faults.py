"""Tests for the sleeping-cell fault and its ground truth."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cellpulse.simulator.__main__ import main
from cellpulse.simulator.dataset import cell_ids, simulate, time_axis
from cellpulse.simulator.faults import (
    GROUND_TRUTH_COLUMNS,
    SLEEPING_CELL,
    Fault,
    ground_truth_table,
    random_faults,
)

CELL = "site-a/cell-001"
START = pd.Timestamp("2026-01-06 14:00", tz="UTC")
END = pd.Timestamp("2026-01-06 16:00", tz="UTC")


def test_only_the_fault_window_changes() -> None:
    fault = Fault(SLEEPING_CELL, CELL, START, END, 0.8)
    normal = simulate(n_days=2, interval_s=60, seed=3)
    faulty = simulate(n_days=2, interval_s=60, seed=3, faults=[fault])
    changed = (normal != faulty).any(axis=1)
    assert changed.sum() == 120
    window = (faulty["cell_id"] == CELL) & (faulty["observed_at"] >= START)
    window &= faulty["observed_at"] < END
    assert (changed == window).all()
    assert (faulty.loc[window, "active_ues"] < normal.loc[window, "active_ues"]).all()
    assert (
        faulty.loc[window, "prb_utilisation_pct"] < normal.loc[window, "prb_utilisation_pct"]
    ).all()
    for kpi in ("rrc_success_rate_pct", "call_drop_rate_pct", "sinr_db"):
        pd.testing.assert_series_equal(faulty[kpi], normal[kpi])


def test_random_faults_follow_the_rules() -> None:
    times = time_axis(n_days=28, interval_s=60)
    faults = random_faults(30, cell_ids(), times, seed=42)
    assert len(faults) == 30
    for fault in faults:
        assert fault.start >= times[len(times) // 2]
        assert fault.end <= times[-1] + pd.Timedelta(minutes=1)
        assert pd.Timedelta(minutes=30) <= fault.end - fault.start <= pd.Timedelta(hours=4)
        assert 0.6 <= fault.severity <= 1.0
    for a in faults:
        for b in faults:
            if a is not b and a.cell_id == b.cell_id:
                assert a.end <= b.start or b.end <= a.start
    assert random_faults(30, cell_ids(), times, seed=42) == faults


def test_too_many_faults_raise_an_error() -> None:
    times = pd.date_range("2026-01-05", periods=600, freq="60s", tz="UTC")
    with pytest.raises(ValueError, match="could not place"):
        random_faults(20, ["only-cell"], times, seed=1)


def test_faults_do_not_change_normal_data_randomness() -> None:
    times = time_axis(n_days=2, interval_s=60)
    faults = random_faults(5, cell_ids(), times, seed=3)
    normal = simulate(n_days=2, interval_s=60, seed=3)
    faulty = simulate(n_days=2, interval_s=60, seed=3, faults=faults)
    pd.testing.assert_series_equal(faulty["sinr_db"], normal["sinr_db"])
    assert list(faulty.columns) == list(normal.columns)


def test_ground_truth_table() -> None:
    fault = Fault(SLEEPING_CELL, CELL, START, END, 0.8)
    table = ground_truth_table([fault])
    assert list(table.columns) == GROUND_TRUTH_COLUMNS
    assert table.loc[0, "cell_id"] == CELL
    assert list(ground_truth_table([]).columns) == GROUND_TRUTH_COLUMNS


def test_cli_writes_ground_truth_file(tmp_path: Path) -> None:
    out = tmp_path / "faulty.parquet"
    assert main(["--days", "2", "--faults", "3", "--out", str(out)]) == 0
    truth = pd.read_csv(tmp_path / "faulty_ground_truth.csv")
    assert len(truth) == 3
    assert list(truth.columns) == GROUND_TRUTH_COLUMNS
    assert "kind" not in pd.read_parquet(out).columns
