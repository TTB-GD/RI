"""Paired raw-cost and pool-normalized Training B -> Race V2 experiment."""
from __future__ import annotations

import json
from pathlib import Path

from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.training_b_trajectory.harness import run_trajectory
from experiments.current.training_race_bridge.training_b_adapter import (
    race_inputs_from_training, run_training_race,
)


SEEDS = tuple(range(20))
FOCUSES = ("balanced", "ef", "quality")
RACE_LENGTH = 6
RACE_INPUTS = {"ctl": 100, "freshness_bonus": 0, "long_run_preparation": False}


def run_matrix():
    courses = []
    for focus in FOCUSES:
        for seed in SEEDS:
            training = run_trajectory(seed=seed, focus=focus, turns=16)
            snapshot = {
                "profile": training["final_profile"],
                "dice_pool": training["dice_pool"],
            }
            converted = race_inputs_from_training(snapshot)
            divisor = converted["pool"].expected_total
            variants = [("raw_ctl100", 1.0, 100)] + [
                (f"pool_expected_ctl{ctl}", divisor, ctl) for ctl in (100, 150, 200)
            ]
            for mode, cost_divisor, ctl in variants:
                race = run_training_race(
                    snapshot, seed=seed, race_length=RACE_LENGTH,
                    policy=POLICIES["ADAPTIVE"], physiology_cost_divisor=cost_divisor,
                    ctl=ctl, freshness_bonus=0, long_run_preparation=False,
                )
                courses.append({
                    "seed": seed, "training_focus": focus, "cost_mode": mode,
                    "ctl": ctl, "training_turns": training["turns"],
                    "training_profile": training["final_profile"],
                    "training_dice_pool": training["dice_pool"],
                    "pool_expected_total": divisor,
                    "training_fatigue": training["final_fatigue"],
                    "race_score": race["score"], "race_spent": race["spent"],
                    "race_dnf": race["dnf"], "race_dnf_turn": race["dnf_turn"],
                    "race_pool": race["pool"], "race_turns": race["turns"],
                    "race_base_reserve": race["base_reserve"],
                    "race_final_reserve": race["final_reserve"],
                    "race_reserve_remaining": race["reserve_remaining"],
                })
    return {
        "status": "EXPERIMENTAL — raw vs pool-expectation-normalized physiological cost",
        "protocol": {
            "seeds": SEEDS, "training_focuses": FOCUSES, "training_turns": 16,
            "race_length": RACE_LENGTH, "race_policy": "ADAPTIVE",
            **RACE_INPUTS,
            "normalization": "physiological_cost / sum((die_size + 1) / 2)",
            "reserve_sensitivity": "CTL 100 / 150 / 200; existing reserve formula only",
            "raw_baseline": "CTL 100",
            "paired_rolls": "same seed and pool across cost and reserve variants",
        },
        "courses": courses,
    }


def summarize(result):
    summary = {}
    modes = ("raw_ctl100", "pool_expected_ctl100",
             "pool_expected_ctl150", "pool_expected_ctl200")
    for focus in FOCUSES:
        summary[focus] = {}
        for mode in modes:
            rows = [c for c in result["courses"]
                    if c["training_focus"] == focus and c["cost_mode"] == mode]
            summary[focus][mode] = {
                "finish_rate": round(sum(not c["race_dnf"] for c in rows) / len(rows), 3),
                "mean_score": round(sum(c["race_score"] for c in rows) / len(rows), 2),
                "mean_spent": round(sum(c["race_spent"] for c in rows) / len(rows), 3),
                "mean_pool_expectation": round(sum(c["pool_expected_total"] for c in rows) / len(rows), 2),
                "dnf_turns": [c["race_dnf_turn"] for c in rows],
            }

    return summary


def run_pool_progression_matrix():
    """Hold Training B physiology fixed and vary only the persistent race pool."""
    from experiments.current.training_race_bridge.training_b_adapter import race_pool_from_training

    prepared = run_trajectory(seed=11, focus="balanced", turns=16)
    profile = prepared["final_profile"]
    pool_fixtures = {
        "4d6": (6, 6, 6, 6),
        "4d8": (8, 8, 8, 8),
        "4d8+1d6": (8, 8, 8, 8, 6),
        "2d10+4d6": (10, 10, 6, 6, 6, 6),
    }
    courses = []
    for pool_name, dice in pool_fixtures.items():
        pool = race_pool_from_training(dice)
        snapshot = {"profile": profile, "dice_pool": dice}
        for seed in SEEDS:
            race = run_training_race(
                snapshot, seed=seed, race_length=RACE_LENGTH,
                policy=POLICIES["ADAPTIVE"], ctl=100,
                freshness_bonus=0, long_run_preparation=False,
                physiology_cost_divisor=pool.expected_total,
            )
            courses.append({
                "seed": seed, "pool_fixture": pool_name,
                "pool_expected_total": pool.expected_total,
                "pool_variance": pool.variance,
                "fixed_training_profile": profile,
                "race_score": race["score"], "race_spent": race["spent"],
                "race_dnf": race["dnf"], "race_dnf_turn": race["dnf_turn"],
                "race_pool": race["pool"],
            })
    summary = {}
    for pool_name in pool_fixtures:
        rows = [c for c in courses if c["pool_fixture"] == pool_name]
        summary[pool_name] = {
            "finish_rate": round(sum(not c["race_dnf"] for c in rows) / len(rows), 3),
            "mean_score": round(sum(c["race_score"] for c in rows) / len(rows), 2),
            "mean_spent": round(sum(c["race_spent"] for c in rows) / len(rows), 3),
            "expected_total": rows[0]["pool_expected_total"],
            "variance": rows[0]["pool_variance"],
        }
    return {"fixed_training_profile": profile, "summary": summary, "courses": courses}



def run_equal_expectation_variance_matrix():
    """Compare same-expectation pools with different face composition/variance."""
    from experiments.current.training_race_bridge.training_b_adapter import race_pool_from_training

    prepared = run_trajectory(seed=11, focus="balanced", turns=16)
    profile = prepared["final_profile"]
    pairs = {
        "E18": {
            "4d8": (8, 8, 8, 8),
            "2d6+2d10": (6, 6, 10, 10),
        },
        "E22_5": {
            "5d8": (8, 8, 8, 8, 8),
            "3d6+1d10+1d12": (6, 6, 6, 10, 12),
        },
        "E27": {
            "6d8": (8, 8, 8, 8, 8, 8),
            "3d6+3d10": (6, 6, 6, 10, 10, 10),
        },
    }
    courses = []
    for pair_name, pool_pair in pairs.items():
        for pool_name, dice in pool_pair.items():
            pool = race_pool_from_training(dice)
            snapshot = {"profile": profile, "dice_pool": dice}
            for seed in SEEDS:
                race = run_training_race(
                    snapshot, seed=seed, race_length=RACE_LENGTH,
                    policy=POLICIES["ADAPTIVE"], ctl=100,
                    freshness_bonus=0, long_run_preparation=False,
                    physiology_cost_divisor=pool.expected_total,
                )
                courses.append({
                    "seed": seed, "pair": pair_name, "pool_fixture": pool_name,
                    "pool_expected_total": pool.expected_total,
                    "pool_variance": pool.variance,
                    "fixed_training_profile": profile,
                    "race_score": race["score"], "race_spent": race["spent"],
                    "race_dnf": race["dnf"], "race_dnf_turn": race["dnf_turn"],
                })
    summary = {}
    for pair_name, pool_pair in pairs.items():
        summary[pair_name] = {}
        for pool_name in pool_pair:
            rows = [c for c in courses if c["pool_fixture"] == pool_name]
            summary[pair_name][pool_name] = {
                "finish_rate": round(sum(not c["race_dnf"] for c in rows) / len(rows), 3),
                "mean_score": round(sum(c["race_score"] for c in rows) / len(rows), 2),
                "mean_spent": round(sum(c["race_spent"] for c in rows) / len(rows), 3),
                "expected_total": rows[0]["pool_expected_total"],
                "variance": rows[0]["pool_variance"],
            }
    return {"fixed_training_profile": profile, "summary": summary, "courses": courses}


def main():
    result = run_matrix()
    result["summary"] = summarize(result)
    output = Path(__file__).with_name("training_b_race_results.json")
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
