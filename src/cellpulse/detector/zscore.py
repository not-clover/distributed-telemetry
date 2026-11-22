"""Baseline detector: how far is each value from its own recent past?"""

from __future__ import annotations

import pandas as pd


class RollingZScore:
    """Rolling z-score per metric; the score of a time step is the largest one over all metrics.

    For every metric: z = (value now - mean of the last `window` steps) / spread of those steps.
    Only past steps are used, never the current or future ones.
    """

    name = "rolling_zscore"

    def __init__(self, window: int = 60, min_periods: int = 10, min_std: float = 0.1) -> None:
        self.window = window
        self.min_periods = min_periods
        self.min_std = min_std
        self.columns: list[str] = []

    def fit(self, train: pd.DataFrame) -> None:
        """Nothing to learn except which metrics to expect; the method only looks backwards."""
        self.columns = list(train.columns)

    def score(self, values: pd.DataFrame) -> pd.Series[float]:
        if list(values.columns) != self.columns:
            raise ValueError("score() got different metrics than fit()")
        past = values.rolling(self.window, min_periods=self.min_periods)
        mean = past.mean().shift(1)
        std = past.std().shift(1).clip(lower=self.min_std)
        z = (values - mean) / std
        return z.abs().max(axis=1).fillna(0.0)
