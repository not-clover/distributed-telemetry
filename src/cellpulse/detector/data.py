"""Load a dataset for the detectors: one table per series, split by time, scaled."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ID_COLUMN = "cell_id"
TIME_COLUMN = "observed_at"


@dataclass(frozen=True)
class Series:
    """One monitored thing (a cell, later an SMD machine) over time.

    values: rows are time steps, columns are metrics. labels: True where a fault was injected.
    The labels are only for evaluation; detectors must never see them.
    """

    name: str
    values: pd.DataFrame
    labels: pd.Series[bool]


@dataclass(frozen=True)
class Split:
    """The three time-ordered parts of one series."""

    train: Series
    tune: Series
    test: Series


@dataclass(frozen=True)
class Scaler:
    """Rescales every metric to mean 0 and spread 1, using numbers learned from training data."""

    mean: pd.Series[float]
    std: pd.Series[float]

    @classmethod
    def fit(cls, values: pd.DataFrame) -> Scaler:
        """Learn the mean and spread of each metric. Call this on the training part only."""
        std = values.std()
        std[std == 0] = 1.0
        return cls(mean=values.mean(), std=std)

    def transform(self, values: pd.DataFrame) -> pd.DataFrame:
        """Apply the learned mean and spread to any part (train, tune or test)."""
        return (values - self.mean) / self.std


def fault_labels(times: pd.DatetimeIndex, truth: pd.DataFrame, name: str) -> pd.Series[bool]:
    """Turn the fault intervals of one series into True/False for each time step."""
    labels = pd.Series(False, index=times)
    faults = truth[truth[ID_COLUMN] == name]
    for start, end in zip(faults["start"], faults["end"], strict=True):
        labels[(times >= start) & (times < end)] = True
    return labels


def load_simulated(data_path: Path, truth_path: Path | None = None) -> list[Series]:
    """Read the simulated Parquet dataset (and its ground truth, if any) as one series per cell."""
    df = pd.read_parquet(data_path)
    if truth_path is None:
        truth = pd.DataFrame(columns=[ID_COLUMN, "start", "end"])
    else:
        truth = pd.read_csv(truth_path)
        truth["start"] = pd.to_datetime(truth["start"], utc=True)
        truth["end"] = pd.to_datetime(truth["end"], utc=True)
    series = []
    for name, group in df.groupby(ID_COLUMN, sort=True):
        values = group.drop(columns=ID_COLUMN).set_index(TIME_COLUMN).sort_index()
        values = values.astype("float64")
        times = pd.DatetimeIndex(values.index)
        series.append(Series(str(name), values, fault_labels(times, truth, str(name))))
    return series


def _part(series: Series, start: int, stop: int) -> Series:
    """Return the rows from position start up to (not including) stop."""
    return Series(series.name, series.values.iloc[start:stop], series.labels.iloc[start:stop])


def split_by_time(series: Series, train: float = 0.5, tune: float = 0.25) -> Split:
    """Cut a series into train, tune and test parts in time order (never shuffled)."""
    n = len(series.values)
    train_end = int(n * train)
    tune_end = int(n * (train + tune))
    split = Split(
        train=_part(series, 0, train_end),
        tune=_part(series, train_end, tune_end),
        test=_part(series, tune_end, n),
    )
    if split.train.labels.any():
        raise ValueError(f"{series.name}: the training part contains faults; it must be normal")
    return split


def prepare(series: Series, train: float = 0.5, tune: float = 0.25) -> Split:
    """Split a series by time, then scale all parts with a scaler fitted on the training part."""
    split = split_by_time(series, train, tune)
    scaler = Scaler.fit(split.train.values)

    def scaled(part: Series) -> Series:
        return Series(part.name, scaler.transform(part.values), part.labels)

    return Split(scaled(split.train), scaled(split.tune), scaled(split.test))
