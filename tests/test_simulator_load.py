"""Tests for the daily load profile."""

from __future__ import annotations

import numpy as np

from cellpulse.simulator.load import base_curve, bump, daily_load

STEPS_PER_DAY = 1440


def test_length() -> None:
    load = daily_load(7, 60, np.random.default_rng(42))
    assert len(load) == 7 * STEPS_PER_DAY


def test_values_stay_between_0_and_1() -> None:
    load = daily_load(7, 60, np.random.default_rng(42))
    assert load.min() >= 0
    assert load.max() <= 1


def test_same_seed_gives_same_load() -> None:
    first = daily_load(7, 60, np.random.default_rng(42))
    second = daily_load(7, 60, np.random.default_rng(42))
    assert np.array_equal(first, second)


def test_different_seed_gives_different_load() -> None:
    first = daily_load(7, 60, np.random.default_rng(1))
    second = daily_load(7, 60, np.random.default_rng(2))
    assert not np.array_equal(first, second)


def test_night_is_quieter_than_evening() -> None:
    load = daily_load(7, 60, np.random.default_rng(42))
    days = load.reshape(7, STEPS_PER_DAY)
    night = days[:, 2 * 60 : 5 * 60].mean()
    evening = days[:, 18 * 60 : 21 * 60].mean()
    assert night < evening


def test_bump_joins_smoothly_at_midnight() -> None:
    hours = np.array([0.0, 23.999])
    values = bump(hours, centre=23.0, height=0.5, width=2.5)
    assert abs(values[0] - values[1]) < 0.01


def test_weekday_morning_is_busier_than_weekend_morning() -> None:
    hours = np.array([8.5])
    weekday = base_curve(hours, np.array([False]))
    weekend = base_curve(hours, np.array([True]))
    assert weekday[0] > weekend[0]
