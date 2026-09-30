import unittest
from unittest.mock import patch

from physiology import PhysiologyProfile

from .core import (
    PolicyView,
    ProductionOptions,
    physiologically_available_productions,
    production_cost,
    run_race,
)
from .fixtures import DicePool
from .policies import POLICIES


PROFILE = PhysiologyProfile(3, 6, 10)
POOL = DicePool("fixture", (6, 6), "deterministic integration test")
POOL3 = DicePool("fixture-3", (6, 6, 6), "deterministic integration test")


class PhysiologyRaceIntegrationTests(unittest.TestCase):
    def test_available_and_payable_boundaries_are_separate(self):
        options = ProductionOptions((1, 4, 8, 9), {})
        available = physiologically_available_productions(options, PROFILE, 2)
        self.assertEqual(available, (1, 4, 8))
        self.assertEqual(production_cost(1, 0, PROFILE), 3)
        self.assertEqual(production_cost(8, 2, PROFILE), 21)

    def test_first_three_segments_filter_vma_but_not_reserve_and_clamp_after_s3(self):
        rolls = ((5, 5),) * 4
        seen = []

        def spy(view):
            seen.append(view)
            return max(view.payable)

        with patch("experiments.current.race_engine_v2.core.generate_rolls", return_value=rolls):
            course = run_race(
                seed=1, pool=POOL, race_length=4, policy=spy, ctl=0,
                freshness_bonus=0, long_run_preparation=False,
                physiology_profile=PROFILE, form_mode="PATTERN",
            )

        self.assertEqual([view.available for view in seen[:3]], [(5, 10)] * 3)
        self.assertEqual([view.payable for view in seen[:3]], [(5, 10)] * 3)
        self.assertIsNone(seen[0].final_reserve)
        self.assertIsNone(seen[1].final_reserve)
        self.assertIsNotNone(seen[2].final_reserve)
        self.assertEqual(course["final_reserve"], course["turns"][2]["spent"])
        self.assertTrue(course["reserve_floor_clamped"])
        self.assertTrue(course["dnf"])
        self.assertEqual(course["dnf_turn"], 4)

    def test_s4_menu_keeps_only_legal_and_payable_productions(self):
        rolls = ((1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 4, 6))
        seen = []

        def choose_low_then_observe(view):
            seen.append(view)
            return min(view.payable)

        with patch("experiments.current.race_engine_v2.core.generate_rolls", return_value=rolls):
            run_race(
                seed=2, pool=POOL3, race_length=4, policy=choose_low_then_observe,
                ctl=0, freshness_bonus=10, long_run_preparation=False,
                physiology_profile=PROFILE, form_mode="PATTERN", difficulty_profile=(0, 0, 0, 2),
            )

        fourth = seen[3]
        self.assertNotIn(9, fourth.available)  # Charge 11: outside VMA.
        self.assertIn(7, fourth.available)
        self.assertNotIn(7, fourth.payable)  # Legal, but too expensive.
        self.assertIn(1, fourth.payable)

    def test_policies_use_profile_cost_and_receive_only_legal_options(self):
        view = PolicyView(
            4, 6, (1, 4, 8), (1, 4, 8), 0, 20, 0, 0, 20, 7.0, None,
            current_difficulty=2, remaining_difficulty_profile=(0, 0),
            physiology_profile=PROFILE,
        )
        self.assertEqual(POLICIES["GREEDY"](view), 8)
        self.assertEqual(POLICIES["EFFICIENT"](view), 4)
        for name in ("AGGRESSIVE", "ADAPTIVE"):
            self.assertIn(POLICIES[name](view), view.payable)


if __name__ == "__main__":
    unittest.main()
