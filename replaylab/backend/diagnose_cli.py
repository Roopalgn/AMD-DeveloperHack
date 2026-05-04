"""CLI entry point for ReplayLab diagnosis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from replaylab.backend.diagnoser import compare_runs


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose a failed ReplayLab run against a recovered run.")
    parser.add_argument("--bad", required=True, help="Path to failed run directory.")
    parser.add_argument("--good", required=True, help="Path to successful run directory.")
    args = parser.parse_args()

    diagnosis = compare_runs(args.bad, args.good)
    print(json.dumps(diagnosis, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
