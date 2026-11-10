"""Tests for the direct Training B -> Race V2 adapter and cost normalization."""
import json
import unittest

from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.training_race_bridge.training_b_race_harness import run_matrix, summarize
from experiments.current.training_race_bridge.training_b_adapter import (
    race_inputs_from_training, race_pool_from_training, race_profile_from_training,
    run_training_race,
)
from training_v2.state import PlayerState, PhysiologyProfile


class TrainingBAdapterTests(unittest.TestCase):
    def test_profile_is_copied_without_hidden_rescaling(self):
        source = PhysiologyProfile(ef=7, threshold=10, vma=13)
        converted = race_profile_from_training(source)
        self.assertEqual((converted.ef, converted.threshold, converted.vma), (7, 10, 13))

    def test_pool_preserves_every_die_and_supported_size(self):
        pool = race_pool_from_training((6, 8, 6, 10, 12))
        self.assertEqual(pool.dice, (6, 8, 6, 10, 12))
        self.assertEqual(pool.name, "1d12+1d10+1d8+2d6")

    def test_invalid_pool_rejected(self):
        with self.assertRaises(ValueError):
            race_pool_from_training((6, 6, 6))
        with self.assertRaises(ValueError):
            race_pool_from_training((6, 6, 6, 6, 20))

    def test_player_state_conversion(self):
        state = PlayerState(profile=PhysiologyProfile(ef=8, threshold=11, vma=14),
                            dice_pool=[6, 8, 6, 10])
        converted = race_inputs_from_training(state)
        self.assertEqual((converted["physiology_profile"].ef,
                          converted["physiology_profile"].threshold,
                          converted["physiology_profile"].vma), (8, 11, 14))
        self.assertEqual(converted["pool"].dice, (6, 8, 6, 10))

    def test_sixteen_turn_training_matrix_compares_paired_cost_modes(self):
        result = run_matrix()
        self.assertEqual(len(result["courses"]), 120)
        for course in result["courses"]:
            self.assertEqual(course["training_turns"], 16)
            self.assertEqual(len(course["training_profile"]), 3)
            self.assertTrue(course["race_pool"])
            self.assertGreaterEqual(course["race_score"], 0)
        summary = summarize(result)
        print("TRAINING_B_RACE_NORMALIZATION_SUMMARY=" + json.dumps(summary, sort_keys=True))
        for focus in ("balanced", "ef", "quality"):
            self.assertEqual(summary[focus]["raw"]["finish_rate"], 0.0)
            self.assertGreater(summary[focus]["pool_expected"]["finish_rate"],
                               summary[focus]["raw"]["finish_rate"])

    def test_race_v2_runs_from_completed_training_snapshot(self):
        snapshot = {"profile": {"ef": 15, "threshold": 21, "vma": 27},
                    "dice_pool": [6, 6, 6, 6, 6, 6]}
        result = run_training_race(
            snapshot, seed=17, race_length=6, policy=POLICIES["ADAPTIVE"],
            ctl=100, freshness_bonus=0, long_run_preparation=False,
        )
        self.assertEqual(result["pool"], "6d6")
        self.assertEqual(result["physiology_profile"].ef, 15)
        self.assertEqual(len(result["rolls"]), 6)
        self.assertEqual(result["score"], sum(t["choice"] for t in result["turns"]))

    def test_normalized_cost_divisor_is_validated(self):
        snapshot = {"profile": {"ef": 15, "threshold": 21, "vma": 27},
                    "dice_pool": [6, 6, 6, 6, 6, 6]}
        args = dict(seed=1, race_length=6, policy=POLICIES["ADAPTIVE"], ctl=100,
                    freshness_bonus=0, long_run_preparation=False)
        with self.assertRaises(ValueError):
            run_training_race(snapshot, physiology_cost_divisor=0, **args)


if __name__ == "__main__":
    unittest.main()
