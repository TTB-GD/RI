"""Regression checks for the experimental Training B trajectory probe."""
import unittest

from experiments.current.training_b_trajectory.harness import run_trajectory


class TrainingBTrajectoryTests(unittest.TestCase):
    def test_sixteen_turn_trajectory_is_reproducible(self):
        first = run_trajectory(seed=11, focus="balanced", turns=16)
        second = run_trajectory(seed=11, focus="balanced", turns=16)
        self.assertEqual(first, second)
        self.assertEqual(len(first["history"]), 16)
        self.assertEqual(first["history"][-1]["turn"], 16)

    def test_trajectory_records_progression_fatigue_and_portfolio(self):
        result = run_trajectory(seed=23, focus="quality", turns=12)
        self.assertEqual(len(result["history"]), 12)
        self.assertIn("threshold", result["final_progression"])
        self.assertIn("vma", result["final_progression"])
        self.assertIn("final_fatigue", result)
        self.assertIn("acquired_sessions", result)
        for turn in result["history"]:
            self.assertIn("fatigue_total", turn)
            self.assertIn("newly_eligible", turn)
            self.assertIn("acquired_this_turn", turn)

    def test_invalid_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            run_trajectory(seed=1, focus="optimal", turns=16)


if __name__ == "__main__":
    unittest.main()
