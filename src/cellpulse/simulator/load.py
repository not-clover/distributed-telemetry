"""Daily load profile for one simulated cell.

Load is a hidden number from 0 (empty cell) to 1 (full cell). It follows a daily
curve (baseline plus bell-shaped bumps) with drifting noise on top.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def bump(hours: FloatArray, centre: float, height: float, width: float) -> FloatArray:
    """Return one bell-shaped bump evaluated at each hour of day (0 to 24).

    Distance to the centre is measured around the clock, so 23:00 and 01:00
    are both one hour from midnight.
    """
    distance = np.abs(hours - centre)
    distance = np.minimum(distance, 24 - distance)
    result: FloatArray = height * np.exp(-((distance / width) ** 2) / 2)
    return result


BASELINE = 0.12


def base_curve(hours: FloatArray, is_weekend: NDArray[np.bool_]) -> FloatArray:
    """Return the noise-free load for each time step: baseline plus bumps."""
    morning = bump(hours, 8.5, 0.25, 1.5)
    lunch = bump(hours, 13.0, 0.20, 1.5)
    evening = bump(hours, 19.5, 0.50, 2.5)
    afternoon = bump(hours, 15.0, 0.40, 4.0)
    weekday = BASELINE + morning + lunch + evening
    weekend = BASELINE + afternoon
    result: FloatArray = np.where(is_weekend, weekend, weekday)
    return result


KEEP = 0.95
STEP_STD = 0.01


def drifting_noise(n: int, rng: np.random.Generator) -> FloatArray:
    """Return n values of AR(1) noise: 0.95 of the previous value plus a small random step."""
    steps = rng.normal(0, STEP_STD, size=n)
    noise = np.zeros(n)
    noise[0] = steps[0]
    for i in range(1, n):
        noise[i] = KEEP * noise[i - 1] + steps[i]
    return noise


def daily_load(n_days: int, interval_s: int, rng: np.random.Generator) -> FloatArray:
    """Return one load value in [0, 1] per time step for n_days days, starting on a Monday."""
    raise NotImplementedError
