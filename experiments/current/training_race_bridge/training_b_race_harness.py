"""End-to-end experimental trajectories: Training B preparation -> Race V2."""
from __future__ import annotations

import json
from pathlib import Path

from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.training_b_trajectory.harness import run_trajectory
from experiments.current.training_race_bridge.training_b_adapter import run_training_race


SEEDS = (11, 23, 47)
FOCUSES = ("balanced", "ef", "quality")
RACE_LENGTH = 6

# Explicit Race V2 fixtures, not values inferred from Training B.
RACE_INPUTS = {
    "ctl": 100,
    "freshness_bonus": 0,
    "long_run_preparation": False,
}


def run_matrix():
    courses = []
    for focus in FOCUSES:
        for seed in SEEDS:
            training = run_trajectory(seed=seed, focus=focus, turns=16)
            race = run_training_race(
                {
                    "profile": training["final_profile"],
                    "dice_pool": training["dice_pool"],
                },
                seed=seed,
                race_length=RACE_LENGTH,
                policy=POLICIES["ADAPTIVE"],
                **RACE_INPUTS,
            )
            courses.append({
                "seed": seed,
                "training_focus": focus,
                "training_turns": training["turns"],
                "training_profile": training["final_profile"],
                "training_dice_pool": training["dice_pool"],
                "training_fatigue": training["final_fatigue"],
                "race_score": race["score"],
                "race_spent": race["spent"],
                "race_dnf": race["dnf"],
                "race_dnf_turn": race["dnf_turn"],
                "race_pool": race["pool"],
                "race_turns": race["turns"],
            })
    return {
        "status": "EXPERIMENTAL — direct Training B -> Race V2 integration",
        "protocol": {
            "seeds": SEEDS,
            "training_focuses": FOCUSES,
            "training_turns": 16,
            "race_length": RACE_LENGTH,
            "race_policy": "ADAPTIVE",
            **RACE_INPUTS,
            "ctl_freshness_and_long_run_are_external_fixtures": True,
        },
        "courses": courses,
    }


def main():
    output = Path(__file__).with_name("training_b_race_results.json")
    output.write_text(json.dumps(run_matrix(), indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
