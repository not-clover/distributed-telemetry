"""Tests for the detector data loader: series per cell, labels, time split and scaling."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cellpulse.detector.data import Scaler, Series, load_simulated, prepare, split_by_time
from cellpulse.simulator.__main__ import main

DAYS = 4
STEPS = DAYS * 24 * 60
KPIS = 8


@pytest.fixture
def dataset(tmp_path: Path) -> tuple[Path, Path]:
    """Write a small 4-day dataset with 3 faults, like cellpulse-simulate does."""
    data_path = tmp_path / "small.parquet"
    main(["--days", str(DAYS), "--seed", "5", "--faults", "3", "--out", str(data_path)])
    return data_path, tmp_path / "small_ground_truth.csv"


def test_one_series_per_cell(dataset: tuple[Path, Path]) -> None:
    series = load_simulated(*dataset)
    assert len(series) == 12
    for s in series:
        assert s.values.shape == (STEPS, KPIS)
        assert "cell_id" not in s.values.columns
        assert s.values.index.is_monotonic_increasing
        assert s.labels.index.equals(s.values.index)


def test_labels_match_ground_truth(dataset: tuple[Path, Path]) -> None:
    series = load_simulated(*dataset)
    truth = pd.read_csv(dataset[1], parse_dates=["start", "end"])
    fault_minutes = ((truth["end"] - truth["start"]) / pd.Timedelta(minutes=1)).sum()
    assert sum(int(s.labels.sum()) for s in series) == fault_minutes


def test_no_ground_truth_means_no_faults(dataset: tuple[Path, Path]) -> None:
    series = load_simulated(dataset[0])
    assert not any(s.labels.any() for s in series)


def test_split_is_in_time_order(dataset: tuple[Path, Path]) -> None:
    split = split_by_time(load_simulated(*dataset)[0])
    assert len(split.train.values) == STEPS // 2
    assert len(split.tune.values) == STEPS // 4
    assert len(split.test.values) == STEPS // 4
    assert split.train.values.index.max() < split.tune.values.index.min()
    assert split.tune.values.index.max() < split.test.values.index.min()


def test_faults_in_training_part_are_rejected() -> None:
    times = pd.date_range("2026-01-05", periods=8, freq="min", tz="UTC")
    labels = pd.Series([True] + [False] * 7, index=times)
    series = Series("bad", pd.DataFrame({"x": np.arange(8.0)}, index=times), labels)
    with pytest.raises(ValueError, match="training part contains faults"):
        split_by_time(series)


def test_scaler_uses_training_numbers_only(dataset: tuple[Path, Path]) -> None:
    series = load_simulated(*dataset)[0]
    split = prepare(series)
    train = split.train.values
    assert np.allclose(train.mean(), 0, atol=1e-9)
    assert np.allclose(train.std(), 1)
    raw_test = split_by_time(series).test.values
    expected = Scaler.fit(split_by_time(series).train.values).transform(raw_test)
    pd.testing.assert_frame_equal(split.test.values, expected)


def test_constant_metric_does_not_divide_by_zero() -> None:
    values = pd.DataFrame({"flat": [3.0] * 4, "moving": [1.0, 2.0, 3.0, 4.0]})
    scaled = Scaler.fit(values).transform(values)
    assert np.isfinite(scaled.to_numpy()).all()
    assert (scaled["flat"] == 0).all()
