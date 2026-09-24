import random
import unittest

from experiments.standard_player_bundle_risk.harness import (
    evaluate_bundle, ordered_outcomes, risk_probability, select_bundle,
    structurally_legal, simulate_policy,
)
from overtraining_capacity_harness import BUST, UNTESTED, resolve, simulate


class TestBundleEngine(unittest.TestCase):
    def test_structural_constraints(self):
        self.assertTrue(structurally_legal(("EF1", "Seuil3"), 4))
        self.assertFalse(structurally_legal(("Seuil3",), 4))
        self.assertFalse(structurally_legal(("EF1", "SL5", "SL5"), 20))

    def test_risk_probability_uses_exceedance_over_best_die(self):
        self.assertEqual(risk_probability("Seuil4", 3, 8), 1/8)
        self.assertEqual(risk_probability("Seuil3", 3, 8), 0)

    def test_expected_value_outcomes_are_exact_and_sum_to_one(self):
        outcomes = ordered_outcomes(("EF1", "Seuil4", "Seuil5"), 3, 6)
        self.assertAlmostEqual(sum(probability for probability, _, _ in outcomes), 1)
        # Bust at first risk, bust at second after first succeeds, all succeed.
        self.assertEqual(len(outcomes), 3)
        self.assertAlmostEqual(outcomes[0][0], 1/6)
        self.assertAlmostEqual(outcomes[1][0], (5/6)*(2/6))
        self.assertAlmostEqual(outcomes[2][0], (5/6)*(4/6))

    def test_moderate_threshold_filters_only_risk_not_structure(self):
        bundle = ("EF1", "Seuil4")
        self.assertIsNone(evaluate_bundle(bundle, "P_STD_MOD15", 8, 3, 14, 6))
        self.assertIsNotNone(evaluate_bundle(bundle, "P_STD_MOD25", 8, 3, 14, 6))

    def test_ordered_real_resolution_stops_after_first_bust(self):
        random.seed(1)  # first d6 is 2
        rows = resolve(("EF1", "Seuil5", "Seuil5"), 3, 6)
        self.assertEqual(rows[1]["status"], BUST)
        self.assertEqual(rows[2]["status"], UNTESTED)


class TestStandardTrajectory(unittest.TestCase):
    def test_p0_matches_existing_baseline(self):
        expected_turns, expected_sessions = simulate(3, "P0_CURRENT", 6)
        actual_turns, actual_sessions, _, _ = simulate_policy(3, "P0_CURRENT", 6)
        self.assertEqual([r["spend_effective"] for r in expected_turns],
                         [r["energy_effective"] for r in actual_turns])
        self.assertEqual([r["q"] for r in expected_turns], [r["q"] for r in actual_turns])
        self.assertEqual([r["status"] for r in expected_sessions],
                         [r["status"] for r in actual_sessions])

    def test_effective_work_and_fatigue_follow_resolved_sessions(self):
        turns, sessions, _, final = simulate_policy(5, "P_STD_MOD40", 5)
        for row in turns:
            realized = [s for s in sessions if s["turn"] == row["turn"] and s["realized"]]
            self.assertEqual(row["energy_effective"], sum(s["rpe"] for s in realized))
        self.assertEqual(final["ctl_final"], sum(r["energy_effective"] for r in turns))


if __name__ == "__main__":
    unittest.main()
