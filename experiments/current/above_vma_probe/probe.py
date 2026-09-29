#!/usr/bin/env python3
"""Deterministic analytical probe of loads above VMA.

EXPERIMENTAL COUNTERFACTUALS — NOT CURRENT BEHAVIOR.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from physiology import PhysiologyProfile, physiological_cost


PROFILES = {
    "P1": PhysiologyProfile(ef=0, threshold=5, vma=10),
    "P2": PhysiologyProfile(ef=0, threshold=6, vma=10),
    "P3": PhysiologyProfile(ef=1, threshold=6, vma=11),
}
DIFFICULTIES = range(4)
OVERLOAD_COEFFICIENTS = (2, 3, 4)


def overload(profile: PhysiologyProfile, charge: int) -> int:
    """Return only the part of charge strictly above VMA."""
    return max(0, charge - profile.vma)


def native_cost_to_vma(profile: PhysiologyProfile, charge: int) -> int:
    """Use the integrated curve, capped only for analytical decomposition."""
    return physiological_cost(profile, min(charge, profile.vma))


def variant_a_legal(profile: PhysiologyProfile, production: int, difficulty: int) -> bool:
    return production + difficulty <= profile.vma


def variant_b_cost(profile: PhysiologyProfile, charge: int) -> int:
    """Locally continue the experimental post-threshold slope above VMA."""
    base = native_cost_to_vma(profile, charge)
    return base + 3 * overload(profile, charge)


def variant_c_cost(profile: PhysiologyProfile, charge: int, coefficient: int) -> int:
    """Add an explicit experimental overload term above VMA."""
    if coefficient not in OVERLOAD_COEFFICIENTS:
        raise ValueError("coefficient must be one of 2, 3, 4")
    base = native_cost_to_vma(profile, charge)
    return base + coefficient * overload(profile, charge)


def configuration(profile_name: str, profile: PhysiologyProfile,
                  production: int, difficulty: int) -> dict:
    charge = production + difficulty
    over = overload(profile, charge)
    return {
        "profile": profile_name,
        "production": production,
        "difficulty": difficulty,
        "charge": charge,
        "overload": over,
        "native_cost_to_vma": native_cost_to_vma(profile, charge),
        "variant_a": "LEGAL" if variant_a_legal(profile, production, difficulty) else "ILLEGAL",
        "variant_b_cost": variant_b_cost(profile, charge),
        "variant_c2_cost": variant_c_cost(profile, charge, 2),
        "variant_c3_cost": variant_c_cost(profile, charge, 3),
        "variant_c4_cost": variant_c_cost(profile, charge, 4),
    }


def build_results() -> dict:
    rows = []
    aggregate_a = []
    aggregate_overload = []
    for name, profile in PROFILES.items():
        for production in range(profile.vma - 3, profile.vma + 1):
            for difficulty in DIFFICULTIES:
                rows.append(configuration(name, profile, production, difficulty))
        for difficulty in DIFFICULTIES:
            aggregate_a.append({
                "profile": name,
                "difficulty": difficulty,
                "maximum_legal_production": profile.vma - difficulty,
                "production_loss_vs_d0": difficulty,
            })
        at_vma = physiological_cost(profile, profile.vma)
        for over in (1, 2, 3):
            costs = {"B": 3 * over, "C2": 2 * over,
                     "C3": 3 * over, "C4": 4 * over}
            aggregate_overload.append({
                "profile": name,
                "overload": over,
                "cost_at_vma": at_vma,
                "surcharges": {
                    variant: {
                        "absolute": surcharge,
                        "relative_to_cost_at_vma": surcharge / at_vma,
                    }
                    for variant, surcharge in costs.items()
                },
            })
    return {
        "status": "EXPERIMENTAL COUNTERFACTUALS — NOT CURRENT BEHAVIOR",
        "method": "deterministic exhaustive analytical grid; no RNG; no race simulation",
        "source_revision": _source_revision(),
        "parameters": {
            "profiles": {name: {"ef": p.ef, "threshold": p.threshold, "vma": p.vma}
                         for name, p in PROFILES.items()},
            "production_offsets_from_vma": [-3, -2, -1, 0],
            "difficulties": list(DIFFICULTIES),
            "native_slopes": [2, 3],
            "overload_coefficients": list(OVERLOAD_COEFFICIENTS),
            "configuration_count": len(rows),
        },
        "configurations": rows,
        "aggregate_a": aggregate_a,
        "aggregate_overload": aggregate_overload,
    }


def _source_revision() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True,
            text=True, cwd=Path(__file__).resolve().parents[3]
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> None:
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(build_results(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
