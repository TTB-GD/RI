"""EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.

Minimal, deterministic probe for the proposed Training V2 architecture.  This
module deliberately owns its rules rather than changing production training.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
import json
from pathlib import Path
import random
import statistics

from experiments.current.race_engine_v2.energy import energy_cost
from patterns import pattern_signature


EF_MILESTONES = (10, 20, 35, 50, 70, 100, 120, 150)
EF_DIE_MILESTONES = {35, 100}
Q_MILESTONES = (7, 15, 25, 35, 50, 65, 80, 100)
Q_UPGRADE_MILESTONES = {15, 35, 65, 100}
SIZE_SEQUENCE = (6, 8, 10, 12)


def difficulty(x: int) -> int:
    if x < 8:
        raise ValueError("quality marker must be at least 8")
    return min(5, 1 + (x - 8) // 5)


def quality_cost(x: int, ef: int) -> int:
    return (x - ef) + difficulty(x)


def has_reserve_bonus(faces: tuple[int, ...]) -> bool:
    """The existing D99 reserve-bonus motifs, without its quality cap."""
    signature = pattern_signature(faces)
    bonus_signatures = {
        4: {(3, 1), (2, 2), (4,)},
        5: {(2, 2, 1), (3, 1, 1), (3, 2), (4, 1), (5,)},
        6: {(2, 2, 1, 1), (3, 1, 1, 1), (3, 2, 1), (2, 2, 2),
            (4, 1, 1), (4, 2), (3, 3), (5, 1), (6,)},
    }
    return signature in bonus_signatures.get(len(faces), set())


def resolve_roll(raw_roll: tuple[int, ...], d99_mode: str = "D99_BONUS_ONLY") -> tuple[int, ...]:
    """Local final-roll model: roll the pool, keep n-1, or all on D99 bonus.

    This avoids the production decision engine.  With no bonus the lowest face
    is the deterministic reserve; improved dice have no production bonus today.
    """
    if d99_mode not in {"D99_OFF", "D99_BONUS_ONLY"}:
        raise ValueError("unknown D99 mode")
    if d99_mode == "D99_BONUS_ONLY" and has_reserve_bonus(raw_roll):
        return tuple(sorted(raw_roll, reverse=True))
    return tuple(sorted(raw_roll, reverse=True)[:-1])


def legal_partitions(dice: tuple[int, ...]) -> tuple[tuple[int, int, tuple[int, ...]], ...]:
    """Enumerate physical non-empty partitions as (EF energy, Q energy, Q indices)."""
    total = sum(dice)
    rows = []
    # Complementary allocations are represented once by requiring EF >= Q.
    for q_count in range(1, len(dice)):
        for q_indices in combinations(range(len(dice)), q_count):
            q = sum(dice[index] for index in q_indices)
            ef = total - q
            if ef >= q:
                rows.append((ef, q, q_indices))
    return tuple(rows)


def partition_features(dice: tuple[int, ...], ef: int = 6, seuil: int = 8,
                       vma: int = 10) -> list[dict]:
    safe = max(dice)
    rows = []
    for ef_energy, q_energy, indices in legal_partitions(dice):
        costs = {"SEUIL": quality_cost(seuil, ef), "VMA": quality_cost(vma, ef)}
        accessible = tuple(name for name, cost in costs.items() if q_energy >= cost)
        rows.append({
            "ef_energy": ef_energy, "q_energy": q_energy, "q_indices": indices,
            "ef_milestone": ef_energy >= EF_MILESTONES[0],
            "accessible": accessible,
            "safe": tuple(name for name in accessible if costs[name] <= safe),
            "risky": tuple(name for name in accessible if costs[name] > safe),
        })
    return rows


def experiment_a() -> dict:
    outcomes = []
    for raw in product(range(1, 7), repeat=4):
        final = resolve_roll(raw)
        partitions = partition_features(final)
        relevant = {(p["ef_energy"], p["q_energy"], p["accessible"], p["safe"], p["risky"])
                    for p in partitions}
        outcomes.append((raw, final, partitions, relevant))

    count = len(outcomes)
    pct = lambda n: round(100 * n / count, 3)
    access = lambda name, rows: any(name in p["accessible"] for p in rows)
    any_safe = lambda rows: any(p["safe"] for p in rows)
    any_risky = lambda rows: any(p["risky"] for p in rows)
    distinct_programs = [len({(p["ef_energy"], p["q_energy"], p["accessible"])
                              for p in rows}) for _, _, rows, _ in outcomes]
    result = {
        "raw_outcomes": count,
        "d99_mode": "D99_BONUS_ONLY",
        "nontrivial_partition_pct": pct(sum(bool(rows) for _, _, rows, _ in outcomes)),
        "mean_legal_partitions": round(statistics.mean(len(rows) for _, _, rows, _ in outcomes), 3),
        "multiple_relevant_partitions_pct": pct(sum(len(rel) > 1 for *_, rel in outcomes)),
        "multiple_distinct_programs_pct": pct(sum(n > 1 for n in distinct_programs)),
        "ef_milestone_access_pct": pct(sum(any(p["ef_milestone"] for p in rows)
                                               for _, _, rows, _ in outcomes)),
        "seuil_access_pct": pct(sum(access("SEUIL", rows) for _, _, rows, _ in outcomes)),
        "vma_access_pct": pct(sum(access("VMA", rows) for _, _, rows, _ in outcomes)),
        "simultaneous_access_pct": pct(sum(access("SEUIL", rows) and access("VMA", rows)
                                             for _, _, rows, _ in outcomes)),
        "safe_quality_access_pct": pct(sum(any_safe(rows) for _, _, rows, _ in outcomes)),
        "risky_quality_access_pct": pct(sum(any_risky(rows) for _, _, rows, _ in outcomes)),
    }
    examples = []
    for raw in ((1, 1, 1, 1), (1, 2, 3, 4), (2, 2, 5, 5), (2, 3, 4, 5),
                (3, 3, 3, 6), (4, 4, 5, 6), (5, 5, 6, 6), (6, 6, 6, 6)):
        final = resolve_roll(raw)
        rows = partition_features(final)
        examples.append({"raw": raw, "final": final, "partition_count": len(rows),
                         "programs": sorted({(p["ef_energy"], p["q_energy"],
                                               "/".join(p["accessible"]) or "NONE")
                                              for p in rows})})
    result["examples"] = examples
    # Operational criterion frozen for this probe: fewer than 10% rolls with
    # >1 distinct energy/access program would be structurally quasi-automatic.
    result["criterion"] = ("CHOIX QUASI AUTOMATIQUE" if result["multiple_distinct_programs_pct"] < 10
                           else "CHOIX REEL" if result["multiple_distinct_programs_pct"] >= 50
                           else "CHOIX FAIBLE")
    return result


@dataclass
class TrainingState:
    ef: int = 6
    seuil: int = 8
    vma: int = 10
    progression_ef: int = 0
    progression_q: int = 0
    pool: tuple[int, ...] = (6, 6, 6, 6)
    upgrades: int = 0
    risky_attempts: int = 0
    busts: int = 0


def _percentile(values: list[int], proportion: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * proportion
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower), 3)


def _choose_partition(state: TrainingState, final: tuple[int, ...], policy: str) -> tuple[dict, str | None]:
    candidates = partition_features(final, state.ef, state.seuil, state.vma)
    priorities = {
        "P_EF": ("EF", "SEUIL", "VMA"),
        "P_QUALITY": ("VMA", "SEUIL", "EF"),
    }
    if policy == "P_BALANCED":
        # Relative lag from starting values; deterministic ties EF, Seuil, VMA.
        starts = {"EF": 6, "SEUIL": 8, "VMA": 10}
        current = {"EF": state.ef, "SEUIL": state.seuil, "VMA": state.vma}
        order = tuple(sorted(current, key=lambda name: ((current[name] - starts[name]) / starts[name],
                                                        ("EF", "SEUIL", "VMA").index(name))))
    else:
        order = priorities[policy]

    def accessible(row: dict, target: str) -> bool:
        if target == "EF":
            return row["ef_milestone"] and state.ef + 1 < state.seuil
        marker = state.seuil if target == "SEUIL" else state.vma
        if target == "SEUIL" and state.seuil + 1 >= state.vma:
            return False
        return row["q_energy"] >= quality_cost(marker, state.ef)

    target = next((name for name in order if any(accessible(row, name) for row in candidates)), None)
    eligible = [row for row in candidates if target is None or accessible(row, target)]
    # Maximise the target compartment, then minimise surplus, then physical indices.
    if target == "EF":
        key = lambda row: (-row["ef_energy"], row["q_energy"], row["q_indices"])
    else:
        key = lambda row: (-row["q_energy"], row["ef_energy"], row["q_indices"])
    return min(eligible, key=key), target


def _apply_milestones(state: TrainingState, old_ef: int, old_q: int) -> None:
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
                index = min(eligible, key=lambda i: (state.pool[i], i))  # spread, deterministic
                pool = list(state.pool)
                pool[index] = SIZE_SEQUENCE[SIZE_SEQUENCE.index(pool[index]) + 1]
                state.pool = tuple(pool)
                state.upgrades += 1


def simulate(seed: int, policy: str, turns: int = 16) -> tuple[dict, list[dict]]:
    rng = random.Random(seed)
    state = TrainingState()
    trajectory = []
    for turn in range(1, turns + 1):
        raw = tuple(rng.randint(1, size) for size in state.pool)
        final = resolve_roll(raw)
        row, target = _choose_partition(state, final, policy)
        old_ef, old_q = state.progression_ef, state.progression_q
        state.progression_ef += row["ef_energy"]
        quality_succeeded = target in {"SEUIL", "VMA"}
        if quality_succeeded:
            marker = state.seuil if target == "SEUIL" else state.vma
            cost = quality_cost(marker, state.ef)
            if cost > max(final):
                state.risky_attempts += 1
                k = cost - max(final)
                # Exact CURRENT principle, local RNG: raw best-pool-die face <= k busts.
                quality_succeeded = rng.randint(1, max(state.pool)) > k
                if not quality_succeeded:
                    state.busts += 1
            if quality_succeeded:
                if target == "SEUIL":
                    state.seuil += 1
                else:
                    state.vma += 1
                state.progression_q += row["q_energy"]
        _apply_milestones(state, old_ef, old_q)
        trajectory.append({"turn": turn, "ef": state.ef, "seuil": state.seuil, "vma": state.vma,
                           "progression_ef": state.progression_ef, "progression_q": state.progression_q,
                           "pool": state.pool, "target": target, "busts": state.busts})
    record = {"seed": seed, "policy": policy, "EF": state.ef, "SEUIL": state.seuil,
              "VMA": state.vma, "progression_EF": state.progression_ef,
              "progression_Q": state.progression_q, "dice_count": len(state.pool),
              "pool": " + ".join(f"d{s}" for s in state.pool), "upgrades": state.upgrades,
              "risky_attempts": state.risky_attempts, "busts": state.busts}
    return record, trajectory


def experiment_b() -> dict:
    metrics = ("EF", "SEUIL", "VMA", "progression_EF", "progression_Q", "dice_count",
               "upgrades", "risky_attempts", "busts")
    output = {"seeds": 200, "turns": 16, "d99_mode": "D99_BONUS_ONLY", "policies": {}}
    for policy in ("P_EF", "P_BALANCED", "P_QUALITY"):
        records, trajectories = zip(*(simulate(seed, policy) for seed in range(200)))
        summary = {}
        for metric in metrics:
            values = [row[metric] for row in records]
            summary[metric] = {"mean": round(statistics.mean(values), 3), "p10": _percentile(values, .1),
                               "median": _percentile(values, .5), "p90": _percentile(values, .9)}
        summary["final_pool_composition"] = dict(sorted(Counter(row["pool"] for row in records).items()))
        six_die_turns = [next(step["turn"] for step in trajectory if len(step["pool"]) == 6)
                          for trajectory in trajectories]
        four_upgrade_turns = [next((step["turn"] for step in trajectory
                                    if sum(size > 6 for size in step["pool"]) == 4), None)
                              for trajectory in trajectories]
        summary["timing_diagnostics"] = {
            "six_dice_turn_median": _percentile(six_die_turns, .5),
            "six_dice_by_turn_10_pct": round(100 * sum(turn <= 10 for turn in six_die_turns) / 200, 3),
            "four_upgrades_by_turn_16_pct": round(100 * sum(turn is not None for turn in four_upgrade_turns) / 200, 3),
            "all_markers_advanced_pct": round(100 * sum(row["EF"] > 6 and row["SEUIL"] > 8 and row["VMA"] > 10
                                                           for row in records) / 200, 3),
        }
        summary["example_trajectories"] = {str(seed): trajectories[seed] for seed in (0, 73, 199)}
        output["policies"][policy] = summary
    return output


def experiment_c() -> dict:
    # Fixed analytical fixtures only: AS42 is lower intensity/longer duration;
    # AS10 is higher intensity/shorter duration. ECO subtracts cost per repeat.
    contexts = {"AS42_LOW": {"as": 18, "repetitions": 10},
                "AS10_HIGH": {"as": 23, "repetitions": 4}}
    profiles = {"FULL_SPEED": {"speed": 4, "eco": 0},
                "BALANCED": {"speed": 2, "eco": -2},
                "FULL_ECO": {"speed": 0, "eco": -4}}
    rows = []
    for context, fixture in contexts.items():
        for profile, allocation in profiles.items():
            target_as = fixture["as"] + allocation["speed"]
            local = {}
            for offset in (-1, 0, 1):
                production = target_as + offset
                base = energy_cost(production, "B")
                adjusted = max(0, base + allocation["eco"])
                local[str(offset)] = {"production": production, "cost": adjusted,
                                      "base_cost": base, "production_gain": production - fixture["as"]}
            rows.append({"context": context, "profile": profile, **allocation,
                         "repetitions": fixture["repetitions"], "around_as": local,
                         "reserve_cost_repeated_at_as": local["0"]["cost"] * fixture["repetitions"],
                         "reserve_saved_vs_no_eco": (local["0"]["base_cost"] - local["0"]["cost"])
                                                    * fixture["repetitions"]})
    return {"curve": "Race Engine V2 Curve B", "spec_points": 4, "rows": rows}


def run_all() -> dict:
    a = experiment_a()
    results = {"status": "EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN", "A": a}
    if a["criterion"] != "CHOIX QUASI AUTOMATIQUE":
        results["B"] = experiment_b()
        results["C"] = experiment_c()
    return results


if __name__ == "__main__":
    destination = Path(__file__).with_name("results.json")
    destination.write_text(json.dumps(run_all(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(destination)
