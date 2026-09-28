import unittest

from experiments.current.race_engine_v2.core import (PolicyView, available_productions,
    base_reserve_from_ctl, generate_rolls, payable_productions, run_race)
from experiments.current.race_engine_v2.energy import energy_cost
from experiments.current.race_engine_v2.fixtures import ENERGY_TABLES, FORM_VALUES, POOLS
from experiments.current.race_engine_v2.form import classify_form_pattern, form_thresholds, form_value
from experiments.current.race_engine_v2.policies import POLICIES


class ProductionTests(unittest.TestCase):
    def test_exhaustive_nonempty_and_deduplicated(self):
        options = available_productions((1, 1, 2))
        self.assertEqual(options.productions, (1, 2, 3, 4))
        self.assertNotIn(0, options.productions)
        # Equal-valued dice collapse to the same diagnostic face composition,
        # while all four distinct sums remain present.
        self.assertEqual(sum(len(v) for v in options.compositions.values()), 5)

    def test_resolver_does_not_select(self):
        self.assertFalse(hasattr(available_productions((1, 2)), "choice"))


class EnergyTests(unittest.TestCase):
    def test_all_exact_boundaries(self):
        expected = {
            "A": (1, 2, 2, 3, 4, 5, 7, 9, 12),
            "B": (1, 2, 2, 3, 5, 7, 10, 13, 16),
            "C": (1, 2, 3, 5, 8, 12, 16, 20, 25),
        }
        probes = (1, 16, 19, 22, 23, 24, 25, 26, 27)
        for curve in ENERGY_TABLES:
            self.assertEqual(tuple(energy_cost(p, curve) for p in probes), expected[curve])
            self.assertEqual(energy_cost(999, curve), expected[curve][-1])


class FormTests(unittest.TestCase):
    def test_classification_is_reproducible_and_pool_relative(self):
        for pool in POOLS.values():
            self.assertEqual(form_thresholds(pool.dice), form_thresholds(pool.dice))
            low_roll = tuple(1 for _ in pool.dice)
            high_roll = pool.dice
            self.assertEqual(classify_form_pattern(low_roll, pool), "LOW")
            self.assertEqual(classify_form_pattern(high_roll, pool), "EXCEPTIONAL")

    def test_mapping_and_sl_only_protects_low(self):
        self.assertEqual(FORM_VALUES, {"LOW": -1, "NORMAL": 0, "GOOD": 1, "EXCEPTIONAL": 2})
        for signal, value in FORM_VALUES.items():
            self.assertEqual(form_value(signal, False), value)
            self.assertEqual(form_value(signal, True), 0 if signal == "LOW" else value)


class ReserveLegalityTests(unittest.TestCase):
    def test_base_freshness_form_clamp_and_remaining(self):
        self.assertEqual(base_reserve_from_ctl(100, 6), 14)
        course = run_race(seed=4, pool=POOLS["2d10+4d6"], race_length=6, curve="C",
            policy=POLICIES["GREEDY"], ctl=0, freshness_bonus=0, long_run_preparation=False)
        self.assertEqual(len(course["signals"]), 3)
        self.assertGreaterEqual(course["final_reserve"], course["turns"][2]["spent"])
        self.assertEqual(course["reserve_remaining"], course["final_reserve"] - course["spent"])

    def test_payable_and_dnf(self):
        options = available_productions((6, 6, 6, 6))
        self.assertEqual(payable_productions(options, 3, "B"), (6, 12, 18))
        self.assertEqual(payable_productions(options, 0, "B"), ())
        course = run_race(seed=0, pool=POOLS["6d6"], race_length=6, curve="C",
            policy=POLICIES["GREEDY"], ctl=0, freshness_bonus=0, long_run_preparation=False)
        self.assertTrue(course["dnf"])


class RngPolicyTests(unittest.TestCase):
    def test_rolls_same_across_policy_and_repeat(self):
        pool = POOLS["6d6"]
        self.assertEqual(generate_rolls(12, pool, 9), generate_rolls(12, pool, 9))
        courses = [run_race(seed=12, pool=pool, race_length=9, curve="B", policy=p,
            ctl=100, freshness_bonus=0, long_run_preparation=False) for p in POLICIES.values()]
        self.assertEqual(len({c["rolls"] for c in courses}), 1)

    def test_policies_deterministic(self):
        view = PolicyView(1, 6, (1, 2, 3), (1, 2, 3), 0, 14, 0, 0, None, 21, "B")
        for policy in POLICIES.values():
            self.assertEqual(policy(view), policy(view))

    def test_adaptive_cannot_receive_future_form_before_s3(self):
        seen = []
        def spy(view):
            seen.append(view)
            return min(view.payable)
        run_race(seed=1, pool=POOLS["6d6"], race_length=6, curve="B", policy=spy,
            ctl=100, freshness_bonus=0, long_run_preparation=False)
        self.assertIsNone(seen[0].final_reserve)
        self.assertIsNone(seen[1].final_reserve)
        self.assertIsNotNone(seen[2].final_reserve)


if __name__ == "__main__":
    unittest.main(verbosity=2)
