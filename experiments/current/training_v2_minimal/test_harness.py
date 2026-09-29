"""Tests for the isolated Training V2 experiment, not CURRENT behavior."""

import unittest

from experiments.current.training_v2_minimal.harness import (
    affordable_programs, experiment_a, experiment_a2, experiment_c,
    legal_partitions, quality_cost, resolve_roll, simulate, simulate_b2,
)


class TrainingV2HarnessTests(unittest.TestCase):
    def test_cost_boundaries(self):
        self.assertEqual(quality_cost(8, 6), 3)
        self.assertEqual(quality_cost(12, 6), 7)
        self.assertEqual(quality_cost(13, 6), 9)
        self.assertEqual(quality_cost(28, 6), 27)

    def test_example_partitions_are_physical_and_legal(self):
        rows = legal_partitions((5, 4, 3, 2))
        energies = {(ef, q) for ef, q, _ in rows}
        self.assertTrue({(9, 5), (8, 6), (7, 7)} <= energies)
        self.assertNotIn((5, 9), energies)
        self.assertTrue(all(ef >= q for ef, q, _ in rows))

    def test_d99_only_controls_reserve(self):
        self.assertEqual(resolve_roll((5, 5, 3, 3)), (5, 5, 3, 3))
        self.assertEqual(resolve_roll((6, 5, 4, 3)), (6, 5, 4))
        self.assertEqual(resolve_roll((5, 5, 3, 3), "D99_OFF"), (5, 5, 3))

    def test_exhaustive_a_is_stable(self):
        result = experiment_a()
        self.assertEqual(result["raw_outcomes"], 1296)
        self.assertEqual(result["criterion"], "CHOIX REEL")

    def test_longitudinal_is_reproducible_and_ordered(self):
        first, _ = simulate(17, "P_BALANCED")
        second, _ = simulate(17, "P_BALANCED")
        self.assertEqual(first, second)
        self.assertLess(first["EF"], first["SEUIL"])
        self.assertLess(first["SEUIL"], first["VMA"])

    def test_c_profiles_share_spec_investment(self):
        rows = experiment_c()["rows"]
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["speed"] + -row["eco"] == 4 for row in rows))

    def test_a2_requires_sum_of_costs_for_double_quality(self):
        self.assertNotIn(("SEUIL", "VMA"),
                         [row["qualities"] for row in affordable_programs(7, 6, 8, 10)])
        double = next(row for row in affordable_programs(9, 6, 8, 10)
                      if row["qualities"] == ("SEUIL", "VMA"))
        self.assertEqual((double["consumed"], double["remainder"]), (8, 1))

    def test_a2_is_exhaustive_and_uses_true_simultaneous_program(self):
        result = experiment_a2()
        self.assertEqual(result["raw_outcomes"], 1296)
        self.assertLess(result["seuil_plus_vma_same_partition_pct"], result["vma_pct"])

    def test_q_spent_spec_conserves_q_energy_except_bust_loss(self):
        record, _ = simulate_b2(17, "P_QUALITY", "Q_SPENT_SPEC")
        self.assertEqual(record["q_available"], record["q_consumed"]
                         + record["q_to_spec"] + record["q_lost_bust"])
        self.assertEqual(record["progression_Q"], record["q_consumed"])

    def test_b2_is_reproducible(self):
        first, _ = simulate_b2(29, "P_BALANCED", "Q_FULL")
        second, _ = simulate_b2(29, "P_BALANCED", "Q_FULL")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
