"""Tests for saving the simulated dataset to Parquet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from cellpulse.simulator.__main__ import main
from cellpulse.simulator.dataset import simulate


def test_export_round_trip(tmp_path: Path) -> None:
    out = tmp_path / "test.parquet"
    exit_code = main(["--days", "2", "--seed", "7", "--out", str(out)])
    assert exit_code == 0
    expected = simulate(n_days=2, interval_s=60, seed=7)
    result = pd.read_parquet(out)
    pd.testing.assert_frame_equal(result, expected)
