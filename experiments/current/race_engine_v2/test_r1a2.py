import math
import unittest

from experiments.current.race_engine_v2.analysis_r1a2 import (average_ranks,
    pearson, plausible_production_count, spearman)
from experiments.current.race_engine_v2.core import generate_rolls, run_race
from experiments.current.race_engine_v2.fixtures import POOLS
from experiments.current.race_engine_v2.form import (classify_form, classify_form_sum,
    classify_form_structure, form_thresholds, form_value, pattern_features,
    structural_pattern_score)
from experiments.current.race_engine_v2.policies import POLICIES


class FormSumBaselineTests(unittest.TestCase):
    def test_thresholds_and_classes_are_unchanged(self):
        pool = POOLS["6d6"]
        self.assertEqual(form_thresholds(pool.dice), (17, 23, 27))
        self.assertEqual(classify_form_sum((1, 2, 3, 3, 4, 4), pool), "LOW")
        self.assertEqual(classify_form((6, 6, 6, 6, 6, 6), pool, "SUM"), "EXCEPTIONAL")


class FormPatternTests(unittest.TestCase):
    def test_score_uses_structure_not_sum(self):
        pool = POOLS["1d8+3d6"]
        low = (1, 1, 2, 3)
        high = (4, 4, 5, 6)
        self.assertNotEqual(sum(low), sum(high))
        self.assertEqual(pattern_features(low), pattern_features(high))
        self.assertEqual(structural_pattern_score(low, pool), structural_pattern_score(high, pool))

    def test_classification_is_deterministic_and_pool_normalized(self):
        roll = (1, 1, 1, 1, 2, 4)
        six_d6 = POOLS["6d6"]
        mixed = POOLS["2d10+4d6"]
        self.assertEqual(classify_form_structure(roll, six_d6), classify_form_structure(roll, six_d6))
        self.assertEqual(classify_form_structure(roll, six_d6), "GOOD")
        self.assertEqual(classify_form_structure(roll, mixed), "EXCEPTIONAL")

    def test_same_pattern_class_allows_different_sums(self):
        pool = POOLS["1d8+3d6"]
        low, high = (1, 1, 2, 3), (4, 4, 5, 6)
        self.assertEqual(classify_form_structure(low, pool), classify_form_structure(high, pool))

    def test_signal_is_fixed_before_policy_choice(self):
        courses = [run_race(seed=9, pool=POOLS["6d6"], race_length=6, curve="B", policy=policy,
            ctl=100, freshness_bonus=0, long_run_preparation=False, form_mode="PATTERN")
            for policy in POLICIES.values()]
        self.assertEqual(len({course["signals"] for course in courses}), 1)

    def test_sl_changes_low_only(self):
        expected = {"LOW": (0, -1), "NORMAL": (0, 0), "GOOD": (1, 1), "EXCEPTIONAL": (2, 2)}
        for signal, (protected, plain) in expected.items():
            self.assertEqual((form_value(signal, True), form_value(signal, False)), (protected, plain))


class RngAndAnalysisTests(unittest.TestCase):
    def test_mode_and_policy_do_not_change_rolls(self):
        pool = POOLS["6d6"]
        expected = generate_rolls(19, pool, 9)
        for mode in ("SUM", "PATTERN"):
            for policy in POLICIES.values():
                course = run_race(seed=19, pool=pool, race_length=9, curve="B", policy=policy,
                    ctl=100, freshness_bonus=0, long_run_preparation=False, form_mode=mode)
                self.assertEqual(course["rolls"], expected)

    def test_correlations_and_tied_ranks(self):
        self.assertAlmostEqual(pearson([1, 2, 3], [2, 4, 6]), 1)
        self.assertAlmostEqual(spearman([1, 1, 3], [4, 4, 9]), 1)
        self.assertEqual(average_ranks([10, 10, 20]), [1.5, 1.5, 3])
        self.assertTrue(math.isnan(pearson([1, 1], [2, 3])))

    def test_plausible_choice_window(self):
        payable = (10, 14, 15, 16, 18, 22)
        narrow = plausible_production_count(payable, "B", 0.05)
        wide = plausible_production_count(payable, "B", 0.20)
        self.assertLessEqual(narrow, wide)
        self.assertGreater(narrow, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
