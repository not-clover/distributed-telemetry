"""Isolation Forest detector: how easy is it to separate this time step from normal ones?"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

MINUTES_PER_DAY = 24 * 60


def add_time_of_day(values: pd.DataFrame) -> pd.DataFrame:
    """Add the time of day as two columns (sine and cosine), so 23:59 and 00:00 end up close."""
    if not isinstance(values.index, pd.DatetimeIndex):
        raise ValueError("time-of-day features need a time index")
    minutes = values.index.hour * 60 + values.index.minute
    angle = 2 * np.pi * minutes / MINUTES_PER_DAY
    result = values.copy()
    result["time_sin"] = np.sin(angle)
    result["time_cos"] = np.cos(angle)
    return result


class IsolationForestDetector:
    """scikit-learn's Isolation Forest, trained on normal data, all metrics together.

    Each row is scored on its own: the forest does not know what came before it.
    With time_features=True it also gets the time of day, so it can learn that
    few users is normal at night but not in the afternoon.
    """

    def __init__(self, time_features: bool = True, n_trees: int = 100, seed: int = 0) -> None:
        self.time_features = time_features
        self.name = "isolation_forest_time" if time_features else "isolation_forest"
        self.model = IsolationForest(n_estimators=n_trees, random_state=seed)
        self.columns: list[str] = []

    def _features(self, values: pd.DataFrame) -> pd.DataFrame:
        return add_time_of_day(values) if self.time_features else values

    def fit(self, train: pd.DataFrame) -> None:
        self.columns = list(train.columns)
        self.model.fit(self._features(train).to_numpy())

    def score(self, values: pd.DataFrame) -> pd.Series[float]:
        if list(values.columns) != self.columns:
            raise ValueError("score() got different metrics than fit()")
        normality = self.model.score_samples(self._features(values).to_numpy())
        return pd.Series(-normality, index=values.index, dtype="float64")
