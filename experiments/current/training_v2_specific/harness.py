"""EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.

Isolated Training V2 probe: physiology opens an AS boundary and only SPEC
changes the local Race Engine V2 comparison.  Nothing in this module is a
CURRENT rule.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import random
import statistics

from experiments.current.race_engine_v2.energy import energy_cost
from experiments.current.training_v2_minimal.harness import (
    EF_DIE_MILESTONES, EF_MILESTONES, Q_MILESTONES, Q_UPGRADE_MILESTONES,
    SIZE_SEQUENCE, legal_partitions, quality_cost, resolve_roll,
)

STATUS = "EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN"
SOURCE_BASELINE = "f9f94bd75fd46fd8ee5cecf5a70fa8564150eb7b"
SPEC_TABLES = {
    "S1": (5, 10, 15, 20, 25),
    "S2": (5, 12, 21, 32, 45),
    "S3": (5, 15, 30, 50, 75),
}
CONTEXTS = {"AS42": 7, "AS10": 9}
POLICIES = ("G_GENERAL", "G_SWITCH", "G_SPEC")
BLOCKS = ((1, 4), (5, 8), (9, 12), (13, 16))


@dataclass
class State:
    context: str
    spec_table: str
    ef: int = 6
    seuil: int = 8
    vma: int = 10
    as_value: int = 0
    eco: int = 0
    progression_ef: int = 0
    progression_q: int = 0
    progression_spec: int = 0
    spec_tiers: int = 0
    pool: tuple[int, ...] = (6, 6, 6, 6)
    upgrades: int = 0

    def __post_init__(self):
        if not self.as_value:
            self.as_value = CONTEXTS[self.context]


def _apply_track_milestones(state: State, old_ef: int, old_q: int) -> None:
    """Reuse the minimal harness tracks without importing its private state."""
    for milestone in EF_MILESTONES:
        if old_ef < milestone <= state.progression_ef:
            if milestone in EF_DIE_MILESTONES:
                state.pool += (6,)
            elif state.ef + 1 < state.seuil:
                state.ef += 1
    for milestone in Q_MILESTONES:
        if old_q < milestone <= state.progression_q and milestone in Q_UPGRADE_MILESTONES:
            eligible = [i for i, size in enumerate(state.pool) if size < 12]
            if eligible and state.upgrades < 4:
                index = min(eligible, key=lambda i: (state.pool[i], i))
                pool = list(state.pool)
                pool[index] = SIZE_SEQUENCE[SIZE_SEQUENCE.index(pool[index]) + 1]
                state.pool = tuple(pool)
                state.upgrades += 1


def _speed_available(state: State) -> bool:
    boundary = state.seuil if state.context == "AS42" else state.vma
    return state.as_value < boundary


def _award_spec_tiers(state: State, build: str = "BALANCED") -> list[str]:
    awards = []
    thresholds = SPEC_TABLES[state.spec_table]
    while state.spec_tiers < len(thresholds) and state.progression_spec >= thresholds[state.spec_tiers]:
        wants_speed = build == "SPEED" or (build == "BALANCED" and state.spec_tiers % 2 == 0)
        if wants_speed and _speed_available(state):
            state.as_value += 1
            awards.append("AS")
        else:  # EXPERIMENTAL convention: saturation forces ECO, with no stored tier.
            state.eco += 1
            awards.append("ECO")
        state.spec_tiers += 1
    return awards


def _phys_options(state: State, used: set[str]) -> list[tuple[str, int]]:
    rows = []
    if "VMA" not in used:
        rows.append(("VMA", quality_cost(state.vma, state.ef)))
    if "SEUIL" not in used and state.seuil + 1 < state.vma:
        rows.append(("SEUIL", quality_cost(state.seuil, state.ef)))
    return rows


def allocate_q(state: State, q_energy: int, policy: str) -> tuple[list[tuple[str, int]], int, int]:
    """Return physiological attempts, SPEC energy, and unused energy.

    Qualities are indivisible and each marker is attempted at most once per
    turn. SPEC can accumulate partial energy. Ties under G_SWITCH go to
    physiology; physiological ties use the declared VMA-then-Seuil order.
    """
    remaining, spec = q_energy, 0
    attempts: list[tuple[str, int]] = []
    used: set[str] = set()
    thresholds = SPEC_TABLES[state.spec_table]

    def buy_phys() -> bool:
        for name, cost in _phys_options(state, used):
            if cost <= remaining:
                attempts.append((name, cost))
                used.add(name)
                return True
        return False

    if policy == "G_GENERAL":
        while buy_phys():
            remaining -= attempts[-1][1]
        if state.spec_tiers < len(thresholds):
            spec, remaining = remaining, 0
    elif policy == "G_SPEC":
        if state.spec_tiers < len(thresholds):
            need = thresholds[state.spec_tiers] - state.progression_spec
            spec = min(remaining, need)
            remaining -= spec
        while buy_phys():
            remaining -= attempts[-1][1]
    elif policy == "G_SWITCH":
        while remaining:
            options = _phys_options(state, used)
            phys = min(options, key=lambda row: (row[1], 0 if row[0] == "VMA" else 1)) if options else None
            spec_need = (thresholds[state.spec_tiers] - state.progression_spec - spec
                         if state.spec_tiers < len(thresholds) else None)
            # Equality deliberately selects physiology.
            choose_phys = phys is not None and (spec_need is None or phys[1] <= spec_need)
            if choose_phys and phys[1] <= remaining:
                attempts.append(phys)
                used.add(phys[0])
                remaining -= phys[1]
            elif spec_need is not None:
                amount = min(remaining, spec_need)
                spec += amount
                remaining -= amount
                if amount < spec_need:
                    break
                # Allocation is computed against current tier; stop at its
                # boundary so the adaptation can alter the next comparison.
                break
            else:
                break
    else:
        raise ValueError(f"unknown policy: {policy}")
    return attempts, spec, remaining


def simulate(seed: int, context: str, table: str, policy: str, turns: int = 16,
             build: str = "BALANCED") -> tuple[dict, list[dict]]:
    rng = random.Random(seed)
    state = State(context=context, spec_table=table)
    trajectory = []
    totals = Counter()
    for turn in range(1, turns + 1):
        raw = tuple(rng.randint(1, size) for size in state.pool)
        final = resolve_roll(raw)
        # Isolate Q allocation: fixed deterministic partition maximises Q while
        # respecting the physical EF >= Q partition constraint.
        ef_energy, q_energy, indices = min(
            legal_partitions(final), key=lambda row: (-row[1], -row[0], row[2]))
        attempts, spec_energy, unused = allocate_q(state, q_energy, policy)
        old_ef, old_q = state.progression_ef, state.progression_q
        state.progression_ef += ef_energy
        successful = []
        phys_allocated = sum(cost for _, cost in attempts)
        for name, cost in attempts:
            succeeded = True
            if cost > max(final):
                k = cost - max(final)
                succeeded = rng.randint(1, max(state.pool)) > k
            if succeeded:
                successful.append(name)
                state.progression_q += cost
        if "SEUIL" in successful:
            state.seuil += 1
        if "VMA" in successful:
            state.vma += 1
        before_tiers = state.spec_tiers
        state.progression_spec += spec_energy
        awards = _award_spec_tiers(state, build)
        _apply_track_milestones(state, old_ef, old_q)
        totals.update(q_total=q_energy, q_phys=phys_allocated, q_spec=spec_energy,
                      q_unused=unused)
        voluntary = spec_energy > 0 and not (policy == "G_GENERAL" and phys_allocated > 0)
        trajectory.append({
            "turn": turn, "ef": state.ef, "seuil": state.seuil, "vma": state.vma,
            "as": state.as_value, "eco": state.eco, "spec_tiers": state.spec_tiers,
            "progression_spec": state.progression_spec, "q_total": q_energy,
            "q_phys": phys_allocated, "q_spec": spec_energy, "q_unused": unused,
            "voluntary_spec": voluntary, "successful": successful, "awards": awards,
            "new_tier": state.spec_tiers > before_tiers,
        })
    cumulative_spec = cumulative_total = 0
    first_25 = None
    for step in trajectory:
        cumulative_spec += step["q_spec"]
        cumulative_total += step["q_total"]
        if first_25 is None and cumulative_total and cumulative_spec / cumulative_total > .25:
            first_25 = step["turn"]
    record = {
        "seed": seed, "context": context, "table": table, "policy": policy,
        "EF": state.ef, "SEUIL": state.seuil, "VMA": state.vma,
        "AS": state.as_value, "ECO": state.eco,
        "progression_SPEC": state.progression_spec, "spec_tiers": state.spec_tiers,
        **totals,
        "spec_share": totals["q_spec"] / totals["q_total"] if totals["q_total"] else 0,
        "first_voluntary_spec": next((s["turn"] for s in trajectory if s["voluntary_spec"]), None),
        "first_spec_over_25_cumulative": first_25,
        "first_spec_over_phys_turn": next((s["turn"] for s in trajectory
                                            if s["q_spec"] > s["q_phys"]), None),
    }
    for start, end in BLOCKS:
        block = trajectory[start - 1:end]
        denominator = sum(s["q_total"] for s in block)
        record[f"spec_share_t{start}_{end}"] = sum(s["q_spec"] for s in block) / denominator
    return record, trajectory


def _distribution(values: list[float | int | None]) -> dict:
    reached = sorted(v for v in values if v is not None)
    return {
        "mean": round(statistics.mean(reached), 3) if reached else None,
        "median": statistics.median(reached) if reached else None,
        "min": min(reached) if reached else None, "max": max(reached) if reached else None,
        "reached_pct": round(100 * len(reached) / len(values), 3),
    }


def run_d1(seeds: int = 50) -> tuple[dict, dict[tuple[str, str, str], list[dict]]]:
    metrics = ("EF", "SEUIL", "VMA", "AS", "ECO", "progression_SPEC", "spec_tiers",
               "q_total", "q_phys", "q_spec", "spec_share", "spec_share_t1_4",
               "spec_share_t5_8", "spec_share_t9_12", "spec_share_t13_16")
    cells, raw = {}, {}
    for context in CONTEXTS:
        for table in SPEC_TABLES:
            for policy in POLICIES:
                records = [simulate(seed, context, table, policy)[0] for seed in range(seeds)]
                raw[(context, table, policy)] = records
                cells[f"{context}__{table}__{policy}"] = {
                    "metrics": {name: _distribution([row[name] for row in records]) for name in metrics},
                    "timing": {name: _distribution([row[name] for row in records]) for name in
                               ("first_voluntary_spec", "first_spec_over_25_cumulative",
                                "first_spec_over_phys_turn")},
                }
    return {"seeds": list(range(seeds)), "turns": 16, "total_turns": seeds * 16 * 18,
            "build": "BALANCED", "cells": cells}, raw


def curve_comparison(as_value: int, eco: int, variant: str) -> list[dict]:
    rows = []
    for offset in range(-2, 3):
        production = as_value + offset
        base = energy_cost(production, "B")
        if variant == "C1":
            reduction = eco if abs(offset) <= 1 else 0
        elif variant == "C2":
            # Half-up convention is explicit and deterministic.
            reduction = eco if offset == 0 else (eco + 1) // 2 if abs(offset) == 1 else 0
        else:
            raise ValueError(f"unknown curve variant: {variant}")
        cost = max(0, base - reduction)
        rows.append({"offset": offset, "production": production, "base_cost": base,
                     "cost": cost, "cost_x4": cost * 4, "cost_x10": cost * 10})
    return rows


def _representative_states(raw: dict) -> list[dict]:
    selected = []
    # Three policy-shaped states per context, all from seed 0 and S2. They are
    # observed D1 endpoints, not synthetic longitudinal runs.
    for context in CONTEXTS:
        for label, policy in (("high_potential_low_spec", "G_GENERAL"),
                              ("balanced", "G_SWITCH"),
                              ("high_spec_low_potential", "G_SPEC")):
            row = raw[(context, "S2", policy)][0]
            selected.append({"label": label, **{k: row[k] for k in
                            ("seed", "context", "table", "policy", "EF", "SEUIL", "VMA",
                             "AS", "ECO", "progression_SPEC", "spec_tiers")}})
    return selected


def run_d2(raw: dict) -> dict:
    states = _representative_states(raw)
    return {"states": [{**state, "curves": {variant: curve_comparison(state["AS"], state["ECO"], variant)
                                              for variant in ("C1", "C2")}}
                       for state in states]}


def run_d3(raw: dict) -> dict:
    rows = []
    for context in CONTEXTS:
        fixture = next(state for state in _representative_states(raw)
                       if state["context"] == context and state["label"] == "balanced")
        for build in ("SPEED", "BALANCED", "ECO"):
            state = State(context=context, spec_table="S1", ef=fixture["EF"],
                          seuil=fixture["SEUIL"], vma=fixture["VMA"])
            state.progression_spec = SPEC_TABLES["S1"][3]
            _award_spec_tiers(state, build)
            at_as = curve_comparison(state.as_value, state.eco, "C1")[2]
            rows.append({"context": context, "build": build, "spec_tiers": 4,
                         "AS": state.as_value, "ECO": state.eco, "cost_at_as": at_as["cost"],
                         "cost_x4": at_as["cost_x4"], "cost_x10": at_as["cost_x10"],
                         "production_at_specific_point": state.as_value})
    return {"curve_variant": "C1", "rows": rows}


def run_all(seeds: int = 50) -> dict:
    d1, raw = run_d1(seeds)
    return {"status": STATUS, "protocol": {"source_baseline": SOURCE_BASELINE,
                                             "seed_count": seeds, "seed_range": [0, seeds - 1]},
            "D1": d1, "D2": run_d2(raw), "D3": run_d3(raw)}


if __name__ == "__main__":
    destination = Path(__file__).with_name("results.json")
    destination.write_text(json.dumps(run_all(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(destination)
