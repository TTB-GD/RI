"""Tests ciblés des règles métier du jeu.

Ces tests complètent les tests de caractérisation sans modifier le code métier.
Ils couvrent principalement les transitions d'état : déblocages, progression
du pool de dés, compteurs de progression et contraintes de sélection.
"""
import unittest

from dice_progression import PlayerDicePool, choose_die_to_upgrade
from player_state import Player
from progression import PlayerProgress
from session_selector import choose_sessions_weighted
from sessions_catalog import available_sessions


class TestSessionCatalogBusinessRules(unittest.TestCase):
    def test_initial_sessions_are_ef1_and_ef2(self):
        progress = PlayerProgress()
        self.assertEqual(available_sessions(progress), ["EF1", "EF2"])

    def test_ef3_unlocks_after_two_ef2(self):
        progress = PlayerProgress()
        progress.record_session("EF2")
        self.assertNotIn("EF3", available_sessions(progress))
        progress.record_session("EF2")
        self.assertIn("EF3", available_sessions(progress))

    def test_spec4_unlocks_from_any_of_three_quality_paths(self):
        for prerequisite in ("Force3", "VMA3", "Seuil3"):
            progress = PlayerProgress()
            progress.record_session("EF2")
            progress.record_session("EF2")
            progress.record_session(prerequisite)
            progress.record_session(prerequisite)
            self.assertIn("Spec4", available_sessions(progress))

    def test_sl5_unlocks_after_two_ef4(self):
        progress = PlayerProgress()
        for _ in range(2):
            progress.record_session("EF2")
        for _ in range(2):
            progress.record_session("EF3")
        for _ in range(2):
            progress.record_session("EF4")
        self.assertIn("SL5", available_sessions(progress))

    def test_newly_unlocked_session_is_available_on_next_query(self):
        progress = PlayerProgress()
        progress.record_session("EF2")
        self.assertNotIn("EF3", ["EF1", "EF2"])
        self.assertIn("EF3", available_sessions(progress))


class TestDiceProgressionBusinessRules(unittest.TestCase):
    def test_ctl_milestones_add_one_die_at_50_and_100(self):
        pool = PlayerDicePool()
        self.assertEqual(pool.sizes, [6, 6, 6, 6])

        pool.maybe_add_dice(49)
        self.assertEqual(pool.sizes, [6, 6, 6, 6])

        pool.maybe_add_dice(50)
        self.assertEqual(pool.sizes, [6, 6, 6, 6, 6])

        pool.maybe_add_dice(100)
        self.assertEqual(pool.sizes, [6, 6, 6, 6, 6, 6])

    def test_ctl_milestones_are_not_duplicated(self):
        pool = PlayerDicePool()
        pool.maybe_add_dice(100)
        pool.maybe_add_dice(100)
        pool.maybe_add_dice(150)
        self.assertEqual(len(pool.sizes), 6)

    def test_quality_upgrades_follow_four_session_steps_and_cap(self):
        pool = PlayerDicePool()

        for quality_total, expected_upgrades, expected_sizes in (
            (3, 0, [6, 6, 6, 6]),
            (4, 1, [8, 6, 6, 6]),
            (8, 2, [8, 8, 6, 6]),
            (12, 3, [8, 8, 8, 6]),
            (16, 4, [8, 8, 8, 8]),
            (20, 4, [8, 8, 8, 8]),
        ):
            current = PlayerDicePool()
            current.maybe_upgrade(quality_total)
            self.assertEqual(current.upgrades_used, expected_upgrades)
            self.assertEqual(current.sizes, expected_sizes)

    def test_upgrade_sequence_is_d6_d8_d10_d12(self):
        pool = PlayerDicePool()
        for total, expected in (
            (4, [8, 6, 6, 6]),
            (8, [8, 8, 6, 6]),
            (12, [8, 8, 8, 6]),
            (16, [8, 8, 8, 8]),
        ):
            pool.maybe_upgrade(total)
            self.assertEqual(pool.sizes, expected)

        pool.maybe_upgrade(20)
        self.assertEqual(pool.sizes, [8, 8, 8, 8])

    def test_choose_die_to_upgrade_respects_concentration_weight(self):
        self.assertEqual(
            choose_die_to_upgrade([6, 8, 10, 12], {"w_concentration": 1.0, "w_spread": 0.0}),
            2,
        )

    def test_player_keeps_persistent_dice_pool_state(self):
        player = Player()
        player.dice_pool.maybe_add_dice(50)
        player.dice_pool.maybe_upgrade(4)
        self.assertEqual(player.dice_pool.sizes, [8, 6, 6, 6, 6])
        self.assertEqual(player.dice_pool.dice_added, 1)
        self.assertEqual(player.dice_pool.upgrades_used, 1)


class TestProgressionCountersBusinessRules(unittest.TestCase):
    def test_ef_and_quality_counters_are_separate(self):
        progress = PlayerProgress()
        progress.record_session("EF1")
        progress.record_session("Seuil3")
        progress.record_session("VMA3")

        self.assertEqual(progress.ef_total, 1)
        self.assertEqual(progress.quality_total, 2)
        self.assertEqual(progress.completions["EF1"], 1)
        self.assertEqual(progress.completions["Seuil3"], 1)
        self.assertEqual(progress.completions["VMA3"], 1)


class TestSessionSelectorBusinessRules(unittest.TestCase):
    def test_selection_never_exceeds_energy_budget_or_rpe_max(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "EF2", "EF3", "Seuil3", "VMA3"],
            energy_budget=10,
            rpe_max=5,
            tn=10,
            weights={"w_energy": 3.0, "w_sessions": 1.5, "w_fatigue": 0.25, "w_rpe": 0.25},
        )
        self.assertLessEqual(sum((3 if name.startswith("EF") else 5) for name in chosen), 10)
        self.assertTrue(all((3 if name.startswith("EF") else 5) <= 5 for name in chosen))

    def test_quality_sessions_never_exceed_ef_sessions_in_same_turn(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "EF2", "Seuil3", "VMA3", "Force3"],
            energy_budget=50,
            rpe_max=10,
            tn=10,
            weights={"w_energy": 3.0, "w_sessions": 1.5, "w_fatigue": 0.0, "w_rpe": 0.25},
        )
        ef_count = sum(name.startswith("EF") for name in chosen)
        quality_count = len(chosen) - ef_count
        self.assertLessEqual(quality_count, ef_count)

    def test_at_most_one_long_run_per_turn(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "EF2", "SL5", "SL6"],
            energy_budget=50,
            rpe_max=10,
            tn=10,
            weights={"w_energy": 3.0, "w_sessions": 1.5, "w_fatigue": 0.0, "w_rpe": 0.25},
        )
        self.assertLessEqual(sum(name.startswith("SL") for name in chosen), 1)

    def test_repeated_non_sl_categories_are_allowed_when_affordable(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "EF2", "EF3"],
            energy_budget=20,
            rpe_max=10,
            tn=10,
            weights={"w_energy": 3.0, "w_sessions": 1.5, "w_fatigue": 0.0, "w_rpe": 0.25},
        )
        self.assertGreaterEqual(sum(name.startswith("EF") for name in chosen), 2)

    def test_selection_is_capped_at_seven_sessions(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "EF2", "EF3", "EF4", "EF5", "Seuil3", "VMA3", "Force3"],
            energy_budget=100,
            rpe_max=10,
            tn=100,
            weights={"w_energy": 3.0, "w_sessions": 1.5, "w_fatigue": 0.0, "w_rpe": 0.25},
        )
        self.assertLessEqual(len(chosen), 7)


if __name__ == "__main__":
    unittest.main()
