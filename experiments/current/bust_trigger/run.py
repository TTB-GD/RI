"""Deterministic characterization harness for the missing bust trigger.

CURRENT EXPERIMENT — NOT PRODUCTION BEHAVIOR.
"""

import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from session_resolution import resolve_session_plan
from session_selector import choose_sessions_weighted
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG


@dataclass(frozen=True)
class RiskCheck:
    session: str
    rpe_max: int
    overshoot: int
    die_size: int
    roll: int | None
    risky: bool
    bust: bool


def risk_die_size(pool_sizes):
    """Experimental policy: use the largest die in the current pool."""
    if not pool_sizes:
        raise ValueError("pool_sizes must not be empty")
    return max(pool_sizes)


def check_candidate_bust(session_name, rpe_max, die_size, roll):
    """Characterize one session under the candidate Fatigue V1 bust rule."""
    category, rpe = SESSION_CATALOG[session_name]
    risky = category in QUALITY_CATEGORIES and rpe > rpe_max
    overshoot = max(0, rpe - rpe_max) if category in QUALITY_CATEGORIES else 0

    if not risky:
        return RiskCheck(
            session=session_name,
            rpe_max=rpe_max,
            overshoot=overshoot,
            die_size=die_size,
            roll=None,
            risky=False,
            bust=False,
        )

    if not 1 <= roll <= die_size:
        raise ValueError("risk roll outside die range")

    return RiskCheck(
        session=session_name,
        rpe_max=rpe_max,
        overshoot=overshoot,
        die_size=die_size,
        roll=roll,
        risky=True,
        bust=roll <= overshoot,
    )


def first_bust_index(planned, rpe_max, pool_sizes, risk_rolls):
    """Test risky qualities in planned order and stop at the first bust.

    risk_rolls supplies one deterministic roll per risky quality actually tested.
    Later rolls are not consumed after the first bust.
    """
    die_size = risk_die_size(pool_sizes)
    roll_iter = iter(risk_rolls)
    checks = []

    for index, name in enumerate(planned):
        category, rpe = SESSION_CATALOG[name]
        if category not in QUALITY_CATEGORIES or rpe <= rpe_max:
            continue

        try:
            roll = next(roll_iter)
        except StopIteration as exc:
            raise ValueError("missing deterministic risk roll") from exc

        check = check_candidate_bust(name, rpe_max, die_size, roll)
        checks.append(check)
        if check.bust:
            return index, tuple(checks)

    return None, tuple(checks)


def theoretical_bust_probability(overshoot, die_size):
    if overshoot <= 0:
        return 0.0
    if die_size <= 0:
        raise ValueError("die_size must be positive")
    return min(overshoot, die_size) / die_size


def selector_risk_gap():
    """FACT probe: current selector hard-blocks RPE above rpe_max."""
    chosen, _ = choose_sessions_weighted(
        ["EF1", "Seuil5"],
        energy_budget=20,
        rpe_max=4,
        tn=14,
        quality_limit=1,
        weights={
            "w_energy": 0.0,
            "w_sessions": 10.0,
            "w_fatigue": 0.0,
            "w_rpe": 0.0,
        },
    )
    return {
        "input": ["EF1", "Seuil5"],
        "rpe_max": 4,
        "chosen": chosen,
        "risky_quality_planned": any(
            SESSION_CATALOG[name][0] in QUALITY_CATEGORIES
            and SESSION_CATALOG[name][1] > 4
            for name in chosen
        ),
    }


def probability_matrix():
    rows = []
    for die_size in (6, 8, 10, 12):
        for overshoot in (1, 2, 3, 4):
            rows.append({
                "die_size": die_size,
                "overshoot": overshoot,
                "bust_probability": theoretical_bust_probability(overshoot, die_size),
            })
    return rows


def deterministic_scenarios():
    return [
        asdict(check_candidate_bust("Seuil3", rpe_max=4, die_size=8, roll=1)),
        asdict(check_candidate_bust("Seuil5", rpe_max=4, die_size=6, roll=1)),
        asdict(check_candidate_bust("Seuil5", rpe_max=4, die_size=6, roll=2)),
        asdict(check_candidate_bust("VMA6", rpe_max=4, die_size=8, roll=2)),
        asdict(check_candidate_bust("VMA6", rpe_max=4, die_size=8, roll=3)),
        asdict(check_candidate_bust("Spec7", rpe_max=4, die_size=10, roll=3)),
        asdict(check_candidate_bust("Spec7", rpe_max=4, die_size=10, roll=4)),
    ]


def ordered_case(name, planned, risk_rolls, rpe_max=4):
    """Run one reproducible ordering case and, on bust, the current resolver."""
    pool_sizes = [6, 6, 8, 10]
    bust_index, checks = first_bust_index(planned, rpe_max, pool_sizes, risk_rolls)
    resolution = resolve_session_plan(
        planned,
        available_session_names=list(SESSION_CATALOG),
        rpe_max=rpe_max,
        bust_index=bust_index,
    )
    return {
        "name": name,
        "planned": planned,
        "supplied_risk_rolls": risk_rolls,
        "risk_die_size": risk_die_size(pool_sizes),
        "bust_index": bust_index,
        "busted_session": planned[bust_index] if bust_index is not None else None,
        "tested_risks": [asdict(check) for check in checks],
        "risk_rolls_consumed": len(checks),
        "resolution": asdict(resolution),
    }


def ordered_scenarios():
    """Minimal cases covering risk order and the first-bust short circuit."""
    return [
        ordered_case("no_risky_session", ["EF1", "Seuil3"], []),
        ordered_case("one_risky_session_no_bust", ["EF1", "Seuil5"], [2]),
        ordered_case(
            "multiple_risks_no_bust", ["Seuil5", "VMA6", "Force5"], [2, 3, 2],
        ),
        ordered_case(
            "bust_on_first_risk", ["Seuil5", "VMA6", "Force5"], [1, 9, 9],
        ),
        ordered_case(
            "bust_on_intermediate_risk",
            ["EF1", "Seuil5", "EF2", "VMA6", "Force5"],
            [5, 2, 9],
        ),
    ]


def run():
    return {
        "status": "CURRENT EXPERIMENT — NOT PRODUCTION BEHAVIOR",
        "selector_gap": selector_risk_gap(),
        "boundary_scenarios": deterministic_scenarios(),
        "ordered_scenarios": ordered_scenarios(),
        "probability_matrix": probability_matrix(),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), ensure_ascii=False, indent=2))
