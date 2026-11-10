"""Tests for the direct Training B -> Race V2 adapter and cost normalization."""
import json
import unittest

from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.training_race_bridge.training_b_race_harness import (
    run_matrix, run_pool_progression_matrix, run_equal_expectation_variance_matrix, run_second_profile_terrain_matrix, summarize,
)
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
        self.assertEqual(len(result["courses"]), 240)
        for course in result["courses"]:
            self.assertEqual(course["training_turns"], 16)
            self.assertEqual(len(course["training_profile"]), 3)
            self.assertTrue(course["race_pool"])
            self.assertGreaterEqual(course["race_score"], 0)
        summary = summarize(result)
        print("TRAINING_B_RACE_NORMALIZATION_SUMMARY=" + json.dumps(summary, sort_keys=True))
        for focus in ("balanced", "ef", "quality"):
            baseline = summary[focus]["raw_ctl100"]["finish_rate"]
            self.assertEqual(baseline, 0.0)
            for mode in ("pool_expected_ctl100", "pool_expected_ctl150",
                         "pool_expected_ctl200"):
                self.assertGreater(summary[focus][mode]["finish_rate"], baseline)
            zones = summary[focus]["pool_expected_ctl100"]["load_zones"]
            selected = zones["selected"]
            self.assertEqual(
                selected["segments_observed"],
                selected["at_or_below_ef"] + selected["above_ef_through_threshold"]
                + selected["above_threshold"],
            )
            legal = zones["legal_options"]
            self.assertEqual(
                legal["legal_options_observed"],
                legal["at_or_below_ef"] + legal["above_ef_through_threshold"]
                + legal["above_threshold"],
            )

    def test_pool_progression_at_fixed_training_profile(self):
        result = run_pool_progression_matrix()
        self.assertEqual(len(result["courses"]), 80)
        expectations = [result["summary"][name]["expected_total"]
                        for name in ("4d6", "4d8", "4d8+1d6", "2d10+4d6")]
        self.assertEqual(expectations, sorted(expectations))
        self.assertEqual(result["courses"][0]["fixed_training_profile"], result["fixed_training_profile"])
        for course in result["courses"]:
            self.assertEqual(course["fixed_training_profile"], result["fixed_training_profile"])
            self.assertGreater(course["pool_expected_total"], 0)
        print("TRAINING_B_POOL_PROGRESSION_SUMMARY=" +
              json.dumps(result["summary"], sort_keys=True))

    def test_equal_expectation_pool_variance_comparison(self):
        result = run_equal_expectation_variance_matrix()
        self.assertEqual(len(result["courses"]), 120)
        for pair in result["summary"].values():
            entries = list(pair.values())
            expectations = [entry["expected_total"] for entry in entries]
            variances = [entry["variance"] for entry in entries]
            self.assertEqual(expectations[0], expectations[1])
            self.assertNotEqual(variances[0], variances[1])
        for course in result["courses"]:
            self.assertEqual(course["fixed_training_profile"], result["fixed_training_profile"])
        print("TRAINING_B_EQUAL_EXPECTATION_VARIANCE_SUMMARY=" +
              json.dumps(result["summary"], sort_keys=True))

    def test_second_training_profile_and_terrain(self):
        result = run_second_profile_terrain_matrix()
        self.assertEqual(len(result["courses"]), 240)
        for pair in result["summary"].values():
            for terrain in pair.values():
                entries = list(terrain.values())
                self.assertEqual(entries[0]["expected_total"], entries[1]["expected_total"])
                self.assertNotEqual(entries[0]["variance"], entries[1]["variance"])
        for course in result["courses"]:
            self.assertEqual(course["fixed_training_profile"], result["fixed_training_profile"])
        print("TRAINING_B_SECOND_PROFILE_TERRAIN_SUMMARY=" +
              json.dumps(result["summary"], sort_keys=True))

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
