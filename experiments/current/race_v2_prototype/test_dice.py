import random
import unittest

from .dice import (
    reroll_capital,
    resolve_dice_decision,
    roll_dice_pool,
)


class RerollCapitalTests(unittest.TestCase):
    def test_base_capital_uses_highest_die_and_affutage_tier(self):
        self.assertEqual(reroll_capital(dice_sizes=(6, 6, 8), sector_count=7, affutage_level=4), 2)
        self.assertEqual(reroll_capital(dice_sizes=(6, 10), sector_count=7, affutage_level=2), 2)
        self.assertEqual(reroll_capital(dice_sizes=(6, 12), sector_count=7, affutage_level=1), 1)
        self.assertEqual(reroll_capital(dice_sizes=(6, 12), sector_count=7, affutage_level=0), 0)

    def test_distance_scaling_and_ceiling_are_applied_after_product(self):
        self.assertEqual(reroll_capital(dice_sizes=(12,), sector_count=10, affutage_level=1), 2)
        self.assertEqual(reroll_capital(dice_sizes=(12,), sector_count=13, affutage_level=1), 2)
        self.assertEqual(reroll_capital(dice_sizes=(12,), sector_count=16, affutage_level=1), 3)

    def test_invalid_capital_inputs_are_rejected(self):
        for sizes, sectors, tier in [((4,), 7, 4), ((6,), 8, 4), ((6,), 7, 5), ((), 7, 4)]:
            with self.subTest(sizes=sizes, sectors=sectors, tier=tier):
                with self.assertRaises(ValueError):
                    reroll_capital(dice_sizes=sizes, sector_count=sectors, affutage_level=tier)


class DiceDecisionTests(unittest.TestCase):
    def test_full_pool_is_rolled_with_reproducible_rng(self):
        a = roll_dice_pool((6, 8, 10, 12), random.Random(42))
        b = roll_dice_pool((6, 8, 10, 12), random.Random(42))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4)
        self.assertTrue(all(1 <= face <= size for face, size in zip(a, (6, 8, 10, 12))))

    def test_individual_reroll_replaces_face_and_consumes_one_unit(self):
        result = resolve_dice_decision(
            dice_sizes=(6, 8),
            initial_faces=(1, 8),
            reroll_indices=(0,),
            selected_indices=(0, 1),
            rerolls_remaining=2,
            rng=random.Random(3),
        )
        self.assertNotEqual(result.final_faces[0], 1)
        self.assertEqual(result.final_faces[1], 8)
        self.assertEqual(result.rerolls_used, 1)
        self.assertEqual(result.rerolls_remaining, 1)
        self.assertEqual(result.energy_spent, sum(result.final_faces))

    def test_same_die_can_be_rerolled_more_than_once(self):
        result = resolve_dice_decision(
            dice_sizes=(6,),
            initial_faces=(1,),
            reroll_indices=(0, 0),
            selected_indices=(0,),
            rerolls_remaining=2,
            rng=random.Random(5),
        )
        self.assertEqual(result.rerolls_used, 2)
        self.assertEqual(result.rerolls_remaining, 0)

    def test_empty_subset_spends_no_energy(self):
        result = resolve_dice_decision(
            dice_sizes=(6, 8),
            initial_faces=(4, 7),
            reroll_indices=(),
            selected_indices=(),
            rerolls_remaining=1,
            rng=random.Random(1),
        )
        self.assertEqual(result.energy_spent, 0)
        self.assertEqual(result.selected_indices, ())

    def test_unselected_dice_are_not_spent(self):
        result = resolve_dice_decision(
            dice_sizes=(6, 8, 10),
            initial_faces=(4, 7, 9),
            reroll_indices=(),
            selected_indices=(0, 2),
            rerolls_remaining=0,
            rng=random.Random(1),
        )
        self.assertEqual(result.energy_spent, 13)

    def test_invalid_or_over_budget_decisions_are_rejected(self):
        common = dict(
            dice_sizes=(6, 8),
            initial_faces=(3, 4),
            selected_indices=(0,),
            rerolls_remaining=1,
            rng=random.Random(1),
        )
        with self.assertRaises(ValueError):
            resolve_dice_decision(**common, reroll_indices=(0, 1))
        with self.assertRaises(ValueError):
            resolve_dice_decision(**common, reroll_indices=(2,))
        with self.assertRaises(ValueError):
            resolve_dice_decision(**{**common, "selected_indices": (0, 0)}, reroll_indices=())


if __name__ == "__main__":
    unittest.main()
