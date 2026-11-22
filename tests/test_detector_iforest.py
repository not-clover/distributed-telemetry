"""Tests for the Isolation Forest detector."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from cellpulse.detector.base import Detector
from cellpulse.detector.iforest import IsolationForestDetector, add_time_of_day

DAYS = 3
STEPS = DAYS * 24 * 60


def daily_metric(days: int = DAYS, seed: int = 0) -> pd.DataFrame:
    """One metric that is high in the afternoon and low at night, plus a little noise."""
    rng = np.random.default_rng(seed)
    times = pd.date_range("2026-01-05", periods=days * 24 * 60, freq="min", tz="UTC")
    hour = times.hour + times.minute / 60
    level = np.where((hour >= 10) & (hour < 20), 5.0, 1.0)
    noise = rng.normal(0, 0.2, len(times))
    return pd.DataFrame({"users": level + noise}, index=times)


def fitted(time_features: bool) -> IsolationForestDetector:
    detector = IsolationForestDetector(time_features=time_features)
    detector.fit(daily_metric())
    return detector


def test_follows_the_detector_protocol() -> None:
    detector: Detector = IsolationForestDetector()
    assert detector.name == "isolation_forest_time"
    assert IsolationForestDetector(time_features=False).name == "isolation_forest"


def test_one_score_per_step() -> None:
    values = daily_metric(days=1, seed=1)
    scores = fitted(True).score(values)
    assert scores.index.equals(values.index)
    assert scores.notna().all()


def test_time_of_day_is_circular() -> None:
    times = pd.DatetimeIndex(["2026-01-05 23:59", "2026-01-06 00:00", "2026-01-06 12:00"])
    features = add_time_of_day(pd.DataFrame({"x": [0.0, 0.0, 0.0]}, index=times))
    near_midnight = features.iloc[0] - features.iloc[1]
    across_day = features.iloc[0] - features.iloc[2]
    assert np.hypot(near_midnight["time_sin"], near_midnight["time_cos"]) < 0.01
    assert np.hypot(across_day["time_sin"], across_day["time_cos"]) > 1.9


def test_time_features_catch_a_night_like_afternoon() -> None:
    values = daily_metric(days=1, seed=2)
    afternoon = (values.index.hour >= 14) & (values.index.hour < 16)
    values.loc[afternoon, "users"] = 1.0
    night = values.index.hour == 3
    with_time = fitted(True).score(values)
    without_time = fitted(False).score(values)
    assert with_time[afternoon].mean() > with_time[night].mean() + 0.05
    assert without_time[afternoon].mean() <= without_time[night].mean()


def test_needs_a_time_index_for_time_features() -> None:
    with pytest.raises(ValueError, match="time index"):
        add_time_of_day(pd.DataFrame({"x": [1.0, 2.0]}))


def test_rejects_different_metrics() -> None:
    values = daily_metric(days=1)
    values["extra"] = 0.0
    with pytest.raises(ValueError, match="different metrics"):
        fitted(False).score(values)
