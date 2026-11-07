"""EXPERIMENTAL — compare D/P/H allocation architectures on common dice rolls.

D: assign every retained die directly to a session occurrence.
P: split retained dice into EF and Quality budgets; no session catalogue.
H: split budgets first, then buy catalogue sessions from their matching budget.

Isolated from production Training. D99_OFF retains the highest n-1 dice.
Fixed pool 4d6; provisional catalogue costs: EF=2, Seuil=4, VMA=5.
No risk/bust or persistent fatigue regulation is modelled.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations, product
import json
import statistics

SESSION_COST = {"EF": 2, "SEUIL": 4, "VMA": 5}
SESSION_FATIGUE = {"EF": 0, "SEUIL": 0, "VMA": 1}
POOL = (6, 6, 6, 6)


def retained_dice(raw_faces):
    if len(raw_faces) < 2:
        raise ValueError("at least two dice are required")
    if any(face < 1 or face > 6 for face in raw_faces):
        raise ValueError("raw faces must be valid d6 results")
    return tuple(sorted(raw_faces, reverse=True)[:-1])


def _set_partitions(items):
    if not items:
        yield ()
        return
    first, *rest = items
    for partition in _set_partitions(tuple(rest)):
        yield ((first,),) + partition
        for index in range(len(partition)):
            blocks = list(partition)
            blocks[index] = (first,) + blocks[index]
            yield tuple(blocks)


def _direct_programs(dice):
    """Every retained die funds exactly one session occurrence."""
    signatures = set()
    keys = tuple(SESSION_COST)
    for blocks in _set_partitions(tuple(range(len(dice)))):
        for names in product(keys, repeat=len(blocks)):
            counts = Counter(names)
            if counts["SEUIL"] > 1 or counts["VMA"] > 1:
                continue
            sessions = []
            for block, name in zip(blocks, names):
                energy = sum(dice[index] for index in block)
                if energy < SESSION_COST[name]:
                    break
                sessions.append((name, energy))
            else:
                signatures.add(tuple(sorted(sessions)))
    return signatures


def _budget_splits(dice):
    """All EF/Quality splits, including zero budget in either compartment."""
    splits = set()
    indices = range(len(dice))
    for count in range(len(dice) + 1):
        for quality_indices in combinations(indices, count):
            quality_set = set(quality_indices)
            quality = sum(value for i, value in enumerate(dice) if i in quality_set)
            ef = sum(dice) - quality
            splits.add((ef, quality))
    return splits


def _catalogue_programs(ef_budget, quality_budget):
    """H programmes: EF repeats; Seuil and VMA each occur at most once."""
    max_ef = ef_budget // SESSION_COST["EF"]
    for ef_count in range(max_ef + 1):
        for seuil_count, vma_count in product((0, 1), repeat=2):
            ef_spent = ef_count * SESSION_COST["EF"]
            quality_spent = (seuil_count * SESSION_COST["SEUIL"]
                             + vma_count * SESSION_COST["VMA"])
            if ef_spent <= ef_budget and quality_spent <= quality_budget:
                yield (ef_count, seuil_count, vma_count, ef_spent, quality_spent)


def _fatigue_blackjack(energy, tn):
    """Mirror current decision_engine curve for integer 4d6 energy/TN."""
    offset = int(energy - tn)
    if offset >= -1:
        fib = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
        index = offset + 3
        return fib[index] if 0 <= index < len(fib) else fib[-1]
    if offset in (-2, -3):
        return 0
    recovery = {-4: -1, -5: -1, -6: -2, -7: -2, -8: -3, -9: -5}
    return recovery.get(offset, -8)


def _imbalance(ef_energy, quality_energy):
    excess = max(0, quality_energy - ef_energy)
    return (excess + 1) // 2


def _percentile(values, p):
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo), 3)


def _summary(values):
    return {
        "mean": round(statistics.mean(values), 3),
        "p10": _percentile(values, 0.10),
        "median": _percentile(values, 0.50),
        "p90": _percentile(values, 0.90),
    }


def _evaluate_roll(raw):
    dice = retained_dice(raw)
    tn = sum((size + 1) / 2 for size in POOL)
    energy = sum(dice)
    blackjack = _fatigue_blackjack(energy, tn)
    d_programs = _direct_programs(dice)
    splits = _budget_splits(dice)
    h_programs = set()
    h_rows = []
    for ef_budget, q_budget in splits:
        for ef_count, seuil_count, vma_count, ef_spent, q_spent in _catalogue_programs(
            ef_budget, q_budget
        ):
            signature = (ef_budget, q_budget, ef_count, seuil_count, vma_count)
            h_programs.add(signature)
            h_rows.append({
                "ef_budget": ef_budget, "quality_budget": q_budget,
                "ef_count": ef_count, "seuil_count": seuil_count,
                "vma_count": vma_count, "ef_spent": ef_spent,
                "quality_spent": q_spent,
                "ef_remainder": ef_budget - ef_spent,
                "quality_remainder": q_budget - q_spent,
                "imbalance_allocated": _imbalance(ef_budget, q_budget),
                "imbalance_spent": _imbalance(ef_spent, q_spent),
                "progression_tokens": {
                    "EF": ef_count, "Seuil": seuil_count, "VMA": vma_count
                },
                "session_fatigue": vma_count * SESSION_FATIGUE["VMA"],
            })
    return {
        "raw": raw, "retained": dice, "tn": tn, "energy": energy,
        "fatigue_blackjack": blackjack,
        "D": {"programme_count": len(d_programs),
              "quality_access": any(
                  any(name in ("SEUIL", "VMA") for name, _ in p)
                  for p in d_programs)},
        "P": {"split_count": len(splits),
              "ef_gt_quality_split_pct": round(
                  100 * sum(ef > q for ef, q in splits) / max(1, len(splits)), 3)},
        "H": {
            "programme_count": len(h_programs),
            "seuil_access": any(row["seuil_count"] for row in h_rows),
            "vma_access": any(row["vma_count"] for row in h_rows),
            "both_quality_types_access": any(
                row["seuil_count"] and row["vma_count"] for row in h_rows),
            "mean_imbalance_allocated": round(
                statistics.mean(row["imbalance_allocated"] for row in h_rows), 3
            ) if h_rows else 0,
            "mean_imbalance_spent": round(
                statistics.mean(row["imbalance_spent"] for row in h_rows), 3
            ) if h_rows else 0,
            "example_programmes": h_rows[:8],
        },
    }


def run_experiment():
    """Exhaust all 6^4 raw 4d6 rolls under common D99_OFF conditions."""
    rows = [_evaluate_roll(raw) for raw in product(range(1, 7), repeat=4)]
    d_counts = [row["D"]["programme_count"] for row in rows]
    p_counts = [row["P"]["split_count"] for row in rows]
    h_counts = [row["H"]["programme_count"] for row in rows]
    return {
        "status": "EXPERIMENTAL — NOT A DESIGN DECISION",
        "rolls": len(rows), "pool": "4d6",
        "d99": "OFF — retain highest three dice",
        "catalogue": SESSION_COST,
        "tn": sum((size + 1) / 2 for size in POOL),
        "metrics": {
            "D_direct_programmes_per_roll": _summary(d_counts),
            "P_budget_splits_per_roll": _summary(p_counts),
            "H_catalogue_programmes_per_roll": _summary(h_counts),
            "H_rolls_with_multiple_programmes_pct": round(
                100 * sum(count > 1 for count in h_counts) / len(rows), 3),
            "H_rolls_with_no_programme_pct": round(
                100 * sum(count == 0 for count in h_counts) / len(rows), 3),
            "H_seuil_access_pct": round(
                100 * sum(row["H"]["seuil_access"] for row in rows) / len(rows), 3),
            "H_vma_access_pct": round(
                100 * sum(row["H"]["vma_access"] for row in rows) / len(rows), 3),
            "H_both_quality_types_access_pct": round(
                100 * sum(row["H"]["both_quality_types_access"] for row in rows) / len(rows), 3),
            "H_mean_imbalance_allocated": round(
                statistics.mean(row["H"]["mean_imbalance_allocated"] for row in rows), 3),
            "H_mean_imbalance_spent": round(
                statistics.mean(row["H"]["mean_imbalance_spent"] for row in rows), 3),
            "blackjack_fatigue_by_energy": dict(sorted(Counter(
                row["fatigue_blackjack"] for row in rows).items())),
        },
        "examples": [
            _evaluate_roll(raw)
            for raw in ((1, 1, 1, 1), (1, 2, 3, 4), (2, 2, 5, 5),
                        (3, 3, 3, 6), (4, 4, 5, 6), (5, 5, 6, 6),
                        (6, 6, 6, 6))
        ],
        "limitations": [
            "D99 is disabled to isolate allocation architecture.",
            "No risk/bust resolution; sessions are treated as completed.",
            "Progression is reported as track tokens; profile values do not change.",
            "Fatigue is diagnostic only; no persistent regulation between turns.",
            "EF > Quality is measured, not imposed as a hard legality constraint.",
            "Session costs and penalties are provisional catalogue fixtures.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_experiment(), indent=2, ensure_ascii=False))
