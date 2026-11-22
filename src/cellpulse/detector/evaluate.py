"""Compare detectors fairly: same data, same threshold rule, event-level metrics.

For every detector and every series (cell):
1. fit on the training part (normal data only),
2. threshold = a quantile of its own training scores; the quantile is chosen on the
   tune part from a fixed list, by best event-level F1 (same rule for every detector),
3. report on the test part, which is never used for any choice.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd

from cellpulse.detector.base import Detector
from cellpulse.detector.data import Split, load_simulated, prepare
from cellpulse.detector.iforest import IsolationForestDetector
from cellpulse.detector.zscore import RollingZScore

BoolArray = npt.NDArray[np.bool_]
FloatArray = npt.NDArray[np.floating[Any]]

STEPS_PER_DAY = 24 * 60  # both datasets have one reading per minute
QUANTILES = (0.99, 0.995, 0.999, 0.9995, 0.9999)
NIGHT_START, NIGHT_END = 23, 7  # faults starting 23:00-06:59 count as night faults

DETECTORS: dict[str, Callable[[], Detector]] = {
    "rolling_zscore": RollingZScore,
    "isolation_forest": lambda: IsolationForestDetector(time_features=False),
    "isolation_forest_time": lambda: IsolationForestDetector(time_features=True),
}


def events(flags: BoolArray) -> list[tuple[int, int]]:
    """Group consecutive True steps into events: (first position, position after the last)."""
    edges = np.diff(np.concatenate([[0], flags.astype(np.int8), [0]]))
    starts = np.flatnonzero(edges == 1).tolist()
    ends = np.flatnonzero(edges == -1).tolist()
    return list(zip(starts, ends, strict=True))


@dataclass
class Counts:
    """Event-level tallies, added up over all series."""

    faults: int = 0
    detected: int = 0
    night_faults: int = 0
    night_detected: int = 0
    alarms: int = 0
    true_alarms: int = 0
    days: float = 0.0
    delays: list[int] = field(default_factory=list)

    def add(self, alarms: BoolArray, labels: BoolArray, times: pd.DatetimeIndex) -> None:
        """Compare one series' alarms with its true labels."""
        for start, end in events(labels):
            hits = np.flatnonzero(alarms[start:end])
            is_night = times[start].hour >= NIGHT_START or times[start].hour < NIGHT_END
            self.faults += 1
            self.night_faults += is_night
            if len(hits) > 0:
                self.detected += 1
                self.night_detected += is_night
                self.delays.append(int(hits[0]))
        for start, end in events(alarms):
            self.alarms += 1
            self.true_alarms += bool(labels[start:end].any())
        self.days += len(labels) / STEPS_PER_DAY

    @property
    def recall(self) -> float:
        return self.detected / self.faults if self.faults else 0.0

    @property
    def precision(self) -> float:
        return self.true_alarms / self.alarms if self.alarms else 0.0

    @property
    def f1(self) -> float:
        total = self.precision + self.recall
        return 2 * self.precision * self.recall / total if total else 0.0

    @property
    def false_alarms_per_day(self) -> float:
        return (self.alarms - self.true_alarms) / self.days if self.days else 0.0


@dataclass(frozen=True)
class Scored:
    """One series after scoring: scores for each part, plus what the test needs."""

    train: FloatArray
    tune: FloatArray
    test: FloatArray
    split: Split


def score_series(make: Callable[[], Detector], split: Split) -> Scored:
    """Fit a fresh detector on the training part and score all three parts."""
    detector = make()
    detector.fit(split.train.values)
    return Scored(
        train=detector.score(split.train.values).to_numpy(),
        tune=detector.score(split.tune.values).to_numpy(),
        test=detector.score(split.test.values).to_numpy(),
        split=split,
    )


def count(scored: Sequence[Scored], quantile: float, part: str) -> Counts:
    """Turn scores into alarms with each series' own threshold and tally the events."""
    counts = Counts()
    for s in scored:
        threshold = np.quantile(s.train, quantile)
        scores = s.tune if part == "tune" else s.test
        labels = s.split.tune.labels if part == "tune" else s.split.test.labels
        counts.add(scores > threshold, labels.to_numpy(), pd.DatetimeIndex(labels.index))
    return counts


@dataclass(frozen=True)
class Result:
    detector: str
    quantile: float
    test: Counts

    def row(self) -> dict[str, str]:
        t = self.test
        delay = f"{np.median(t.delays):.0f}" if t.delays else "-"
        return {
            "Detector": self.detector,
            "Threshold (train quantile)": f"{self.quantile:g}",
            "Faults caught": f"{t.detected}/{t.faults}",
            "Day": f"{t.detected - t.night_detected}/{t.faults - t.night_faults}",
            "Night": f"{t.night_detected}/{t.night_faults}",
            "Precision": f"{t.precision:.2f}",
            "Recall": f"{t.recall:.2f}",
            "F1": f"{t.f1:.2f}",
            "False alarms / cell / day": f"{t.false_alarms_per_day:.2f}",
            "Median delay (min)": delay,
        }


def evaluate(
    name: str,
    make: Callable[[], Detector],
    splits: Sequence[Split],
    quantiles: Sequence[float] = QUANTILES,
) -> Result:
    """Choose the threshold quantile on the tune part, then report on the test part."""
    scored = [score_series(make, split) for split in splits]
    best = max(quantiles, key=lambda q: count(scored, q, "tune").f1)
    return Result(name, best, count(scored, best, "test"))


def markdown_table(results: Sequence[Result]) -> str:
    rows = [r.row() for r in results]
    header = list(rows[0])
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row[h] for h in header) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellpulse-evaluate", description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/faulty.parquet"))
    parser.add_argument("--truth", type=Path, default=Path("data/faulty_ground_truth.csv"))
    parser.add_argument("--out", type=Path, default=Path("results/simulated.md"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    splits = [prepare(series) for series in load_simulated(args.data, args.truth)]
    results = [evaluate(name, make, splits) for name, make in DETECTORS.items()]
    table = markdown_table(results)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(table)
    print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
