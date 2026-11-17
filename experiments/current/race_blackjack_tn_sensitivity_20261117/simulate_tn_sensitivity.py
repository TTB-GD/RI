#!/usr/bin/env python3
"""Reproduce the long-term Blackjack TN sensitivity experiment."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

COSTS = (1, 1, 2, 3, 4, 5, 7, 10, 13)
TNS = range(9, 15)


def cost(raw: int, tn: int) -> int:
    ef = tn - 5
    return 0 if raw < ef else COSTS[min(raw - ef, 8)]


def output(raw: int, tn: int) -> int:
    ef, vma = tn - 5, tn + 3
    return min(raw, ef - 1) if raw < ef else min(raw, vma)


def target(durability: int, turns_left: int, tn: int) -> int:
    ef, vma = tn - 5, tn + 3
    if durability <= 0:
        return ef - 1
    budget = math.ceil(durability / turns_left)
    feasible = [e for e in range(ef, vma + 1) if cost(e, tn) <= budget]
    return max(feasible) if feasible else ef - 1


def play(tn: int, rng: np.random.Generator) -> tuple[int, int, int, int, int]:
    pool, durability, rerolls = 4, 8, 8
    energy = spent = lost = used = locked = 0
    ef = tn - 5
    for turn in range(8):
        if durability <= 0:
            energy += ef - 1
            locked += 1
            continue
        goal = target(durability, 8 - turn, tn)
        dice = [int(x) for x in rng.integers(1, 7, size=max(1, pool - 2))]
        rerolled = [False] * len(dice)
        while True:
            total = sum(dice)
            affordable = cost(total, tn) <= durability
            if total > goal and rerolls > 0:
                candidates = [i for i, done in enumerate(rerolled) if not done]
                if candidates:
                    i = max(candidates, key=lambda j: dice[j])
                    dice[i] = int(rng.integers(1, 7))
                    rerolled[i] = True
                    rerolls -= 1
                    used += 1
                    continue
            if total > goal and not affordable:
                candidates = [i for i, done in enumerate(rerolled) if not done]
                if rerolls > 0 and candidates:
                    i = max(candidates, key=lambda j: dice[j])
                    dice[i] = int(rng.integers(1, 7))
                    rerolled[i] = True
                    rerolls -= 1
                    used += 1
                    continue
                break
            if total >= goal and affordable:
                break
            if len(dice) < pool:
                dice.append(int(rng.integers(1, 7)))
                rerolled.append(False)
                continue
            candidates = [i for i, done in enumerate(rerolled) if not done]
            if rerolls > 0 and candidates:
                i = (max(candidates, key=lambda j: dice[j])
                     if not affordable or total > goal
                     else min(candidates, key=lambda j: dice[j]))
                dice[i] = int(rng.integers(1, 7))
                rerolled[i] = True
                rerolls -= 1
                used += 1
                continue
            break
        total = sum(dice)
        c = cost(total, tn)
        if c > durability:
            energy += ef - 1
            locked += 1
        else:
            energy += output(total, tn)
            durability -= c
            spent += c
            if durability == 0:
                pool = max(1, pool - 1)
                lost += 1
    return energy, spent, lost, used, locked


def run(runs: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    rows = []
    for tn in TNS:
        samples = np.asarray([play(tn, rng) for _ in range(runs)], dtype=float)
        e = samples[:, 0]
        mean, sd = float(e.mean()), float(e.std(ddof=1))
        se = sd / math.sqrt(runs)
        rows.append({
            "tn": tn, "ef": tn - 5, "vma": tn + 3, "runs": runs,
            "mean_energy": mean, "sd_energy": sd, "se_energy": se,
            "ci95_energy": [mean - 1.96 * se, mean + 1.96 * se],
            "mean_sustainability_spent": float(samples[:, 1].mean()),
            "mean_dice_lost": float(samples[:, 2].mean()),
            "mean_rerolls_used": float(samples[:, 3].mean()),
            "mean_ef_locked_turns": float(samples[:, 4].mean()),
        })
    return {
        "model": {
            "initial_pool": "4d6", "tn_range": [9, 14],
            "ef_rule": "TN - 5", "vma_rule": "TN + 3",
            "curve_costs_ef_to_vma": list(COSTS),
            "initial_sustainability": 8, "turns": 8, "reroll_reserve": 8,
            "policy": "Long-term heuristic: highest affordable target under ceil(remaining sustainability / turns remaining); rerolls correct overshoots.",
            "reroll_rule": "shared reserve; each die at most once per turn; reroll replaces result",
        },
        "seed": seed, "results": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    result = run(args.runs, args.seed)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for row in result["results"]:
        print(row)
