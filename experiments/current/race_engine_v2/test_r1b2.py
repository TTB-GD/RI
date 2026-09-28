import unittest

from experiments.current.race_engine_v2.core import physiological_load, production_cost, run_race
from experiments.current.race_engine_v2.energy import energy_cost
from experiments.current.race_engine_v2.fixtures import POOLS
from experiments.current.race_engine_v2.policies import POLICIES
from experiments.current.race_engine_v2.run_r1b2 import (FLAT, MAGNITUDE_PROFILES,
    REPRESENTATIVE_PROFILES, frequency_profiles, paired_metrics)


class R1B2CalibrationTests(unittest.TestCase):
    def test_magnitudes_change_only_load_and_cost(self):
        for difficulty in range(1, 5):
            self.assertEqual(physiological_load(21, difficulty), 21 + difficulty)
            self.assertEqual(production_cost(21, difficulty, "B"), energy_cost(21 + difficulty, "B"))

    def test_exact_profiles_and_frequency(self):
        self.assertEqual(MAGNITUDE_PROFILES["M4"], (0, 0, 0, 4, 4, 0, 0, 0, 0))
        profiles = frequency_profiles((2, 3))
        self.assertEqual(profiles["D2_F3"], (0, 2, 0, 0, 2, 0, 0, 2, 0))
        self.assertEqual(sum(value > 0 for value in profiles["D3_F4"]), 4)
        self.assertEqual(REPRESENTATIVE_PROFILES["P1"], (0, 1, 0, 1, 0, 1, 0, 1, 0))

    def test_flat_and_terrain_pairing_keep_rolls_and_form(self):
        kwargs = dict(seed=31, pool=POOLS["6d6"], race_length=9, curve="B",
            policy=POLICIES["ADAPTIVE"], ctl=100, freshness_bonus=0,
            long_run_preparation=False, form_mode="PATTERN")
        flat = run_race(**kwargs, difficulty_profile=FLAT)
        terrain = run_race(**kwargs, difficulty_profile=MAGNITUDE_PROFILES["M3"])
        self.assertEqual(flat["rolls"], terrain["rolls"])
        self.assertEqual(flat["signals"], terrain["signals"])
        self.assertEqual(flat["final_reserve"], terrain["final_reserve"])

    def test_score_is_only_production_and_no_terrain_memory_field(self):
        course = run_race(seed=5, pool=POOLS["4d8+1d6"], race_length=9, curve="B",
            policy=POLICIES["AGGRESSIVE"], ctl=100, freshness_bonus=0,
            long_run_preparation=False, form_mode="PATTERN",
            difficulty_profile=REPRESENTATIVE_PROFILES["P1"])
        self.assertEqual(course["score"], sum(turn["choice"] for turn in course["turns"]))
        self.assertNotIn("cumulative_difficulty", course)
        self.assertTrue(all("cumulative_difficulty" not in turn for turn in course["turns"]))

    def test_pairing_uses_strict_deltas_and_post_difficulty_state(self):
        kwargs = dict(seed=8, pool=POOLS["6d6"], race_length=9, curve="B",
            policy=POLICIES["EFFICIENT"], ctl=100, freshness_bonus=0,
            long_run_preparation=False, form_mode="PATTERN")
        flat = run_race(**kwargs, difficulty_profile=FLAT)
        profile = MAGNITUDE_PROFILES["M2"]
        terrain = run_race(**kwargs, difficulty_profile=profile)
        paired = paired_metrics(flat, terrain, profile)
        self.assertEqual(len(paired["deltas"]), 2)
        self.assertEqual(len(paired["post_p"]), 1)
        self.assertEqual(len(paired["post_r"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
