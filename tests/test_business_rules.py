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
        self.assertEqual(pool.sizes, [8, 8, 8, 8])

    def test_added_fifth_die_is_eligible_for_upgrade(self):
        pool = PlayerDicePool()
        pool.maybe_add_dice(50)
        pool.maybe_upgrade(4)
        self.assertEqual(pool.sizes, [8, 6, 6, 6, 6])
        self.assertEqual(pool.upgrades_used, 1)

    def test_added_sixth_die_is_eligible_for_upgrade(self):
        pool = PlayerDicePool()
        pool.maybe_add_dice(100)
        pool.maybe_upgrade(4)
        self.assertEqual(pool.sizes, [8, 6, 6, 6, 6, 6])
        self.assertEqual(pool.upgrades_used, 1)

    def test_four_upgrade_budget_is_global_across_all_six_dice(self):
        pool = PlayerDicePool()
        pool.maybe_add_dice(100)
        pool.maybe_upgrade(20)
        self.assertEqual(pool.upgrades_used, 4)
        self.assertEqual(pool.sizes, [8, 8, 8, 8, 6, 6])
        self.assertNotEqual(pool.sizes, [12, 8, 8, 8, 6, 6])

    def test_mixed_pool_respects_spread_profile(self):
        pool = PlayerDicePool(sizes=[12, 8, 6, 6])
        pool.maybe_upgrade(4)
        self.assertEqual(pool.sizes, [12, 8, 8, 6])

    def test_choose_die_to_upgrade_respects_concentration_weight(self):
        weights = {"w_concentration": 2.0, "w_spread": 1.0}
        self.assertEqual(choose_die_to_upgrade([6, 6, 8, 10], weights), 3)


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
        chosen, _ = choose_sessions_weighted(
            ["EF1", "EF2", "Seuil3"],
            energy_budget=8,
            rpe_max=6,
            tn=10,
            quality_limit=3,
        )
        self.assertLessEqual(sum({"EF1": 1, "EF2": 2, "Seuil3": 3}[name] for name in chosen), 8)
        self.assertLessEqual(max(({"EF1": 1, "EF2": 2, "Seuil3": 3}[name] for name in chosen), default=0), 6)

    def test_only_one_sl_can_be_selected_per_turn(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "SL5", "SL5"],
            energy_budget=20,
            rpe_max=5,
            tn=10,
            quality_limit=3,
        )
        self.assertLessEqual(sum(name.startswith("SL") for name in chosen), 1)

    def test_quality_sessions_require_ef_same_turn(self):
        chosen, _ = choose_sessions_weighted(
            ["Seuil3"],
            energy_budget=10,
            rpe_max=10,
            tn=10,
            quality_limit=3,
        )
        self.assertEqual(chosen, [])

    def test_quality_entry_cannot_repeat_when_ef_quota_allows_it(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "Seuil3"],
            energy_budget=20,
            rpe_max=10,
            tn=10,
            quality_limit=3,
            weights={
                "w_energy": 0.0,
                "w_sessions": 10.0,
                "w_fatigue": 0.0,
                "w_rpe": 0.0,
            },
        )
        ef_count = sum(name == "EF1" for name in chosen)
        quality_count = sum(name == "Seuil3" for name in chosen)
        self.assertGreaterEqual(ef_count, 2)
        self.assertEqual(quality_count, 1)
        self.assertLessEqual(quality_count, ef_count)

    def test_long_run_is_prioritized_when_ef_and_sl_are_affordable(self):
        chosen, trace = choose_sessions_weighted(
            ["EF1", "EF2", "SL5"],
            energy_budget=7,
            rpe_max=5,
            tn=10,
            quality_limit=3,
        )
        self.assertIn("SL5", chosen)
        self.assertEqual(chosen[0], "EF2")
        self.assertEqual(chosen[1], "SL5")
        self.assertEqual(trace[1]["note"], "priorite_SL")

    def test_long_run_is_not_selected_without_affordable_ef(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "SL5"],
            energy_budget=5,
            rpe_max=0,
            tn=10,
            quality_limit=3,
        )
        self.assertEqual(chosen, [])
        self.assertNotIn("SL5", chosen)

    def test_session_count_is_capped_at_seven(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1"],
            energy_budget=20,
            rpe_max=1,
            tn=10,
            quality_limit=3,
            weights={
                "w_energy": 3.0,
                "w_sessions": 1.5,
                "w_fatigue": 0.0,
                "w_rpe": 0.25,
            },
        )
        self.assertEqual(len(chosen), 7)


if __name__ == "__main__":
    unittest.main()
