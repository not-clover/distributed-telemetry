"""Entry point for cellpulse-detector.

Polls Prometheus and flags anomalous cells.
Not implemented yet: see the anomaly detector story in milestone v0.3.
"""

from __future__ import annotations

import argparse
import logging
import sys

from cellpulse import __version__

log = logging.getLogger("cellpulse.detector")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellpulse-detector", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    log.warning("cellpulse-detector is not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
