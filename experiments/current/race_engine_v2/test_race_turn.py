import unittest

from training_v2.physiology import PhysiologyCurve, PhysiologyPoint

from .physiology_grid import build_physiology_grid
from .race_turn import resolve_race_turn


class SequenceRng:
    def __init__(self, values):
        self.values = iter(values)

    def randint(self, low, high):
        value = next(self.values)
        if not low <= value <= high:
            raise AssertionError(f"{value} outside [{low}, {high}]")
        return value


CURVE = PhysiologyCurve(
    ef=PhysiologyPoint(2, 4),
    threshold=PhysiologyPoint(5, 8),
    vma=PhysiologyPoint(8, 12),
)
GRID = build_physiology_grid(CURVE)
POOL = (6, 6, 6, 6)


class RaceTurnDiceActionTests(unittest.TestCase):
    def test_keep_uses_n_minus_one_dice_and_downhill_grid_conversion(self):
        result = resolve_race_turn(
            pool_sizes=POOL, grid=GRID, difficulty=-2,
            reserve_remaining=20, action="keep",
            rng=SequenceRng((1, 2, 3)),
        )
        self.assertEqual(result.initial_roll.final_values, (1, 2, 3))
        self.assertEqual(result.dice.energy, 6)
        self.assertEqual(result.segment.energy_spent, 6)
        self.assertEqual(result.segment.effective_energy, 8)
        self.assertEqual(result.segment.speed, 12)
        self.assertEqual(result.segment.reserve_remaining, 14)

    def test_add_rolls_the_reserved_smallest_die_only_when_selected(self):
        result = resolve_race_turn(
            pool_sizes=POOL, grid=GRID, difficulty=0,
            reserve_remaining=20, action="add",
            rng=SequenceRng((1, 2, 3, 4)),
        )
        self.assertEqual(result.initial_roll.raw_faces, (1, 2, 3, None))
        self.assertEqual(result.dice.final_values, (1, 2, 3, 4))
        self.assertEqual(result.dice.energy, 10)
        self.assertEqual(result.segment.energy_spent, 8)  # VMA clipping
        self.assertEqual(result.segment.reserve_remaining, 12)

    def test_reroll_replaces_one_active_die(self):
        result = resolve_race_turn(
            pool_sizes=POOL, grid=GRID, difficulty=1,
            reserve_remaining=20, action="reroll", reroll_index=0,
            rng=SequenceRng((1, 2, 3, 6)),
        )
        self.assertEqual(result.dice.final_values, (6, 2, 3))
        self.assertEqual(result.dice.energy, 11)
        self.assertEqual(result.segment.energy_spent, 8)
        self.assertEqual(result.segment.effective_energy, 7)
        self.assertEqual(result.segment.reserve_remaining, 12)

    def test_add_and_reroll_apply_both_operations(self):
        result = resolve_race_turn(
            pool_sizes=POOL, grid=GRID, difficulty=0,
            reserve_remaining=20, action="add+reroll", reroll_index=1,
            rng=SequenceRng((1, 2, 3, 5, 4)),
        )
        self.assertEqual(result.dice.final_values, (1, 5, 3, 4))
        self.assertEqual(result.dice.energy, 13)
        self.assertEqual(result.segment.energy_spent, 8)

    def test_keep_does_not_roll_the_reserved_die(self):
        rng = SequenceRng((1, 2, 3))
        resolve_race_turn(
            pool_sizes=POOL, grid=GRID, difficulty=0,
            reserve_remaining=20, action="keep", rng=rng,
        )
        with self.assertRaises(StopIteration):
            rng.randint(1, 6)

    def test_insufficient_reserve_is_not_silently_reinterpreted(self):
        with self.assertRaisesRegex(ValueError, "exceeds remaining race reserve"):
            resolve_race_turn(
                pool_sizes=POOL, grid=GRID, difficulty=0,
                reserve_remaining=5, action="keep",
                rng=SequenceRng((1, 2, 3)),
            )

    def test_reroll_requires_an_active_die_index(self):
        with self.assertRaisesRegex(ValueError, "valid active die index"):
            resolve_race_turn(
                pool_sizes=POOL, grid=GRID, difficulty=0,
                reserve_remaining=20, action="reroll",
                rng=SequenceRng((1, 2, 3)),
            )


if __name__ == "__main__":
    unittest.main()
