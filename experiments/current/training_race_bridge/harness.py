"""EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.

Minimal adapter between synthetic Training V2 SPEC states and the unchanged
experimental Race Engine V2 primitives.  The adapter intentionally lives here:
it neither changes nor monkey-patches Race Engine V2.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
import json
from pathlib import Path

from experiments.current.race_engine_v2.core import (
    available_productions, base_reserve_from_ctl, generate_rolls,
)
from experiments.current.race_engine_v2.energy import energy_cost
from experiments.current.race_engine_v2.fixtures import POOLS
from experiments.current.race_engine_v2.form import classify_form, form_value

STATUS = "EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN"
SEEDS = tuple(range(20))
POOL = POOLS["6d6"]
RACE_LENGTH = 6
CURVE = "B"
CTL = 100
FRESHNESS = 0
FORM_MODE = "PATTERN"
EF, SEUIL, VMA = 15, 21, 27
BUILDS = {"SPEED": (4, 0), "BALANCED": (2, 2), "ECONOMY": (0, 4)}
CONTEXTS = {"AS42": 17, "AS10": 22}


@dataclass(frozen=True)
class Athlete:
    context: str
    ef: int
    seuil: int
    vma: int
    initial_as: int
    active_as: int
    position_tiers: int
    efficiency_tiers: int
    effective_eco: int
    unusable_position_tiers: int
    unusable_efficiency_tiers: int


def curve_cost(production: int) -> int:
    return energy_cost(production, CURVE)


def eco_max(active_as: int) -> int:
    return min(curve_cost(active_as) - curve_cost(EF),
               curve_cost(VMA) - curve_cost(active_as))


def make_athlete(context: str, build: str) -> Athlete:
    position, efficiency = BUILDS[build]
    initial = CONTEXTS[context]
    active = min(VMA, initial + position)
    applied_position = active - initial
    effective = min(efficiency, eco_max(active))
    return Athlete(context, EF, SEUIL, VMA, initial, active, position,
                   efficiency, effective, position - applied_position,
                   efficiency - effective)


def effective_cost(production: int, athlete: Athlete) -> tuple[int, bool]:
    native = curve_cost(production)
    if production != athlete.active_as:
        return native, False
    adjusted = max(curve_cost(athlete.ef), native - athlete.effective_eco)
    return adjusted, adjusted < native


def _sustainable_choice(options: tuple[int, ...], athlete: Athlete, budget: int,
                        remaining_segments: int) -> tuple[int, bool]:
    """Single neutral probe policy: target AS, preserve one EF-cost per future leg."""
    floor = curve_cost(athlete.ef) * remaining_segments
    target_options = [p for p in options if p <= athlete.active_as]
    sustainable = [p for p in target_options
                   if p <= athlete.active_as and effective_cost(p, athlete)[0] + floor <= budget]
    unconstrained_choice = max(target_options) if target_options else min(options)
    if sustainable:
        choice = max(sustainable)
        return choice, choice != unconstrained_choice
    payable = [p for p in options if effective_cost(p, athlete)[0] <= budget]
    if not payable:
        raise ValueError("no payable production")
    choice = min(payable)
    return choice, choice != unconstrained_choice


def run_course(context: str, build: str, seed: int) -> dict:
    athlete = make_athlete(context, build)
    rolls = generate_rolls(seed, POOL, RACE_LENGTH)
    base = base_reserve_from_ctl(CTL, RACE_LENGTH)
    spent = 0
    raw_reserve = None
    reserve = None
    form_values: list[int] = []
    turns: list[dict] = []
    first_constrained = None

    for segment, roll in enumerate(rolls, 1):
        if segment <= 3:
            signal = classify_form(roll, POOL, FORM_MODE)
            form_values.append(form_value(signal, False))
            if segment == 3:
                raw_reserve = base + FRESHNESS + sum(form_values)
        options = available_productions(roll).productions
        visible_reserve = raw_reserve if segment == 3 else reserve
        budget = (base + FRESHNESS - spent if visible_reserve is None
                  else visible_reserve - spent)
        try:
            choice, constrained = _sustainable_choice(
                options, athlete, budget, RACE_LENGTH - segment)
        except ValueError:
            return _result(athlete, build, seed, rolls, turns, spent, reserve,
                           segment, first_constrained)
        cost, eco_triggered = effective_cost(choice, athlete)
        spent += cost
        if constrained and first_constrained is None:
            first_constrained = segment
        if segment == 3:
            reserve = max(raw_reserve, spent)
        turns.append({"segment": segment, "roll": roll, "choice": choice,
                      "native_cost": curve_cost(choice), "cost": cost,
                      "at_as": choice == athlete.active_as,
                      "below_as": choice < athlete.active_as,
                      "above_as": choice > athlete.active_as,
                      "eco_triggered": eco_triggered,
                      "reserve_remaining": None if reserve is None else reserve - spent})
    return _result(athlete, build, seed, rolls, turns, spent, reserve, None,
                   first_constrained)


def _result(athlete: Athlete, build: str, seed: int, rolls, turns, spent,
            reserve, dnf_turn, first_constrained) -> dict:
    production = sum(turn["choice"] for turn in turns)
    at_as = sum(turn["at_as"] for turn in turns)
    return {"context": athlete.context, "build": build, "seed": seed,
            "athlete": asdict(athlete), "rolls": rolls, "turns": turns,
            "finished": dnf_turn is None, "dnf_turn": dnf_turn,
            "segments_played": len(turns), "production_total": production,
            "production_mean": production / len(turns) if turns else 0,
            "cost_total": spent, "final_reserve": reserve,
            "reserve_remaining": None if reserve is None else reserve - spent,
            "segments_at_as": at_as,
            "cost_at_as": sum(t["cost"] for t in turns if t["at_as"]),
            "eco_trigger_count": sum(t["eco_triggered"] for t in turns),
            "production_per_cost": production / spent if spent else None,
            "frequency_at_as": at_as / len(turns) if turns else 0,
            "frequency_below_as": sum(t["below_as"] for t in turns) / len(turns) if turns else 0,
            "frequency_above_as": sum(t["above_as"] for t in turns) / len(turns) if turns else 0,
            "first_reserve_constrained_segment": first_constrained}


METRICS = ("production_total", "cost_total", "reserve_remaining", "segments_at_as")


def _mean(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows if row[key] is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def run_experiment() -> dict:
    courses = [run_course(context, build, seed) for context in CONTEXTS
               for seed in SEEDS for build in BUILDS]
    summaries = []
    for context in CONTEXTS:
        for build in BUILDS:
            rows = [r for r in courses if r["context"] == context and r["build"] == build]
            summaries.append({"context": context, "build": build, "courses": len(rows),
                              "finish_rate": _mean(rows, "finished"),
                              **{key: _mean(rows, key) for key in (
                                  "production_total", "production_mean", "cost_total",
                                  "reserve_remaining", "segments_at_as", "cost_at_as",
                                  "eco_trigger_count", "production_per_cost", "frequency_at_as",
                                  "frequency_below_as", "frequency_above_as")},
                              "first_reserve_constrained_segment_mean": _mean(
                                  rows, "first_reserve_constrained_segment")})
    pairs = []
    for context in CONTEXTS:
        for seed in SEEDS:
            indexed = {r["build"]: r for r in courses
                       if r["context"] == context and r["seed"] == seed}
            for left, right in combinations(BUILDS, 2):
                pairs.append({"context": context, "seed": seed,
                              "comparison": f"{left} - {right}",
                              **{metric: (indexed[left][metric] - indexed[right][metric])
                                 for metric in METRICS}})
    return {"status": STATUS, "protocol": {"seeds": list(SEEDS),
            "contexts": CONTEXTS, "builds": BUILDS, "race_length": RACE_LENGTH,
            "course_count": len(courses), "pool": POOL.name, "curve": CURVE,
            "ctl": CTL, "freshness": FRESHNESS, "form_mode": FORM_MODE,
            "difficulty": "D0_FLAT", "policy": "SPEC_TARGET_SUSTAINABLE"},
            "athletes": [asdict(make_athlete(c, b)) for c in CONTEXTS for b in BUILDS],
            "summaries": summaries, "paired_differences": pairs, "courses": courses}


def main() -> None:
    path = Path(__file__).with_name("results.json")
    path.write_text(json.dumps(run_experiment(), indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
