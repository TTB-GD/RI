#!/usr/bin/env python3
"""Deterministic micro-enumeration of experimental local SPEC curves.

EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN
"""

from __future__ import annotations

import json
from pathlib import Path


EF = 0
THRESHOLD = 5
VMA = 10
AS_FIXTURES = {"AS42": 2, "AS21": 4, "AS10": 6, "AS5": 8}
FOOTPRINTS = {
    "E0": {0: -1},
    "E1": {-1: -1, 0: -2, 1: -1},
    # Faster-side bias: the benefit is retained at AS+1, but nowhere beyond it.
    "E2": {-1: -1, 0: -2, 1: -2},
}
BUDGETS = (2, 3, 4)


def native_curve(threshold: int, vma: int) -> list[int]:
    """Use +2 through threshold, then +3: visible but uncalibrated regimes."""
    return [2 * min(position, threshold) + 3 * max(0, position - threshold)
            for position in range(vma + 1)]


def adjusted_curve(as_position: int, efficiencies: int, footprint: dict[int, int],
                   threshold: int = THRESHOLD, vma: int = VMA) -> list[int]:
    curve = native_curve(threshold, vma)
    for offset, delta in footprint.items():
        position = as_position + offset
        if EF <= position <= vma:
            curve[position] += efficiencies * delta
    return curve


def violations(curve: list[int]) -> list[str]:
    found = []
    if any(cost < 0 for cost in curve):  # Native EF cost is fixed at zero.
        found.append("cost_below_ef")
    if any(left > right for left, right in zip(curve, curve[1:])):
        found.append("non_monotone")
    return found


def position_limit(label: str, threshold: int, vma: int) -> int:
    return threshold if label in ("AS42", "AS21") else vma


def position_legal(label: str, as_position: int, efficiencies: int,
                   footprint: dict[int, int], threshold: int = THRESHOLD,
                   vma: int = VMA) -> bool:
    candidate_as = as_position + 1
    if candidate_as >= position_limit(label, threshold, vma):
        return False
    return not violations(adjusted_curve(candidate_as, efficiencies, footprint,
                                          threshold, vma))


def efficiency_legal(as_position: int, efficiencies: int,
                     footprint: dict[int, int], threshold: int = THRESHOLD,
                     vma: int = VMA) -> bool:
    # The footprint is fixed and radius <= 1 by construction, so only the two
    # numerical shape invariants can fail when another level is added.
    return not violations(adjusted_curve(as_position, efficiencies + 1, footprint,
                                          threshold, vma))


def state_record(label: str, as_position: int, positions: int, efficiencies: int,
                 footprint: dict[int, int], threshold: int = THRESHOLD,
                 vma: int = VMA) -> dict:
    can_position = position_legal(label, as_position, efficiencies, footprint,
                                  threshold, vma)
    can_efficiency = efficiency_legal(as_position, efficiencies, footprint,
                                      threshold, vma)
    return {
        "id": f"{label}:AS{as_position}:P{positions}:E{efficiencies}",
        "final_as": as_position,
        "position_levels": positions,
        "efficiency_levels": efficiencies,
        "curve": adjusted_curve(as_position, efficiencies, footprint,
                                 threshold, vma),
        "position_legal": can_position,
        "efficiency_legal": can_efficiency,
        "spec_saturated": not can_position and not can_efficiency,
    }


def enumerate_states(label: str, start_as: int, footprint: dict[int, int]) -> dict:
    frontier = {(start_as, 0, 0)}
    by_budget = {}
    for spent in range(1, max(BUDGETS) + 1):
        candidates = set()
        for as_position, positions, efficiencies in frontier:
            if position_legal(label, as_position, efficiencies, footprint):
                candidates.add((as_position + 1, positions + 1, efficiencies))
            if efficiency_legal(as_position, efficiencies, footprint):
                candidates.add((as_position, positions, efficiencies + 1))
        frontier = candidates
        if spent in BUDGETS:
            by_budget[str(spent)] = [
                state_record(label, *state, footprint)
                for state in sorted(frontier)
            ]
    return by_budget


def footprint_table(as_position: int, footprint: dict[int, int]) -> list[dict]:
    native = native_curve(THRESHOLD, VMA)
    adjusted = adjusted_curve(as_position, 1, footprint)
    positions = sorted(as_position + offset for offset in footprint)
    return [{"position": position, "native_cost": native[position],
             "cost_after_one_efficiency": adjusted[position],
             "delta": adjusted[position] - native[position]}
            for position in positions]


def main() -> None:
    native = native_curve(THRESHOLD, VMA)
    spaces = {}
    footprint_tables = {}
    saturated = {}
    reopenings = []

    for footprint_name, footprint in FOOTPRINTS.items():
        spaces[footprint_name] = {}
        footprint_tables[footprint_name] = {}
        for label, start_as in AS_FIXTURES.items():
            footprint_tables[footprint_name][label] = footprint_table(start_as, footprint)
            budget_states = enumerate_states(label, start_as, footprint)
            spaces[footprint_name][label] = budget_states
            unique_saturated = {}
            for states in budget_states.values():
                for state in states:
                    if state["spec_saturated"]:
                        unique_saturated[state["id"]] = state
            for state_id, state in unique_saturated.items():
                threshold = THRESHOLD + (label in ("AS42", "AS21"))
                vma = VMA + (label in ("AS10", "AS5"))
                reopened_position = position_legal(
                    label, state["final_as"], state["efficiency_levels"], footprint,
                    threshold, vma)
                reopened_efficiency = efficiency_legal(
                    state["final_as"], state["efficiency_levels"], footprint,
                    threshold, vma)
                reopenings.append({
                    "footprint": footprint_name,
                    "state": state_id,
                    "boundary": "threshold" if label in ("AS42", "AS21") else "vma",
                    "before": THRESHOLD if label in ("AS42", "AS21") else VMA,
                    "after": threshold if label in ("AS42", "AS21") else vma,
                    "position_reopened": reopened_position,
                    "efficiency_reopened": reopened_efficiency,
                })
            saturated[f"{footprint_name}/{label}"] = list(unique_saturated)

    width_checks = []
    for vma in (10, 11, 12):
        curve = native_curve(THRESHOLD, vma)
        checked = 0
        invalid = 0
        for footprint in FOOTPRINTS.values():
            for as_position in range(1, vma):
                for efficiencies in range(3):
                    checked += 1
                    invalid += bool(violations(adjusted_curve(
                        as_position, efficiencies, footprint, THRESHOLD, vma)))
        width_checks.append({"vma": vma, "native_curve": curve,
                             "native_monotone": not violations(curve),
                             "local_states_checked": checked,
                             "invalid_local_states": invalid})

    result = {
        "status": "EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN",
        "method": "deterministic exhaustive micro-enumeration; no RNG; no Monte Carlo",
        "parameters": {"ef": EF, "threshold": THRESHOLD, "vma": VMA,
                       "as_fixtures": AS_FIXTURES, "budgets": BUDGETS,
                       "native_increments": {"ef_through_threshold": 2,
                                             "after_threshold": 3},
                       "footprints": FOOTPRINTS},
        "native_curve": [{"position": position, "native_cost": cost,
                          "zone": "EF→Seuil" if position <= THRESHOLD else "Seuil→VMA"}
                         for position, cost in enumerate(native)],
        "footprint_tables": footprint_tables,
        "spaces": spaces,
        "saturated_state_ids": saturated,
        "reopenings": reopenings,
        "unbounded_vma_checks": width_checks,
    }
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
