"""Entry point for cellpulse-cli.

Developer CLI: 'status' and 'load' commands (owned by partner).
Not implemented yet: see the 'cellpulse-cli status' story in milestone v0.1.
"""

from __future__ import annotations

import argparse
import logging
import sys

from cellpulse import __version__

log = logging.getLogger("cellpulse.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellpulse-cli", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    log.warning("cellpulse-cli is not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
