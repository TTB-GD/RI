#!/usr/bin/env python3
"""Reproduce the long-term Blackjack TN sensitivity experiment."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

SUSTAINABILITY = {
    9: 1, 10: 1, 11: 2, 12: 3, 13: 4,
    14: 5, 15: 7, 16: 10, 17: 13,
}
TNS = range(9, 15)
INITIAL_POOL = 4
INITIAL_SUSTAINABILITY = 8
TURNS = 8
REROLL_RESERVE = 8


def energy_cost(raw_sum: int) -> int:
    """Cost on the fixed EF=9 / VMA=17 curve."""
    if raw_sum < 9:
        return 0
    return SUSTAINABILITY[min(raw_sum, 17)]


def energy_output(raw_sum: int) -> int:
    """Energy output on the fixed curve."""
    if raw_sum < 9:
        return min(raw_sum, 8)
    return min(raw_sum, 17)


def long_term_target(durability: int, turns_left: int) -> int:
    """Highest energy affordable under the per-turn long-term budget."""
    if durability <= 0:
        return 8
    budget = math.ceil(durability / turns_left)
    feasible = [
        energy for energy in range(9, 18)
        if energy_cost(energy) <= budget
    ]
    return max(feasible) if feasible else 8


def play_course(tn: int, rng: np.random.Generator) -> tuple[int, int, int, int, int]:
    """Play one course. TN caps the Blackjack target; it does not move the curve."""
    pool = INITIAL_POOL
    durability = INITIAL_SUSTAINABILITY
    tokens = REROLL_RESERVE
    total_energy = total_sustainability = dice_lost = rerolls_used = locked_turns = 0

    for turn_index in range(TURNS):
        if durability <= 0:
            total_energy += 8
            locked_turns += 1
            continue

        turns_left = TURNS - turn_index
        goal = min(tn, long_term_target(durability, turns_left))

        # Blackjack: roll N-2 dice, then add remaining dice one at a time.
        dice = [
            int(x) for x in rng.integers(1, 7, size=max(1, pool - 2))
        ]
        rerolled = [False] * len(dice)

        while True:
            raw_sum = sum(dice)
            affordable = energy_cost(raw_sum) <= durability

            # Long-term policy corrects overshoots of the effective target.
            if raw_sum > goal and tokens > 0:
                candidates = [
                    i for i, already_rerolled in enumerate(rerolled)
                    if not already_rerolled
                ]
                if candidates:
                    index = max(candidates, key=lambda i: dice[i])
                    dice[index] = int(rng.integers(1, 7))
                    rerolled[index] = True
                    tokens -= 1
                    rerolls_used += 1
                    continue

            # If the result is still unaffordable, the turn ends EF-locked.
            if raw_sum > goal and not affordable:
                break

            if raw_sum >= goal and affordable:
                break

            if len(dice) < pool:
                dice.append(int(rng.integers(1, 7)))
                rerolled.append(False)
                continue

            candidates = [
                i for i, already_rerolled in enumerate(rerolled)
                if not already_rerolled
            ]
            if tokens > 0 and candidates:
                # Under target with a full pool: improve the smallest die.
                index = min(candidates, key=lambda i: dice[i])
                dice[index] = int(rng.integers(1, 7))
                rerolled[index] = True
                tokens -= 1
                rerolls_used += 1
                continue
            break

        raw_sum = sum(dice)
        cost = energy_cost(raw_sum)
        if cost > durability:
            total_energy += 8
            locked_turns += 1
        else:
            total_energy += energy_output(raw_sum)
            durability -= cost
            total_sustainability += cost
            if durability == 0:
                pool = max(1, pool - 1)
                dice_lost += 1

    return (
        total_energy, total_sustainability, dice_lost,
        rerolls_used, locked_turns,
    )


def run(runs: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    rows = []
    for tn in TNS:
        samples = np.asarray(
            [play_course(tn, rng) for _ in range(runs)],
            dtype=float,
        )
        energy = samples[:, 0]
        mean = float(energy.mean())
        sd = float(energy.std(ddof=1))
        se = sd / math.sqrt(runs)
        rows.append({
            "tn": tn,
            "runs": runs,
            "mean_energy": mean,
            "sd_energy": sd,
            "se_energy": se,
            "ci95_energy": [mean - 1.96 * se, mean + 1.96 * se],
            "mean_sustainability_spent": float(samples[:, 1].mean()),
            "mean_dice_lost": float(samples[:, 2].mean()),
            "mean_rerolls_used": float(samples[:, 3].mean()),
            "mean_ef_locked_turns": float(samples[:, 4].mean()),
        })

    return {
        "model": {
            "initial_pool": "4d6",
            "tn_range": [9, 14],
            "tn_role": "Blackjack target only; effective target is min(TN, long-term affordable target)",
            "ef_energy": 9,
            "vma_energy": 17,
            "sustainability_curve": {
                str(key): value for key, value in SUSTAINABILITY.items()
            },
            "below_ef": "raw energy below 9 costs 0 and output is capped at 8",
            "above_vma": "output capped at 17 and cost fixed at 13",
            "initial_sustainability": INITIAL_SUSTAINABILITY,
            "turns": TURNS,
            "reroll_reserve": REROLL_RESERVE,
            "policy": "Long-term heuristic: highest energy affordable with ceil(remaining sustainability / turns remaining), capped by TN",
            "reroll_rule": "shared course reserve; each die at most once per turn; reroll replaces its result",
            "reserve_depletion": "when sustainability reaches 0, one die is removed and all remaining turns are locked to output 8",
            "unaffordable_result": "output is locked to 8 for the turn; no sustainability is spent",
        },
        "seed": seed,
        "results": rows,
        "caveat": "Explicit heuristic, not an optimal-play solver.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    data = run(args.runs, args.seed)
    args.output.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for row in data["results"]:
        print(row)
