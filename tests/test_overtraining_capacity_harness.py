import random
import unittest

from overtraining_capacity_harness import (BUST, NORMAL, SUCCESS, UNTESTED,
                                           deterministic_scenarios, resolve,
                                           v1_components)


class TestFatigueV1Tables(unittest.TestCase):
    def test_q_and_recovery_boundaries_match_closed_v1_table(self):
        expected = {
            -8: (0, -4), -7: (0, -4), -6: (0, -3), -5: (0, -2), -4: (0, -1),
            -3: (0, 0), -1: (0, 0), 0: (0, 0), 1: (1, 0), 2: (2, 0),
            3: (3, 0), 4: (5, 0), 5: (8, 0), 6: (13, 0), 9: (13, 0),
        }
        for offset, (q, recovery) in expected.items():
            with self.subTest(offset=offset):
                self.assertEqual(v1_components(14 + offset, 14)[1:], (q, recovery))

    def test_bust_keeps_normals_and_stops_later_risk_tests(self):
        random.seed(1)  # d6 -> 2, so RPE 3 above RPE max 1 busts
        rows = resolve(["EF1", "Seuil3", "VMA3", "EF1"], 1, 6)
        self.assertEqual([row["status"] for row in rows], [NORMAL, BUST, UNTESTED, NORMAL])
        self.assertEqual(rows[1]["bust_roll"], 2)
        self.assertIsNone(rows[2]["bust_roll"])


class TestDeterministicCapacityScenarios(unittest.TestCase):
    def test_q_s_and_recovery_scenarios_cross_and_return_at_boundary(self):
        scenarios = deterministic_scenarios()
        self.assertTrue(scenarios["A_q_seul"][0]["overtraining"])
        self.assertTrue(scenarios["B_s_seul"][2]["overtraining"])
        recovery = scenarios["D_recuperation"]
        self.assertTrue(recovery[0]["removed"])
        self.assertTrue(recovery[-1]["recovered"])
        self.assertLessEqual(recovery[-1]["fatigue"], 6)


if __name__ == "__main__":
    unittest.main()
