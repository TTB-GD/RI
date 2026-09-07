import unittest

from dice_progression import PlayerDicePool, choose_die_to_upgrade
from player_state import Player
from progression import PlayerProgress
from session_selector import choose_sessions_weighted


class TestSessionCatalogBusinessRules(unittest.TestCase):
    def test_initial_sessions_are_ef1_and_ef2(self):
        progress = PlayerProgress()
        self.assertEqual(progress.available_sessions(), ["EF1", "EF2"])

    def test_ef3_unlocks_after_two_ef2(self):
        progress = PlayerProgress()
        progress.record_session("EF2")
        self.assertNotIn("EF3", progress.available_sessions())
        progress.record_session("EF2")
        self.assertIn("EF3", progress.available_sessions())

    def test_spec4_unlocks_from_any_of_three_quality_paths(self):
        for session_name in ("Seuil3", "VMA3", "Force3"):
            progress = PlayerProgress()
            progress.record_session(session_name)
            self.assertNotIn("Spec4", progress.available_sessions())
            progress.record_session(session_name)
            self.assertIn("Spec4", progress.available_sessions())

    def test_sl5_unlocks_after_two_ef4(self):
        progress = PlayerProgress()
        progress.record_session("EF4")
        self.assertNotIn("SL5", progress.available_sessions())
        progress.record_session("EF4")
        self.assertIn("SL5", progress.available_sessions())

    def test_player_progress_exposes_catalog_availability(self):
        progress = PlayerProgress()
        progress.record_session("EF2")
        self.assertNotIn("EF3", progress.available_sessions())
        progress.record_session("EF2")
        self.assertIn("EF3", progress.available_sessions())


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

    def test_ctl_milestones_do_not_add_duplicate_dice(self):
        pool = PlayerDicePool()
        pool.maybe_add_dice(100)
        self.assertEqual(pool.sizes, [6, 6, 6, 6, 6, 6])
        pool.maybe_add_dice(100)
        self.assertEqual(pool.sizes, [6, 6, 6, 6, 6, 6])

    def test_quality_progression_upgrades_one_die_every_four_quality_sessions(self):
        pool = PlayerDicePool()
        pool.maybe_upgrade(3)
        self.assertEqual(pool.sizes, [6, 6, 6, 6])
        pool.maybe_upgrade(4)
        self.assertEqual(pool.sizes, [8, 6, 6, 6])
        pool.maybe_upgrade(8)
        self.assertEqual(pool.sizes, [8, 8, 6, 6])

    def test_quality_progression_caps_at_four_upgrades(self):
        pool = PlayerDicePool()
        pool.maybe_upgrade(20)
        self.assertEqual(pool.upgrades_used, 4)
        self.assertEqual(pool.sizes, [12, 12, 12, 12])

    def test_choose_die_to_upgrade_respects_concentration_weight(self):
        self.assertEqual(choose_die_to_upgrade([6, 6, 8, 10]), 2)


class TestProgressionBusinessRules(unittest.TestCase):
    def test_record_session_separates_ef_and_quality_counters(self):
        progress = PlayerProgress()
        progress.record_session("EF1")
        progress.record_session("Seuil3")
        self.assertEqual(progress.ef_total, 1)
        self.assertEqual(progress.quality_total, 1)
        self.assertEqual(progress.completions["EF1"], 1)
        self.assertEqual(progress.completions["Seuil3"], 1)


class TestPlayerStateBusinessRules(unittest.TestCase):
    def test_player_keeps_same_dice_pool_across_turns(self):
        player = Player()
        pool = player.dice_pool
        pool.maybe_add_dice(50)
        self.assertIs(player.dice_pool, pool)
        self.assertEqual(player.dice_pool.sizes, [6, 6, 6, 6, 6])


class TestSessionSelectorBusinessRules(unittest.TestCase):
    def test_selection_never_exceeds_energy_budget_or_rpe_max(self):
        sessions = [
            {"name": "EF1", "category": "EF", "energy": 3, "rpe": 3},
            {"name": "EF2", "category": "EF", "energy": 3, "rpe": 3},
            {"name": "Seuil3", "category": "Seuil", "energy": 5, "rpe": 5},
        ]
        chosen = choose_sessions_weighted(
            sessions,
            energy_draw=8,
            rpe_max=6,
            rng_seed=1,
        )
        self.assertLessEqual(sum(s["energy"] for s in chosen), 8)
        self.assertLessEqual(sum(s["rpe"] for s in chosen), 6)

    def test_only_one_sl_can_be_selected_per_turn(self):
        sessions = [
            {"name": "SL5", "category": "SL", "energy": 3, "rpe": 2},
            {"name": "SL6", "category": "SL", "energy": 3, "rpe": 2},
            {"name": "EF1", "category": "EF", "energy": 1, "rpe": 1},
        ]
        chosen = choose_sessions_weighted(
            sessions,
            energy_draw=10,
            rpe_max=10,
            rng_seed=1,
        )
        self.assertLessEqual(sum(s["category"] == "SL" for s in chosen), 1)

    def test_quality_sessions_require_ef_same_turn(self):
        sessions = [
            {"name": "Seuil3", "category": "Seuil", "energy": 1, "rpe": 1},
        ]
        chosen = choose_sessions_weighted(
            sessions,
            energy_draw=10,
            rpe_max=10,
            rng_seed=1,
        )
        self.assertEqual(chosen, [])

    def test_session_count_is_capped_at_seven(self):
        sessions = [
            {"name": f"EF{i}", "category": "EF", "energy": 1, "rpe": 0}
            for i in range(1, 8)
        ]
        chosen = choose_sessions_weighted(
            sessions,
            energy_draw=20,
            rpe_max=20,
            rng_seed=1,
        )
        self.assertLessEqual(len(chosen), 7)


if __name__ == "__main__":
    unittest.main()
