"""What every detector must offer, so the evaluation can treat them all the same way."""

from __future__ import annotations

from typing import Protocol

import pandas as pd


class Detector(Protocol):
    """A detector learns from normal data, then gives each time step an anomaly score.

    Higher score = more unusual. Turning scores into alarms (the threshold) is the
    evaluation's job, so every detector is compared with the same rule.
    """

    name: str

    def fit(self, train: pd.DataFrame) -> None:
        """Learn what normal looks like from the (scaled, fault-free) training part."""
        ...

    def score(self, values: pd.DataFrame) -> pd.Series[float]:
        """Return one anomaly score per row of values, with the same index."""
        ...
