"""Tests for the rolling z-score baseline detector."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from cellpulse.detector.base import Detector
from cellpulse.detector.zscore import RollingZScore

STEPS = 300


def noisy_metrics(seed: int = 0) -> pd.DataFrame:
    """Two metrics of plain noise around 0, one row per minute."""
    rng = np.random.default_rng(seed)
    times = pd.date_range("2026-01-05", periods=STEPS, freq="min", tz="UTC")
    return pd.DataFrame(rng.normal(0, 1, size=(STEPS, 2)), index=times, columns=["a", "b"])


def fitted(values: pd.DataFrame) -> RollingZScore:
    detector = RollingZScore(window=60)
    detector.fit(values)
    return detector


def test_follows_the_detector_protocol() -> None:
    detector: Detector = RollingZScore()
    assert detector.name == "rolling_zscore"


def test_one_score_per_step_and_no_gaps() -> None:
    values = noisy_metrics()
    scores = fitted(values).score(values)
    assert scores.index.equals(values.index)
    assert scores.notna().all()
    assert (scores >= 0).all()


def test_sudden_drop_scores_high() -> None:
    values = noisy_metrics()
    values.iloc[200:, 0] -= 8
    scores = fitted(noisy_metrics()).score(values)
    assert scores.iloc[200] > 5
    assert scores.iloc[100:199].max() < scores.iloc[200]


def test_does_not_look_into_the_future() -> None:
    values = noisy_metrics()
    changed = values.copy()
    changed.iloc[250:] += 100
    detector = fitted(values)
    pd.testing.assert_series_equal(detector.score(values)[:250], detector.score(changed)[:250])


def test_flat_metric_does_not_explode() -> None:
    values = noisy_metrics()[["b"]] * 0
    values.iloc[150, 0] = 0.01
    assert fitted(values).score(values).iloc[150] == pytest.approx(0.1)


def test_rejects_different_metrics() -> None:
    detector = fitted(noisy_metrics())
    with pytest.raises(ValueError, match="different metrics"):
        detector.score(noisy_metrics()[["b", "a"]])
