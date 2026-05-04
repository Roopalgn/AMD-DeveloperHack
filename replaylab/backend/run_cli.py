"""CLI entry point for the ReplayLab experiment runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from replaylab.backend.runner import run_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and record a ReplayLab experiment command.")
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--cmd", required=True)
    parser.add_argument("--output_dir", default="replaylab/runs")
    args = parser.parse_args()

    record = run_command(args.cmd, args.run_id, args.output_dir)
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
