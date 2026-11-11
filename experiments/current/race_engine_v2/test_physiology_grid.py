import unittest

from training_v2.physiology import PhysiologyCurve, PhysiologyPoint
from experiments.current.race_engine_v2.physiology_grid import (
    build_physiology_grid,
    resolve_race_segment,
)


def sample_curve():
    return PhysiologyCurve(
        ef=PhysiologyPoint(4, 8),
        threshold=PhysiologyPoint(8, 12),
        vma=PhysiologyPoint(12, 16),
    )


class PhysiologyGridTests(unittest.TestCase):
    def setUp(self):
        self.curve = sample_curve()
        self.grid = build_physiology_grid(self.curve)

    def test_printed_grid_contains_integer_energy_cells(self):
        self.assertEqual(
            [(cell.energy, cell.speed) for cell in self.grid.cells],
            [(energy, energy + 4) for energy in range(13)],
        )

    def test_anchor_values_are_preserved(self):
        self.assertEqual(self.grid.speed_at(4), 8)   # EF
        self.assertEqual(self.grid.speed_at(8), 12)  # Seuil
        self.assertEqual(self.grid.speed_at(12), 16) # VMA

    def test_interpolation_rounds_half_up(self):
        curve = PhysiologyCurve(
            ef=PhysiologyPoint(2, 5),
            threshold=PhysiologyPoint(4, 8),
            vma=PhysiologyPoint(6, 11),
        )
        grid = build_physiology_grid(curve)
        self.assertEqual(grid.speed_at(3), 7)

    def test_uphill_reduces_speed_without_increasing_reserve_spend(self):
        result = resolve_race_segment(
            grid=self.grid, energy_result=8, difficulty=2, reserve_remaining=20
        )
        self.assertEqual(result.effective_energy, 6)
        self.assertEqual(result.speed, 10)
        self.assertEqual(result.reserve_remaining, 12)
        self.assertEqual(result.energy_spent, 8)

    def test_downhill_increases_speed_without_increasing_energy_spend(self):
        result = resolve_race_segment(
            grid=self.grid, energy_result=8, difficulty=-2, reserve_remaining=20
        )
        self.assertEqual(result.effective_energy, 10)
        self.assertEqual(result.speed, 14)
        self.assertEqual(result.reserve_remaining, 12)

    def test_extrapolates_both_sides_and_floors_negative_speed_at_zero(self):
        self.assertEqual(self.grid.speed_at(14), 18)
        self.assertEqual(self.grid.speed_at(-10), 0)

    def test_vma_cap_applies_before_terrain(self):
        result = resolve_race_segment(
            grid=self.grid, energy_result=13, difficulty=-5, reserve_remaining=20
        )
        self.assertEqual(result.energy_spent, 12)
        self.assertEqual(result.effective_energy, 17)
        self.assertEqual(result.speed, 21)
        self.assertEqual(result.reserve_remaining, 8)

    def test_reserve_is_debited_by_actual_energy_spent(self):
        with self.assertRaisesRegex(ValueError, "reserve"):
            resolve_race_segment(
                grid=self.grid, energy_result=8, difficulty=3, reserve_remaining=7
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
