#!/usr/bin/env python3
"""Blackjack sustainability experiment: 33 dice pools x 27 physiological profiles.

Single-file, standard-library-only simulator. TN caps the Blackjack target;
it does not alter the physiological sustainability curve.

Curve interpretation: the first cost in each profile is anchored at --ef-energy.
Subsequent costs apply to consecutive energy values. The final cost is held
constant above the last listed value. Below EF, sustainability cost is zero
and energy output is capped at EF-1.

When sustainability reaches exactly zero, the lowest-sided die is removed
(d6 before d8, d10, d12); subsequent turns are locked to EF-1.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from pathlib import Path

TN_VALUES = tuple(range(9, 15))
DEFAULT_RESERVES = (8, 16, 24)
DEFAULT_TURNS = 8
DEFAULT_REROLLS = 8
DEFAULT_EF_ENERGY = 9

# The 27 cost sequences are transcribed from FEEDBACK.md.
# Each sequence starts at EF and is intentionally kept at its own length.
PROFILE_COSTS = {
    "conf 3-2": (1, 2, 3, 5, 9, 13),
    "conf 3-3": (1, 2, 3, 5, 7, 10, 13),
    "conf 4-2": (1, 2, 3, 4, 5, 9, 13),
    "conf 4-3": (1, 2, 3, 4, 5, 7, 10, 13),
    "conf 4-4": (1, 2, 3, 4, 5, 7, 9, 11, 13),
    "conf 5-2": (1, 1, 2, 3, 4, 5, 9, 13),
    "conf 5-3": (1, 1, 2, 3, 4, 5, 7, 10, 13),
    "conf 5-4": (1, 1, 2, 3, 4, 5, 7, 9, 11, 13),
    "conf 5-5": (1, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13),
    "conf 6-2": (1, 1, 1, 2, 3, 4, 5, 9, 13),
    "conf 6-3": (1, 1, 1, 2, 3, 4, 5, 7, 10, 13),
    "conf 6-4": (1, 1, 1, 2, 3, 4, 5, 7, 9, 11, 13),
    "conf 6-5": (1, 1, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13),
    "conf 6-6": (1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13),
    "conf 7-2": (1, 1, 1, 1, 2, 3, 4, 5, 9, 13),
    "conf 7-3": (1, 1, 1, 1, 2, 3, 4, 5, 7, 10, 13),
    "conf 7-4": (1, 1, 1, 1, 2, 3, 4, 5, 7, 9, 11, 13),
    "conf 7-5": (1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13),
    "conf 7-6": (1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13),
    "conf 7-7": (1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13),
    "conf 8-2": (1, 1, 1, 1, 1, 2, 3, 4, 5, 9, 13),
    "conf 8-3": (1, 1, 1, 1, 1, 2, 3, 4, 5, 7, 10, 13),
    "conf 8-4": (1, 1, 1, 1, 1, 2, 3, 4, 5, 7, 9, 11, 13),
    "conf 8-5": (1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13),
    "conf 8-6": (1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13),
    "conf 8-7": (1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13),
    "conf 8-8": (1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13),
}

# The 33 pools, in the order of tables_completes.csv.xlsx.
# A die is represented by its number of faces.
POOL_DICE = {
    1: (6, 6, 6, 6),
    2: (6, 6, 6, 8),
    3: (6, 6, 6, 10),
    4: (6, 6, 8, 8),
    5: (6, 6, 6, 12),
    6: (6, 6, 8, 10),
    7: (6, 8, 8, 8),
    8: (6, 6, 6, 6, 6),
    9: (6, 6, 8, 12),
    10: (6, 6, 10, 10),
    11: (6, 8, 8, 10),
    12: (8, 8, 8, 8),
    13: (6, 6, 6, 6, 8),
    14: (6, 6, 6, 6, 10),
    15: (6, 6, 6, 8, 8),
    16: (6, 6, 6, 6, 12),
    17: (6, 6, 6, 8, 10),
    18: (6, 6, 8, 8, 8),
    19: (6, 6, 6, 6, 6, 6),
    20: (6, 6, 6, 8, 12),
    21: (6, 6, 6, 10, 10),
    22: (6, 6, 8, 8, 10),
    23: (6, 8, 8, 8, 8),
    24: (6, 6, 6, 6, 6, 8),
    25: (6, 6, 6, 6, 6, 10),
    26: (6, 6, 6, 6, 8, 8),
    27: (6, 6, 6, 6, 6, 12),
    28: (6, 6, 6, 6, 8, 10),
    29: (6, 6, 6, 8, 8, 8),
    30: (6, 6, 6, 6, 8, 12),
    31: (6, 6, 6, 6, 10, 10),
    32: (6, 6, 6, 8, 8, 10),
    33: (6, 6, 8, 8, 8, 8),
}

POOL_NAMES = {
    1:"4d6", 2:"3d6+1d8", 3:"3d6+1d10", 4:"2d6+2d8",
    5:"3d6+1d12", 6:"2d6+1d8+1d10", 7:"1d6+3d8", 8:"5d6",
    9:"2d6+1d8+1d12", 10:"2d6+2d10", 11:"1d6+2d8+1d10",
    12:"4d8", 13:"4d6+1d8", 14:"4d6+1d10", 15:"3d6+2d8",
    16:"4d6+1d12", 17:"3d6+1d8+1d10", 18:"2d6+3d8", 19:"6d6",
    20:"3d6+1d8+1d12", 21:"3d6+2d10", 22:"2d6+2d8+1d10",
    23:"1d6+4d8", 24:"5d6+1d8", 25:"5d6+1d10", 26:"4d6+2d8",
    27:"5d6+1d12", 28:"4d6+1d8+1d10", 29:"3d6+3d8",
    30:"4d6+1d8+1d12", 31:"4d6+2d10", 32:"3d6+2d8+1d10",
    33:"2d6+4d8",
}


def curve_cost(energy: int, costs: tuple[int, ...], ef: int) -> int:
    if energy < ef:
        return 0
    offset = min(energy - ef, len(costs) - 1)
    return costs[offset]


def energy_output(raw_total: int, costs: tuple[int, ...], ef: int) -> int:
    if raw_total < ef:
        return min(raw_total, ef - 1)
    return min(raw_total, ef + len(costs) - 1)


def long_term_target(sustainability: int, turns_left: int,
                     costs: tuple[int, ...], ef: int) -> int:
    if sustainability <= 0:
        return ef - 1
    budget = math.ceil(sustainability / turns_left)
    affordable = [ef + i for i in range(len(costs))
                  if costs[i] <= budget]
    return max(affordable) if affordable else ef - 1


def play_course(tn: int, reserve: int, turns: int, rerolls: int,
                pool_definition: tuple[int, ...], costs: tuple[int, ...],
                ef: int, rng: random.Random) -> tuple[int, int, int, int, int]:
    pool = list(pool_definition)
    sustainability = reserve
    rerolls_left = rerolls
    energy_total = spent = dice_lost = rerolls_used = ef_locked = 0

    for turn_index in range(turns):
        if sustainability <= 0:
            energy_total += ef - 1
            ef_locked += 1
            continue

        target = min(tn, long_term_target(
            sustainability, turns - turn_index, costs, ef
        ))
        # Start with N-2 dice, then add remaining dice one at a time.
        dice = [rng.randint(1, sides) for sides in pool[:max(1, len(pool)-2)]]
        rerolled = [False] * len(dice)

        while True:
            total = sum(dice)
            affordable = curve_cost(total, costs, ef) <= sustainability

            if total > target and rerolls_left:
                candidates = [i for i, used in enumerate(rerolled) if not used]
                if candidates:
                    idx = max(candidates, key=lambda i: dice[i])
                    dice[idx] = rng.randint(1, pool[idx])
                    rerolled[idx] = True
                    rerolls_left -= 1
                    rerolls_used += 1
                    continue

            if total > target and not affordable:
                break
            if total >= target and affordable:
                break

            if len(dice) < len(pool):
                idx = len(dice)
                dice.append(rng.randint(1, pool[idx]))
                rerolled.append(False)
                continue

            candidates = [i for i, used in enumerate(rerolled) if not used]
            if rerolls_left and candidates:
                idx = min(candidates, key=lambda i: dice[i])
                dice[idx] = rng.randint(1, pool[idx])
                rerolled[idx] = True
                rerolls_left -= 1
                rerolls_used += 1
                continue
            break

        total = sum(dice)
        cost = curve_cost(total, costs, ef)
        if cost > sustainability:
            energy_total += ef - 1
            ef_locked += 1
        else:
            energy_total += energy_output(total, costs, ef)
            sustainability -= cost
            spent += cost
            if sustainability == 0 and pool:
                # Agreed hypothesis: permanently remove the lowest-sided die.
                pool.remove(min(pool))
                dice_lost += 1

    return energy_total, spent, dice_lost, rerolls_used, ef_locked


def stable_seed(seed: int, pool_id: int, profile_index: int,
                reserve: int, tn: int) -> int:
    return seed + pool_id * 1_000_003 + profile_index * 100_003 + reserve * 1_009 + tn * 97


def simulate_cell(pool_id: int, profile_id: str, tn: int, reserve: int,
                  runs: int, turns: int, rerolls: int, seed: int,
                  ef: int) -> dict:
    dice = POOL_DICE[pool_id]
    costs = PROFILE_COSTS[profile_id]
    rng = random.Random(seed)
    samples = [play_course(tn, reserve, turns, rerolls, dice, costs, ef, rng)
               for _ in range(runs)]
    energies = [s[0] for s in samples]
    avg = statistics.mean(energies)
    sd = statistics.stdev(energies) if runs > 1 else 0.0
    se = sd / math.sqrt(runs)
    return {
        "pool_id": pool_id, "pool": POOL_NAMES[pool_id],
        "pool_dice": list(dice), "profile_id": profile_id,
        "profile_costs": list(costs), "ef_energy": ef,
        "profile_last_energy": ef + len(costs) - 1,
        "tn": tn, "initial_sustainability": reserve,
        "runs": runs, "seed": seed,
        "mean_energy": avg, "sd_energy": sd, "se_energy": se,
        "ci95_low": avg - 1.96 * se, "ci95_high": avg + 1.96 * se,
        "mean_sustainability_spent": statistics.mean(s[1] for s in samples),
        "mean_dice_lost": statistics.mean(s[2] for s in samples),
        "mean_rerolls_used": statistics.mean(s[3] for s in samples),
        "mean_ef_locked_turns": statistics.mean(s[4] for s in samples),
    }


def parse_ids(values: list[str] | None, available: list, label: str) -> list:
    if not values:
        return available
    selected = []
    for value in values:
        try:
            item = int(value) if label == "pool" else value
        except ValueError:
            raise argparse.ArgumentTypeError(f"Identifiant de pool invalide: {value}")
        if item not in available:
            raise argparse.ArgumentTypeError(f"{label} inconnu: {value}")
        if item not in selected:
            selected.append(item)
    return selected


def run_experiment(args) -> dict:
    pool_ids = parse_ids(args.pool_ids, list(POOL_DICE), "pool")
    profile_ids = parse_ids(args.profile_ids, list(PROFILE_COSTS), "profile")
    results = []
    for pool_id in pool_ids:
        for profile_index, profile_id in enumerate(profile_ids):
            for reserve in args.reserves:
                for tn in args.tns:
                    seed = stable_seed(args.seed, pool_id, profile_index, reserve, tn)
                    results.append(simulate_cell(
                        pool_id, profile_id, tn, reserve, args.runs, args.turns,
                        args.rerolls, seed, args.ef_energy
                    ))
    return {
        "experiment": "Blackjack — pools de dés x profils de soutenabilité",
        "seed": args.seed,
        "parameters": {
            "runs_per_cell": args.runs, "tn_values": args.tns,
            "initial_sustainability_values": args.reserves,
            "turns": args.turns, "reroll_reserve": args.rerolls,
            "ef_energy": args.ef_energy,
            "selected_pool_ids": pool_ids, "selected_profile_ids": profile_ids,
            "pool_catalogue_count": len(POOL_DICE),
            "profile_catalogue_count": len(PROFILE_COSTS),
        },
        "rules": {
            "tn": "TN caps the Blackjack target only; it does not modify curve costs.",
            "curve": "First profile cost is anchored at EF; subsequent costs map to consecutive energies; final cost is held above profile end.",
            "below_ef": "Zero sustainability cost; energy output capped at EF-1.",
            "blackjack": "Roll N-2 dice, then add dice one by one; each die may be rerolled at most once per turn.",
            "rerolls": "Shared reserve over the full course; reroll replaces the die result.",
            "depletion": "At exact zero sustainability, remove one lowest-sided die permanently; subsequent turns are locked to EF-1.",
            "unaffordable": "If the result cost exceeds remaining sustainability, output is EF-1 and no sustainability is spent.",
            "heuristic": "Target is min(TN, highest energy affordable under ceil(remaining sustainability / turns remaining)).",
            "dice_loss_hypothesis": "Remove d6 first, then d8, d10, d12.",
        },
        "results": results,
        "caveat": "Explicit heuristic, not an optimal-play solver. Results depend on the declared dice-loss and curve-anchor assumptions.",
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("Aucun résultat à exporter.")
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def self_test() -> None:
    assert len(PROFILE_COSTS) == 27
    assert len(POOL_DICE) == 33
    assert curve_cost(8, PROFILE_COSTS["conf 3-2"], 9) == 0
    assert curve_cost(9, PROFILE_COSTS["conf 3-2"], 9) == 1
    assert curve_cost(14, PROFILE_COSTS["conf 3-2"], 9) == 13
    assert curve_cost(100, PROFILE_COSTS["conf 3-2"], 9) == 13
    assert energy_output(100, PROFILE_COSTS["conf 3-2"], 9) == 14
    assert len(POOL_DICE[1]) == 4 and POOL_DICE[1] == (6, 6, 6, 6)
    assert POOL_DICE[33] == (6, 6, 8, 8, 8, 8)
    print("SELF-TEST OK: 27 profils, 33 pools, ancrage EF et écrêtage.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--tns", type=int, nargs="+", default=list(TN_VALUES))
    parser.add_argument("--reserves", type=int, nargs="+", default=list(DEFAULT_RESERVES))
    parser.add_argument("--turns", type=int, default=DEFAULT_TURNS)
    parser.add_argument("--rerolls", type=int, default=DEFAULT_REROLLS)
    parser.add_argument("--ef-energy", type=int, default=DEFAULT_EF_ENERGY,
                        help="Energy position of the first cost in every profile (default: 9).")
    parser.add_argument("--pool-ids", nargs="+",
                        help="Pool IDs 1–33. Default: pool 1 only.")
    parser.add_argument("--profile-ids", nargs="+",
                        help='Profile IDs, e.g. "conf 3-2". Default: first profile only.')
    parser.add_argument("--output", type=Path,
                        default=Path("tn_sustainability_sensitivity_results.json"))
    parser.add_argument("--csv-output", type=Path,
                        help="CSV destination (default: same basename as --output).")
    parser.add_argument("--self-test", action="store_true",
                        help="Run built-in data and curve checks, then exit.")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return
    if args.runs < 1 or args.turns < 1:
        parser.error("--runs and --turns must be at least 1")
    if args.rerolls < 0 or args.ef_energy < 1:
        parser.error("--rerolls must be non-negative and --ef-energy positive")
    if any(v < 0 for v in args.reserves):
        parser.error("--reserves must be non-negative")
    if any(v < 1 for v in args.tns):
        parser.error("--tns must be positive")
    # Conservative defaults avoid silently launching 33 x 27 x 18 x 50k courses.
    if args.pool_ids is None:
        args.pool_ids = ["1"]
    if args.profile_ids is None:
        args.profile_ids = ["conf 3-2"]

    try:
        data = run_experiment(args)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    csv_path = args.csv_output or args.output.with_suffix(".csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(csv_path, data["results"])

    print(f'{len(data["results"])} configurations simulées.')
    print(f"JSON : {args.output}")
    print(f"CSV  : {csv_path}")
    print("Pool | Profil | TN | Réserve | Énergie moyenne | Soutenabilité | Dés perdus | Relances | Tours EF")
    for row in data["results"]:
        print(f'{row["pool"]} | {row["profile_id"]} | {row["tn"]} | '
              f'{row["initial_sustainability"]} | {row["mean_energy"]:.4f} | '
              f'{row["mean_sustainability_spent"]:.4f} | {row["mean_dice_lost"]:.4f} | '
              f'{row["mean_rerolls_used"]:.4f} | {row["mean_ef_locked_turns"]:.4f}')


if __name__ == "__main__":
    main()
