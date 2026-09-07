import unittest

from decision_engine import energy_and_fatigue
from patterns import pattern_signature
from session_effects import session_outcome
from session_selector import choose_sessions_weighted
from sessions_catalog import available_sessions


class TestDecisionEngineCharacterization(unittest.TestCase):
    def test_energy_and_fatigue_curve(self):
        # TN = 20: characterize the current quasi-Fibonacci curve.
        expected = {
            16: (16, -1),
            17: (17, 0),
            18: (18, 0),
            19: (19, 1),
            20: (20, 2),
            21: (21, 3),
            22: (22, 5),
            23: (23, 8),
            24: (24, 13),
        }
        for spend, result in expected.items():
            with self.subTest(spend=spend):
                self.assertEqual(energy_and_fatigue(spend, 20), result)

    def test_half_away_from_zero_rounding(self):
        self.assertEqual(energy_and_fatigue(20.5, 20), (20.5, 3))
        self.assertEqual(energy_and_fatigue(19.5, 20), (19.5, 1))


class TestSessionEffectsCharacterization(unittest.TestCase):
    def test_four_of_a_kind_gives_three_sessions_and_pool_bonus(self):
        result = session_outcome([6, 6, 6, 6], [6, 6, 6, 6], 4)
        self.assertEqual(result["signature"], (4,))
        self.assertEqual(result["sessions"], 3)
        self.assertTrue(result["bonus_pool"])
        self.assertEqual(result["total"], 24)
        self.assertIsNone(result["dice_dropped"])

    def test_five_dice_without_bonus_drop_lowest(self):
        result = session_outcome([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 5)
        self.assertEqual(result["signature"], (1, 1, 1, 1, 1))
        self.assertEqual(result["sessions"], 1)
        self.assertFalse(result["bonus_pool"])
        self.assertEqual(result["dice_dropped"], 1)
        self.assertEqual(result["dice_used"], [5, 4, 3, 2])
        self.assertEqual(result["total"], 14)


class TestSessionSelectorCharacterization(unittest.TestCase):
    def test_quality_requires_ef_in_same_turn(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "Seuil3"],
            energy_budget=4,
            rpe_max=3,
            tn=10,
        )
        self.assertIn("EF1", chosen)
        self.assertIn("Seuil3", chosen)
        self.assertLessEqual(
            sum(1 for name in chosen if name.startswith("Seuil")),
            sum(1 for name in chosen if name.startswith("EF")),
        )

    def test_long_run_is_limited_to_one_per_turn(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "SL5", "SL5"],
            energy_budget=20,
            rpe_max=5,
            tn=10,
        )
        self.assertLessEqual(sum(name.startswith("SL") for name in chosen), 1)

    def test_session_count_is_capped_at_seven(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1"],
            energy_budget=20,
            rpe_max=1,
            tn=10,
        )
        self.assertEqual(len(chosen), 7)


class TestCatalogCharacterization(unittest.TestCase):
    def test_initial_sessions_are_ef1_and_ef2(self):
        self.assertEqual(available_sessions({}), ["EF1", "EF2"])

    def test_pattern_signature_is_sorted_by_multiplicity(self):
        self.assertEqual(pattern_signature([6, 6, 3, 3, 3]), (3, 2))


if __name__ == "__main__":
    unittest.main()
