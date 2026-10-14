"""Read tracked JSON evidence; check Training V2's minimal F9 structure.

This validates syntax and containers, not scientific values or reproducibility.
No experiment is imported or executed, and no file is written.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys


TRAINING_RESULTS = "experiments/current/training_v2_minimal/results.json"
BLOCKS = ("A", "A2", "B", "B2", "C")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-JSON numeric constant: {value}")


def validate_training_results(result):
    """Require the five blocks and their basic containers, not a full schema."""
    if not isinstance(result, dict):
        raise ValueError("Training V2 results must be an object")
    for block in BLOCKS:
        if not isinstance(result.get(block), dict) or not result[block]:
            raise ValueError(f"Training V2 block {block} must be a nonempty object")
    for block in ("A", "A2"):
        count = result[block].get("raw_outcomes")
        if type(count) is not int or count <= 0:
            raise ValueError(f"Training V2 {block}.raw_outcomes must be a positive integer")
    for block, key in (("B", "policies"), ("B2", "cells")):
        entries = result[block].get(key)
        if (not isinstance(entries, dict) or not entries
                or any(not isinstance(v, dict) or not v for v in entries.values())):
            raise ValueError(f"Training V2 {block}.{key} must contain nonempty objects")
    rows = result["C"].get("rows")
    if (not isinstance(rows, list) or not rows
            or any(not isinstance(row, dict) or not row for row in rows)):
        raise ValueError("Training V2 C.rows must contain nonempty objects")


def validate_repository(root):
    """Use Git's index, including added files, while ignoring local outputs."""
    listing = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.json"]
    )
    paths = [p.decode("utf-8") for p in listing.split(b"\0") if p]
    if TRAINING_RESULTS not in paths:
        raise ValueError(f"required tracked JSON missing: {TRAINING_RESULTS}")
    for relative in paths:
        try:
            result = json.loads(
                (root / relative).read_text(encoding="utf-8"),
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
            if relative == TRAINING_RESULTS:
                validate_training_results(result)
        except (OSError, UnicodeError, ValueError) as exc:
            raise ValueError(f"{relative}: {exc}") from exc
    return len(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        count = validate_repository(args.root)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"JSON validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {count} tracked JSON files and Training V2 blocks A/A2/B/B2/C.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
