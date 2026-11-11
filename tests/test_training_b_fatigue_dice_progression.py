import unittest

from decision_engine import energy_and_fatigue
from training_v2.dice_progression import add_die, upgrade_die
from training_v2.state import PlayerState


class TrainingBFatigueAndDiceProgressionTests(unittest.TestCase):
    def test_quasi_fibonacci_curve_uses_ceiling_for_fractional_tn_offset(self):
        # Five d6 have TN 17.5. A +1.5 deviation rounds upward to +2,
        # which maps to F(5) = 5 on the historical curve.
        self.assertEqual(energy_and_fatigue(19, 17.5), (19, 5))

    def test_negative_fractional_offset_is_rounded_toward_positive_infinity(self):
        # -1.5 rounds upward to -1, preserving the historical F(2) = 1 rule.
        self.assertEqual(energy_and_fatigue(16, 17.5), (16, 1))

    def test_exact_tn_keeps_historical_fibonacci_fatigue(self):
        self.assertEqual(energy_and_fatigue(14, 14), (14, 2))

    def test_upgrade_is_chosen_by_player_not_smallest_die(self):
        state = PlayerState(dice_pool=[6, 8, 6, 10])
        upgrade_die(state, 1)
        self.assertEqual(state.dice_pool, [6, 10, 6, 10])
        self.assertEqual(state.upgrades_used, 1)

    def test_upgrade_advances_one_step_and_rejects_d12(self):
        state = PlayerState(dice_pool=[6, 8, 10, 12])
        upgrade_die(state, 2)
        self.assertEqual(state.dice_pool, [6, 8, 12, 12])
        with self.assertRaises(ValueError):
            upgrade_die(state, 3)

    def test_add_die_is_capped_at_six(self):
        state = PlayerState()
        add_die(state)
        add_die(state)
        self.assertEqual(state.dice_pool, [6, 6, 6, 6, 6, 6])
        with self.assertRaises(ValueError):
            add_die(state)


if __name__ == "__main__":
    unittest.main()
