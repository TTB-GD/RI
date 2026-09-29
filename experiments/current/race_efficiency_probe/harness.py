"""EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.

Deterministic analytic probe of POSITION and EFFICIENCY inside EF..VMA.
It does not call or modify Race Engine V2 or any production rule.
"""

from __future__ import annotations

import json
from pathlib import Path

STATUS = "EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN"
SOURCE_BASELINE = "4f7fb9d"
EF, VMA = 0, 10
CURVES = {
    "LINEAR": {"base": 5.0, "linear": 1.0, "quadratic": 0.0},
    "CONVEX": {"base": 5.0, "linear": 0.8, "quadratic": 0.05},
}
BUILDS = {
    "FULL_POSITION": (4, 0),
    "BALANCED": (2, 2),
    "FULL_EFFICIENCY": (0, 4),
}
STARTS = {"LOW": 2, "MID": 5, "HIGH": 8}
SEGMENTS = (4, 8, 12)


def native_cost(curve: str, position: int) -> float:
    """Return C0 on the closed experimental aerobic domain."""
    if curve not in CURVES:
        raise ValueError(f"unknown curve: {curve}")
    if not EF <= position <= VMA:
        raise ValueError(f"position outside [{EF}, {VMA}]: {position}")
    terms = CURVES[curve]
    return round(terms["base"] + terms["linear"] * position
                 + terms["quadratic"] * position**2, 3)


def eco_max(curve: str, position: int) -> float:
    lower = native_cost(curve, position) - native_cost(curve, EF)
    upper = native_cost(curve, VMA) - native_cost(curve, position)
    return round(min(lower, upper), 3)


def adjusted_cost(curve: str, position: int, raw_eco: float) -> tuple[float, float, float]:
    effective = min(raw_eco, eco_max(curve, position))
    return (round(native_cost(curve, position) - effective, 3),
            round(effective, 3), round(raw_eco - effective, 3))


def envelope_rows(curve: str) -> list[dict]:
    ef_cost, vma_cost = native_cost(curve, EF), native_cost(curve, VMA)
    return [{
        "position": x,
        "C0": native_cost(curve, x),
        "distance_to_EF_cost": round(native_cost(curve, x) - ef_cost, 3),
        "distance_to_VMA_cost": round(vma_cost - native_cost(curve, x), 3),
        "ECO_MAX": eco_max(curve, x),
        "minimum_reachable_cost": adjusted_cost(curve, x, float("inf"))[0],
    } for x in range(EF, VMA + 1)]


def build_row(curve: str, start_name: str, build: str) -> dict:
    position_tiers, raw_eco = BUILDS[build]
    final_as = min(VMA, STARTS[start_name] + position_tiers)
    cost, effective, wasted = adjusted_cost(curve, final_as, raw_eco)
    next_as = min(VMA, final_as + 1)
    next_cost, next_effective, _ = adjusted_cost(curve, next_as, raw_eco)
    next_eff_cost, _, _ = adjusted_cost(curve, final_as, raw_eco + 1)
    return {
        "curve": curve, "start": start_name, "build": build,
        "position_tiers": position_tiers, "final_AS": final_as,
        "raw_ECO": raw_eco, "effective_ECO": effective, "wasted_ECO": wasted,
        "native_cost_at_AS": native_cost(curve, final_as),
        "adjusted_cost_at_AS": cost,
        "next_POSITION": {
            "new_AS": next_as,
            "delta_C0": round(native_cost(curve, next_as) - native_cost(curve, final_as), 3),
            "delta_ECO_MAX": round(eco_max(curve, next_as) - eco_max(curve, final_as), 3),
            "adjusted_cost_change": round(next_cost - cost, 3),
            "effective_ECO_change": round(next_effective - effective, 3),
        },
        "next_EFFICIENCY": {"real_cost_reduction": round(cost - next_eff_cost, 3)},
    }


def race_rows(build: dict) -> list[dict]:
    """Repeat costs locally; ECO applies only at the build's active AS."""
    rows = []
    for pace in range(max(EF, build["final_AS"] - 1), min(VMA, build["final_AS"] + 1) + 1):
        per_segment = (build["adjusted_cost_at_AS"] if pace == build["final_AS"]
                       else native_cost(build["curve"], pace))
        rows.append({
            "curve": build["curve"], "start": build["start"], "build": build["build"],
            "tested_pace": pace, "cost_per_segment": per_segment,
            **{f"cost_x{n}": round(per_segment * n, 3) for n in SEGMENTS},
        })
    return rows


def run_probe() -> dict:
    envelopes = {curve: envelope_rows(curve) for curve in CURVES}
    builds = [build_row(curve, start, build) for curve in CURVES
              for start in STARTS for build in BUILDS]
    races = [race for build in builds for race in race_rows(build)]
    checks = {
        "monotone": all(all(rows[i]["C0"] < rows[i + 1]["C0"]
                             for i in range(len(rows) - 1)) for rows in envelopes.values()),
        "zero_at_EF": all(rows[0]["ECO_MAX"] == 0 for rows in envelopes.values()),
        "zero_at_VMA": all(rows[-1]["ECO_MAX"] == 0 for rows in envelopes.values()),
        "nonnegative_envelope": all(row["ECO_MAX"] >= 0 for rows in envelopes.values()
                                    for row in rows),
        "floor_respected": all(row["minimum_reachable_cost"] >= rows[0]["C0"]
                               for rows in envelopes.values() for row in rows),
    }
    return {
        "status": STATUS,
        "protocol": {"source_baseline": SOURCE_BASELINE, "deterministic": True,
                     "seeds": [], "games": 0, "turns": 0, "EF": EF, "VMA": VMA,
                     "curves": CURVES, "starts": STARTS, "builds": BUILDS,
                     "segments": list(SEGMENTS),
                     "E4_ECO_scope": "active AS only; adjacent tested paces use C0"},
        "E1_E2": envelopes, "E3": builds, "marginals": builds, "E4": races,
        "checks": checks,
    }


def main() -> None:
    destination = Path(__file__).with_name("results.json")
    destination.write_text(json.dumps(run_probe(), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()

