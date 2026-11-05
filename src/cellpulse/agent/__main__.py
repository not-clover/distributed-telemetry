"""Entry point for cellpulse-agent.

Simulates N 5G cells at one site and streams their KPIs to the collectors.
Not implemented yet: see the agent simulator story in milestone v0.1.
"""

from __future__ import annotations

import argparse
import logging
import sys

from cellpulse import __version__

log = logging.getLogger("cellpulse.agent")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellpulse-agent", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    log.warning("cellpulse-agent is not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
