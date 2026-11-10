"""Paired raw-cost and pool-normalized Training B -> Race V2 experiment."""
from __future__ import annotations

import json
from pathlib import Path

from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.training_b_trajectory.harness import run_trajectory
from experiments.current.training_race_bridge.training_b_adapter import (
    race_inputs_from_training, run_training_race,
)


SEEDS = (11, 23, 47)
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
            for mode, cost_divisor in (("raw", 1.0), ("pool_expected", divisor)):
                race = run_training_race(
                    snapshot, seed=seed, race_length=RACE_LENGTH,
                    policy=POLICIES["ADAPTIVE"], physiology_cost_divisor=cost_divisor,
                    **RACE_INPUTS,
                )
                courses.append({
                    "seed": seed, "training_focus": focus, "cost_mode": mode,
                    "training_turns": training["turns"],
                    "training_profile": training["final_profile"],
                    "training_dice_pool": training["dice_pool"],
                    "pool_expected_total": divisor,
                    "training_fatigue": training["final_fatigue"],
                    "race_score": race["score"], "race_spent": race["spent"],
                    "race_dnf": race["dnf"], "race_dnf_turn": race["dnf_turn"],
                    "race_pool": race["pool"], "race_turns": race["turns"],
                    "race_base_reserve": race["base_reserve"],
                    "race_final_reserve": race["final_reserve"],
                })
    return {
        "status": "EXPERIMENTAL — raw vs pool-expectation-normalized physiological cost",
        "protocol": {
            "seeds": SEEDS, "training_focuses": FOCUSES, "training_turns": 16,
            "race_length": RACE_LENGTH, "race_policy": "ADAPTIVE",
            **RACE_INPUTS,
            "normalization": "physiological_cost / sum((die_size + 1) / 2)",
            "reserve": "unchanged Race V2 base reserve; same units as normalized cost",
            "paired_rolls": "same seed and pool in raw and normalized modes",
        },
        "courses": courses,
    }


def summarize(result):
    summary = {}
    for focus in FOCUSES:
        summary[focus] = {}
        for mode in ("raw", "pool_expected"):
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


def main():
    result = run_matrix()
    result["summary"] = summarize(result)
    output = Path(__file__).with_name("training_b_race_results.json")
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
