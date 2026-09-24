import unittest

from experiments.current.bust_trigger.run import (
    check_candidate_bust,
    first_bust_index,
    risk_die_size,
    selector_risk_gap,
    theoretical_bust_probability,
)


class TestCandidateBustTriggerHarness(unittest.TestCase):
    def test_non_risky_quality_is_not_rolled(self):
        check = check_candidate_bust("Seuil3", 4, 8, 1)
        self.assertFalse(check.risky)
        self.assertFalse(check.bust)
        self.assertIsNone(check.roll)

    def test_gap_one_busts_on_one_and_passes_on_two(self):
        self.assertTrue(check_candidate_bust("Seuil5", 4, 6, 1).bust)
        self.assertFalse(check_candidate_bust("Seuil5", 4, 6, 2).bust)

    def test_gap_two_boundary(self):
        self.assertTrue(check_candidate_bust("VMA6", 4, 8, 2).bust)
        self.assertFalse(check_candidate_bust("VMA6", 4, 8, 3).bust)

    def test_largest_pool_die_is_candidate_risk_die(self):
        self.assertEqual(risk_die_size([6, 6, 8, 10]), 10)

    def test_first_bust_stops_later_risk_tests(self):
        planned = ["EF1", "Seuil5", "VMA6", "Force5"]
        index, checks = first_bust_index(
            planned,
            rpe_max=4,
            pool_sizes=[6, 8],
            risk_rolls=[5, 2, 1],
        )
        self.assertEqual(index, 2)
        self.assertEqual(len(checks), 2)
        self.assertEqual(checks[-1].session, "VMA6")
        self.assertTrue(checks[-1].bust)

    def test_exact_probability(self):
        self.assertAlmostEqual(theoretical_bust_probability(1, 6), 1 / 6)
        self.assertAlmostEqual(theoretical_bust_probability(2, 10), 0.2)
        self.assertAlmostEqual(theoretical_bust_probability(4, 12), 1 / 3)

    def test_current_selector_cannot_plan_risky_quality(self):
        probe = selector_risk_gap()
        self.assertFalse(probe["risky_quality_planned"])
        self.assertNotIn("Seuil5", probe["chosen"])


if __name__ == "__main__":
    unittest.main()
