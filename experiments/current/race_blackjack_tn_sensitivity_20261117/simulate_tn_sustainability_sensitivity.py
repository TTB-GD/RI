#!/usr/bin/env python3
"""Standalone TN × initial-sustainability sensitivity simulation.

Uses only the Python standard library. The physiological energy/sustainability
curve is fixed; TN only caps the Blackjack target.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import mean, stdev

SUSTAINABILITY_COST = {
    9: 1, 10: 1, 11: 2, 12: 3, 13: 4,
    14: 5, 15: 7, 16: 10, 17: 13,
}
TN_VALUES = tuple(range(9, 15))
DEFAULT_RESERVES = (8, 16, 24)
INITIAL_POOL = 4
DEFAULT_TURNS = 8
DEFAULT_REROLLS = 8


def energy_cost(raw_total: int) -> int:
    """Cost on the fixed EF=9 / VMA=17 curve."""
    if raw_total < 9:
        return 0
    return SUSTAINABILITY_COST[min(raw_total, 17)]


def energy_output(raw_total: int) -> int:
    """Energy output; below EF is capped at 8 and above VMA at 17."""
    if raw_total < 9:
        return min(raw_total, 8)
    return min(raw_total, 17)


def long_term_target(sustainability: int, turns_left: int) -> int:
    """Highest energy affordable under the average remaining-turn budget."""
    if sustainability <= 0:
        return 8
    budget = math.ceil(sustainability / turns_left)
    affordable = [
        energy for energy in range(9, 18)
        if energy_cost(energy) <= budget
    ]
    return max(affordable) if affordable else 8


def play_course(
    tn: int,
    initial_sustainability: int,
    turns: int,
    reroll_reserve: int,
    rng: random.Random,
) -> tuple[int, int, int, int, int]:
    """Return energy, sustainability spent, dice lost, rerolls, EF-locked turns."""
    pool = INITIAL_POOL
    sustainability = initial_sustainability
    rerolls_left = reroll_reserve
    energy_total = sustainability_spent = dice_lost = rerolls_used = 0
    ef_locked_turns = 0

    for turn_index in range(turns):
        if sustainability <= 0:
            energy_total += 8
            ef_locked_turns += 1
            continue

        turns_left = turns - turn_index
        target = min(tn, long_term_target(sustainability, turns_left))

        # Blackjack sequence: roll N-2 dice, then add dice one at a time.
        dice = [rng.randint(1, 6) for _ in range(max(1, pool - 2))]
        rerolled = [False] * len(dice)

        while True:
            raw_total = sum(dice)
            affordable = energy_cost(raw_total) <= sustainability

            # Correct overshoots by rerolling the highest eligible die.
            if raw_total > target and rerolls_left > 0:
                candidates = [
                    i for i, already_rerolled in enumerate(rerolled)
                    if not already_rerolled
                ]
                if candidates:
                    index = max(candidates, key=lambda i: dice[i])
                    dice[index] = rng.randint(1, 6)
                    rerolled[index] = True
                    rerolls_left -= 1
                    rerolls_used += 1
                    continue

            # An unaffordable overshoot ends the turn at EF.
            if raw_total > target and not affordable:
                break
            if raw_total >= target and affordable:
                break

            if len(dice) < pool:
                dice.append(rng.randint(1, 6))
                rerolled.append(False)
                continue

            # With a full pool and a result below target, improve the
            # smallest die that has not already been rerolled this turn.
            candidates = [
                i for i, already_rerolled in enumerate(rerolled)
                if not already_rerolled
            ]
            if rerolls_left > 0 and candidates:
                index = min(candidates, key=lambda i: dice[i])
                dice[index] = rng.randint(1, 6)
                rerolled[index] = True
                rerolls_left -= 1
                rerolls_used += 1
                continue
            break

        raw_total = sum(dice)
        cost = energy_cost(raw_total)
        if cost > sustainability:
            energy_total += 8
            ef_locked_turns += 1
        else:
            energy_total += energy_output(raw_total)
            sustainability -= cost
            sustainability_spent += cost
            if sustainability == 0:
                pool = max(1, pool - 1)
                dice_lost += 1

    return (
        energy_total,
        sustainability_spent,
        dice_lost,
        rerolls_used,
        ef_locked_turns,
    )


def cell_seed(base_seed: int, reserve: int, tn: int) -> int:
    """Stable independent random stream for each reserve/TN cell."""
    return base_seed + reserve * 1_000_003 + tn * 9_176


def simulate_cell(
    tn: int,
    reserve: int,
    runs: int,
    turns: int,
    rerolls: int,
    seed: int,
) -> dict:
    rng = random.Random(seed)
    samples = [
        play_course(tn, reserve, turns, rerolls, rng)
        for _ in range(runs)
    ]
    energy_values = [sample[0] for sample in samples]
    energy_mean = mean(energy_values)
    energy_sd = stdev(energy_values) if runs > 1 else 0.0
    standard_error = energy_sd / math.sqrt(runs)

    return {
        "initial_sustainability": reserve,
        "tn": tn,
        "runs": runs,
        "seed": seed,
        "mean_energy": energy_mean,
        "sd_energy": energy_sd,
        "se_energy": standard_error,
        "ci95_energy": [
            energy_mean - 1.96 * standard_error,
            energy_mean + 1.96 * standard_error,
        ],
        "mean_sustainability_spent": mean(sample[1] for sample in samples),
        "mean_dice_lost": mean(sample[2] for sample in samples),
        "mean_rerolls_used": mean(sample[3] for sample in samples),
        "mean_ef_locked_turns": mean(sample[4] for sample in samples),
    }


def run_experiment(
    runs: int,
    seed: int,
    reserves: tuple[int, ...],
    turns: int,
    rerolls: int,
) -> dict:
    results = []
    for reserve in reserves:
        for tn in TN_VALUES:
            results.append(
                simulate_cell(
                    tn=tn,
                    reserve=reserve,
                    runs=runs,
                    turns=turns,
                    rerolls=rerolls,
                    seed=cell_seed(seed, reserve, tn),
                )
            )

    return {
        "experiment": "Blackjack TN × initial sustainability sensitivity",
        "seed": seed,
        "configuration": {
            "tn_values": list(TN_VALUES),
            "initial_sustainability_values": list(reserves),
            "turns": turns,
            "initial_pool": "4d6",
            "reroll_reserve": rerolls,
            "ef_energy": 9,
            "vma_energy": 17,
            "sustainability_curve": {
                str(key): value for key, value in SUSTAINABILITY_COST.items()
            },
            "policy": (
                "Long-term heuristic: effective target is the minimum of TN "
                "and the highest energy affordable with "
                "ceil(remaining sustainability / turns remaining)."
            ),
            "reroll_rule": (
                "Shared course reserve; each die can be rerolled at most once "
                "per turn; reroll replaces the previous result."
            ),
            "depletion_rule": (
                "When sustainability reaches exactly zero, one die is lost; "
                "all subsequent turns are locked to energy 8."
            ),
            "unaffordable_rule": (
                "If final cost exceeds remaining sustainability, output is "
                "locked to energy 8 and no sustainability is spent."
            ),
            "random_streams": (
                "A deterministic independent stream is used for each "
                "reserve/TN combination."
            ),
        },
        "results": results,
        "caveat": "Explicit heuristic, not an optimal-play solver.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate TN 9–14 for initial sustainability reserves "
            "8, 16 and 24. Standard library only."
        )
    )
    parser.add_argument("--runs", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument(
        "--reserves", type=int, nargs="+", default=list(DEFAULT_RESERVES),
        help="Initial sustainability values (default: 8 16 24).",
    )
    parser.add_argument("--turns", type=int, default=DEFAULT_TURNS)
    parser.add_argument("--rerolls", type=int, default=DEFAULT_REROLLS)
    parser.add_argument(
        "--output", type=Path,
        default=Path("tn_sustainability_sensitivity_results.json"),
    )
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.turns < 1:
        parser.error("--turns must be at least 1")
    if args.rerolls < 0 or any(value < 0 for value in args.reserves):
        parser.error("--rerolls and --reserves must be non-negative")

    data = run_experiment(
        runs=args.runs,
        seed=args.seed,
        reserves=tuple(args.reserves),
        turns=args.turns,
        rerolls=args.rerolls,
    )
    args.output.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Résultats écrits dans : {args.output}")
    print("Réserve | TN | Énergie moyenne | Soutenabilité consommée | Dés perdus | Relances | Tours EF")
    for row in data["results"]:
        print(
            f'{row["initial_sustainability"]:7d} | {row["tn"]:2d} | '
            f'{row["mean_energy"]:15.4f} | '
            f'{row["mean_sustainability_spent"]:23.4f} | '
            f'{row["mean_dice_lost"]:10.4f} | '
            f'{row["mean_rerolls_used"]:8.4f} | '
            f'{row["mean_ef_locked_turns"]:8.4f}'
        )


if __name__ == "__main__":
    main()
