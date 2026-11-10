"""Experimental pool-expectation normalization probe.

Candidate rule: express each physiological cost as a count of expected full
pool rolls. The existing reserve value is interpreted in those same units.
This is a calibration hypothesis, not a CURRENT Race V2 rule.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

from experiments.current.race_engine_v2 import core
from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.training_b_trajectory.harness import run_trajectory
from experiments.current.training_race_bridge.training_b_adapter import run_training_race


SEEDS = (11, 23, 47)
FOCUSES = ("balanced", "ef", "quality")
RACE_LENGTH = 6
RACE_INPUTS = {
    "ctl": 100,
    "freshness_bonus": 0,
    "long_run_preparation": False,
}


def normalized_cost(profile, load, pool_expected_total):
    """Cost in expected-pool-roll units, rounded up to preserve payment."""
    raw = core.physiological_cost(profile, load)
    return max(1, math.ceil(raw / pool_expected_total))


def run_matrix():
    courses = []
    for focus in FOCUSES:
        for seed in SEEDS:
            training = run_trajectory(seed=seed, focus=focus, turns=16)
            snapshot = {
                "profile": training["final_profile"],
                "dice_pool": training["dice_pool"],
            }
            # Convert each profile cost using the actual persistent pool's
            # expectation. Reserve remains the explicit Race V2 fixture.
            from experiments.current.training_race_bridge.training_b_adapter import (
                race_pool_from_training,
            )
            pool = race_pool_from_training(training["dice_pool"])
            expected = pool.expected_total
            original = core.physiological_cost
            with patch(
                "experiments.current.race_engine_v2.core.physiological_cost",
                side_effect=lambda profile, load: normalized_cost(
                    profile, load, expected
                ),
            ):
                race = run_training_race(
                    snapshot,
                    seed=seed,
                    race_length=RACE_LENGTH,
                    policy=POLICIES["ADAPTIVE"],
                    **RACE_INPUTS,
                )
            courses.append({
                "seed": seed,
                "training_focus": focus,
                "training_profile": training["final_profile"],
                "race_pool": pool.name,
                "pool_expected_total": expected,
                "race_base_reserve": race["base_reserve"],
                "race_score": race["score"],
                "race_spent": race["spent"],
                "race_dnf": race["dnf"],
                "race_dnf_turn": race["dnf_turn"],
                "race_turns": race["turns"],
            })

    summary = {}
    for focus in FOCUSES:
        rows = [c for c in courses if c["training_focus"] == focus]
        summary[focus] = {
            "finish_rate": sum(not c["race_dnf"] for c in rows) / len(rows),
            "mean_score": round(sum(c["race_score"] for c in rows) / len(rows), 2),
            "mean_spent": round(sum(c["race_spent"] for c in rows) / len(rows), 2),
            "mean_pool_expectation": round(
                sum(c["pool_expected_total"] for c in rows) / len(rows), 2
            ),
            "profiles": [c["training_profile"] for c in rows],
            "pools": sorted({c["race_pool"] for c in rows}),
        }
    return {
        "status": "EXPERIMENTAL — pool-expectation normalized physiological cost",
        "protocol": {
            "seeds": SEEDS,
            "training_focuses": FOCUSES,
            "training_turns": 16,
            "race_length": RACE_LENGTH,
            "race_policy": "ADAPTIVE",
            **RACE_INPUTS,
            "cost_rule": "max(1, ceil(physiological_cost / E(pool)))",
            "reserve_rule": "unchanged Race V2 fixture; interpreted in expected-pool-roll units",
            "reserve_interpretation_is_hypothesis": True,
        },
        "summary": summary,
        "courses": courses,
    }


def main():
    output = Path(__file__).with_name("pool_normalized_cost_results.json")
    output.write_text(json.dumps(run_matrix(), indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
