import unittest

from experiments.current.race_engine_v2.core import (PolicyView, physiological_load,
    production_cost, run_race)
from experiments.current.race_engine_v2.energy import energy_cost
from experiments.current.race_engine_v2.fixtures import DIFFICULTY_PROFILES, POOLS
from experiments.current.race_engine_v2.policies import POLICIES


class TerrainRuleTests(unittest.TestCase):
    def test_load_cost_and_score_boundary(self):
        self.assertEqual(physiological_load(21, 0), 21)
        self.assertEqual(physiological_load(21, 3), 24)
        self.assertEqual(production_cost(21, 0, "B"), energy_cost(21, "B"))
        self.assertEqual(production_cost(21, 3, "B"), energy_cost(24, "B"))
        self.assertGreater(production_cost(21, 3, "B"), production_cost(21, 0, "B"))

    def test_score_excludes_difficulty_and_reserve_only_loses_cost(self):
        course = run_race(seed=3, pool=POOLS["6d6"], race_length=6, curve="B",
            policy=POLICIES["EFFICIENT"], ctl=100, freshness_bonus=0,
            long_run_preparation=False, form_mode="PATTERN",
            difficulty_profile=DIFFICULTY_PROFILES[6]["D1_EARLY"], profile_name="D1_EARLY")
        self.assertEqual(course["score"], sum(turn["choice"] for turn in course["turns"]))
        self.assertEqual(course["spent"], sum(turn["cost"] for turn in course["turns"]))
        self.assertEqual(course["final_reserve"], course["base_reserve"] + course["form_adjustment"])

    def test_flat_profile_is_exact_baseline(self):
        kwargs = dict(seed=17, pool=POOLS["4d8+1d6"], race_length=6, curve="B",
            policy=POLICIES["ADAPTIVE"], ctl=100, freshness_bonus=0,
            long_run_preparation=False, form_mode="PATTERN")
        baseline = run_race(**kwargs)
        flat = run_race(**kwargs, difficulty_profile=DIFFICULTY_PROFILES[6]["D0_FLAT"])
        for field in ("rolls", "signals", "form_adjustment", "final_reserve", "spent",
                      "score", "dnf", "dnf_turn", "reserve_floor_clamped"):
            self.assertEqual(flat[field], baseline[field])
        self.assertEqual([turn["choice"] for turn in flat["turns"]],
                         [turn["choice"] for turn in baseline["turns"]])

    def test_policy_view_receives_public_profile(self):
        seen = []
        def spy(view):
            seen.append(view)
            return min(view.payable)
        profile = DIFFICULTY_PROFILES[6]["D1_EARLY"]
        run_race(seed=1, pool=POOLS["6d6"], race_length=6, curve="B", policy=spy,
            ctl=100, freshness_bonus=0, long_run_preparation=False,
            form_mode="PATTERN", difficulty_profile=profile)
        self.assertEqual(seen[1].current_difficulty, 3)
        self.assertEqual(seen[0].remaining_difficulty_profile, profile[1:])

    def test_policy_does_not_change_rolls_and_form_pattern_is_unchanged(self):
        profile = DIFFICULTY_PROFILES[9]["D3_ROLLING"]
        courses = [run_race(seed=22, pool=POOLS["2d10+4d6"], race_length=9, curve="B",
            policy=policy, ctl=100, freshness_bonus=0, long_run_preparation=False,
            form_mode="PATTERN", difficulty_profile=profile) for policy in POLICIES.values()]
        self.assertEqual(len({course["rolls"] for course in courses}), 1)
        self.assertEqual(len({course["signals"] for course in courses}), 1)

    def test_dnf_has_no_new_condition(self):
        profile = DIFFICULTY_PROFILES[6]["D2_LATE"]
        course = run_race(seed=0, pool=POOLS["2d10+4d6"], race_length=6, curve="B",
            policy=POLICIES["GREEDY"], ctl=0, freshness_bonus=0,
            long_run_preparation=False, form_mode="PATTERN", difficulty_profile=profile)
        self.assertTrue(course["dnf"])
        self.assertEqual(course["dnf_turn"], len(course["turns"]) + 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
