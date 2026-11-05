"""Entry point for cellpulse-collector.

gRPC ingest service; exposes received KPIs as Prometheus metrics.
Not implemented yet: see the collector ingest story in milestone v0.1.
"""

from __future__ import annotations

import argparse
import logging
import sys

from cellpulse import __version__

log = logging.getLogger("cellpulse.collector")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellpulse-collector", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    log.warning("cellpulse-collector is not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
