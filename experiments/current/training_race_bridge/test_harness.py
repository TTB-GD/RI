"""Targeted tests for the isolated bridge, not CURRENT prototype tests."""

import unittest

from experiments.current.race_engine_v2.core import generate_rolls
from experiments.current.training_race_bridge.harness import (
    BUILDS, CONTEXTS, CURVE, EF, POOL, RACE_LENGTH, SEEDS, curve_cost,
    eco_max, effective_cost, make_athlete, run_course,
)


class BridgeTests(unittest.TestCase):
    def test_same_physiology_pool_and_spec_budget(self):
        for context in CONTEXTS:
            athletes = [make_athlete(context, build) for build in BUILDS]
            self.assertEqual({(a.ef, a.seuil, a.vma, a.initial_as) for a in athletes},
                             {(athletes[0].ef, athletes[0].seuil,
                               athletes[0].vma, athletes[0].initial_as)})
            self.assertEqual({sum(BUILDS[b]) for b in BUILDS}, {4})
            self.assertEqual(POOL.name, "6d6")

    def test_position_only_changes_active_as(self):
        economy = make_athlete("AS42", "ECONOMY")
        speed = make_athlete("AS42", "SPEED")
        self.assertEqual((economy.ef, economy.seuil, economy.vma),
                         (speed.ef, speed.seuil, speed.vma))
        self.assertNotEqual(economy.active_as, speed.active_as)
        self.assertEqual(generate_rolls(7, POOL, RACE_LENGTH),
                         run_course("AS42", "SPEED", 7)["rolls"])

    def test_efficiency_only_changes_exact_as_cost_and_obeys_bounds(self):
        athlete = make_athlete("AS10", "ECONOMY")
        adjusted, triggered = effective_cost(athlete.active_as, athlete)
        self.assertTrue(triggered)
        self.assertLess(adjusted, curve_cost(athlete.active_as))
        self.assertEqual(effective_cost(athlete.active_as - 1, athlete),
                         (curve_cost(athlete.active_as - 1), False))
        self.assertGreaterEqual(adjusted, curve_cost(EF))
        self.assertLessEqual(athlete.effective_eco, eco_max(athlete.active_as))

    def test_fixed_seed_is_reproducible(self):
        self.assertEqual(run_course("AS10", "BALANCED", SEEDS[3]),
                         run_course("AS10", "BALANCED", SEEDS[3]))


if __name__ == "__main__":
    unittest.main()
