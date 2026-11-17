"""Entry point for cellpulse-simulate.

Generates the simulated dataset of normal cell behaviour and saves it as a Parquet file.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from cellpulse import __version__
from cellpulse.simulator.dataset import simulate

log = logging.getLogger("cellpulse.simulator")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellpulse-simulate", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--days", type=int, default=28, help="number of days to simulate")
    parser.add_argument("--interval", type=int, default=60, help="seconds between measurements")
    parser.add_argument("--seed", type=int, default=42, help="seed for the random generator")
    parser.add_argument(
        "--out", type=Path, default=Path("data/normal.parquet"), help="where to save the dataset"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    df = simulate(n_days=args.days, interval_s=args.interval, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out, index=False)
    log.info("wrote %d rows to %s", len(df), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
