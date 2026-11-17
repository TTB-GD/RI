#!/usr/bin/env python3
"""Reproducible Monte Carlo comparison for the 4d6 / 8-turn Blackjack Race test.

Run: python simulate.py --runs 50000 --seed 20261117 --output results.json

The two player policies are explicit heuristics, not optimal-play solvers.
"""
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
INITIAL_POOL = 4
INITIAL_SUSTAINABILITY = 8
TURNS = 8
REROLL_RESERVES = (0, 4, 8)


def energy_cost(raw_sum: int) -> int:
    if raw_sum < 9:
        return 0
    return SUSTAINABILITY[min(raw_sum, 17)]


def energy_output(raw_sum: int) -> int:
    if raw_sum < 9:
        return min(raw_sum, 8)
    return min(raw_sum, 17)


def target_for(policy: str, durability: int, turns_left: int) -> int:
    if durability <= 0:
        return 8
    budget = durability if policy == "opportunistic" else math.ceil(durability / turns_left)
    feasible = [energy for energy in range(9, 18)
                if energy_cost(energy) <= budget]
    return max(feasible) if feasible else 8


def play_course(token_reserve: int, policy: str, rng: np.random.Generator) -> dict:
    pool = INITIAL_POOL
    durability = INITIAL_SUSTAINABILITY
    tokens = token_reserve
    total_energy = total_sustainability = dice_lost = rerolls_used = ef_locked_turns = 0

    for turn_index in range(TURNS):
        if durability <= 0:
            total_energy += 8
            ef_locked_turns += 1
            continue

        turns_left = TURNS - turn_index
        target = target_for(policy, durability, turns_left)

        # Blackjack: roll N-2 dice, then decide whether to add the remaining dice.
        initial_count = max(1, pool - 2)
        dice = [int(x) for x in rng.integers(1, 7, size=initial_count)]
        rerolled = [False] * len(dice)

        while True:
            raw_sum = sum(dice)
            feasible = energy_cost(raw_sum) <= durability

            # Long-term policy corrects any overshoot of its planned target.
            if policy == "long_term" and raw_sum > target and tokens > 0:
                candidates = [i for i, used in enumerate(rerolled) if not used]
                if candidates:
                    index = max(candidates, key=lambda i: dice[i])
                    dice[index] = int(rng.integers(1, 7))
                    rerolled[index] = True
                    tokens -= 1
                    rerolls_used += 1
                    continue

            # An unaffordable result must be corrected or the player is EF-locked this turn.
            if raw_sum > target and not feasible:
                candidates = [i for i, used in enumerate(rerolled) if not used]
                if tokens > 0 and candidates:
                    index = max(candidates, key=lambda i: dice[i])
                    dice[index] = int(rng.integers(1, 7))
                    rerolled[index] = True
                    tokens -= 1
                    rerolls_used += 1
                    continue
                break

            if raw_sum >= target and feasible:
                break

            if len(dice) < pool:
                dice.append(int(rng.integers(1, 7)))
                rerolled.append(False)
                continue

            candidates = [i for i, used in enumerate(rerolled) if not used]
            if tokens > 0 and candidates:
                index = (max(candidates, key=lambda i: dice[i])
                         if not feasible or raw_sum > target
                         else min(candidates, key=lambda i: dice[i]))
                dice[index] = int(rng.integers(1, 7))
                rerolled[index] = True
                tokens -= 1
                rerolls_used += 1
                continue
            break

        raw_sum = sum(dice)
        cost = energy_cost(raw_sum)
        if cost > durability:
            output = 8
            ef_locked_turns += 1
        else:
            output = energy_output(raw_sum)
            durability -= cost
            total_sustainability += cost
            if durability == 0:
                pool = max(1, pool - 1)
                dice_lost += 1

        total_energy += output

    return {
        "energy": total_energy,
        "sustainability_spent": total_sustainability,
        "dice_lost": dice_lost,
        "rerolls_used": rerolls_used,
        "ef_locked_turns": ef_locked_turns,
    }


def run(runs: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    results = []
    for policy in ("opportunistic", "long_term"):
        for reserve in REROLL_RESERVES:
            samples = [play_course(reserve, policy, rng) for _ in range(runs)]
            energy = np.array([sample["energy"] for sample in samples], dtype=float)
            results.append({
                "policy": policy,
                "reroll_reserve": reserve,
                "runs": runs,
                "mean_energy": float(energy.mean()),
                "se_energy": float(energy.std(ddof=1) / math.sqrt(runs)),
                "sd_energy": float(energy.std(ddof=1)),
                "mean_sustainability_spent": float(np.mean([s["sustainability_spent"] for s in samples])),
                "mean_dice_lost": float(np.mean([s["dice_lost"] for s in samples])),
                "mean_rerolls_used": float(np.mean([s["rerolls_used"] for s in samples])),
                "mean_ef_locked_turns": float(np.mean([s["ef_locked_turns"] for s in samples])),
            })
    return {
        "model": {
            "initial_pool": "4d6",
            "target_number": 14,
            "ef_energy": 9,
            "vma_energy": 17,
            "initial_sustainability": 8,
            "turns": 8,
            "sustainability_curve": {str(k): v for k, v in SUSTAINABILITY.items()},
            "below_ef": "raw energy below 9 costs 0 and output is capped at 8",
            "above_vma": "output capped at 17 and cost fixed at 13",
            "unaffordable_result": "output is locked to 8 for the turn; no sustainability is spent",
            "reserve_depletion": "when sustainability reaches 0, one die is removed and all remaining turns are locked to output 8",
            "reroll_rule": "shared course reserve; each die can be rerolled at most once per turn; reroll replaces its result",
        },
        "policies": {
            "opportunistic": "At each turn, target the highest energy level affordable with the current remaining sustainability. Correct only results whose cost exceeds the remaining reserve.",
            "long_term": "At each turn, target the highest energy level affordable with ceil(remaining sustainability / turns left). Correct overshoots of that target with available rerolls.",
            "caveat": "Both are explicit heuristic policies, not optimal strategies. Rerolls are used sequentially; no die is rerolled twice in a turn.",
        },
        "seed": seed,
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    data = run(args.runs, args.seed)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for row in data["results"]:
        print(row)
