"""Smoke tests: the package imports, entry points run, and the proto contract compiles."""

from __future__ import annotations

import importlib

import pytest

import cellpulse
from cellpulse.v1 import telemetry_pb2

COMPONENTS = ["agent", "collector", "detector", "cli"]


def test_version_is_semver() -> None:
    parts = cellpulse.__version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


@pytest.mark.parametrize("component", COMPONENTS)
def test_entry_point_runs(component: str) -> None:
    module = importlib.import_module(f"cellpulse.{component}.__main__")
    assert module.main([]) == 0


def test_kpi_batch_round_trip() -> None:
    batch = telemetry_pb2.KpiBatch(site_id="site-a", sequence=1)
    sample = batch.samples.add()
    sample.cell_id = "site-a/cell-001"
    sample.prb_utilisation_pct = 42.5
    sample.observed_at.GetCurrentTime()

    decoded = telemetry_pb2.KpiBatch.FromString(batch.SerializeToString())

    assert decoded.site_id == "site-a"
    assert decoded.samples[0].prb_utilisation_pct == pytest.approx(42.5)
