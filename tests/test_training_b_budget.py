"""Tests for the Training B energy-budget conservation boundary."""
import unittest

from training_v2.budget import TrainingEnergyBudget


class TrainingEnergyBudgetTests(unittest.TestCase):
    def test_quality_is_threshold_plus_vma(self):
        budget = TrainingEnergyBudget.from_split(
            total_energy=31,
            ef_energy=13,
            threshold_energy=10,
            vma_energy=8,
        )
        self.assertEqual(budget.quality_energy, 18)
        self.assertEqual(
            budget.ef_energy + budget.quality_energy,
            budget.total_energy,
        )

    def test_both_quality_filiere_can_be_funded_in_one_turn(self):
        budget = TrainingEnergyBudget(20, 8, 7, 5)
        self.assertEqual((budget.threshold_energy, budget.vma_energy), (7, 5))

    def test_zero_allocation_to_a_filiere_is_valid(self):
        budget = TrainingEnergyBudget(12, 12, 0, 0)
        self.assertEqual(budget.quality_energy, 0)

    def test_rejects_energy_creation_or_loss(self):
        with self.assertRaisesRegex(ValueError, "conserve total energy"):
            TrainingEnergyBudget(20, 8, 7, 4)

    def test_rejects_negative_energy(self):
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            TrainingEnergyBudget(10, 12, -2, 0)

    def test_rejects_non_integer_energy(self):
        with self.assertRaises(TypeError):
            TrainingEnergyBudget(10, 5, 2.5, 2)


if __name__ == "__main__":
    unittest.main()
