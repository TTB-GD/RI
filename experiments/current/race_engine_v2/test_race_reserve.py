import unittest
from training_v2 import PlayerState, TrainingEnergyBudget
from training_v2.turn import resolve_training_turn
from .race_reserve import FreshnessRule, RaceReserveProfile, preview_race_reserve, RACE_SEGMENT_COUNTS

class FixedRng:
    def __init__(self, values): self.values = iter(values)
    def randint(self, low, high):
        value = next(self.values)
        if not low <= value <= high: raise AssertionError("face outside die range")
        return value

class RaceReserveTests(unittest.TestCase):
    def profile(self, **kwargs):
        values = dict(name="10 km", segments=10, target_ef=20, target_threshold=40,
            target_vma=20, reserve_scale=1.0,
            freshness=FreshnessRule(6, 0.5, 3, 0.75))
        values.update(kwargs)
        return RaceReserveProfile(**values)

    def test_course_segment_counts(self):
        self.assertEqual(RACE_SEGMENT_COUNTS, {"5 km": 7, "10 km": 10, "half-marathon": 13, "marathon": 16})

    def test_energy_counts_even_when_first_session_busts(self):
        state = PlayerState()
        result = resolve_training_turn(
            state, choose_dice_action=lambda roll: "keep",
            allocate_budget=lambda dice: TrainingEnergyBudget(dice.energy, 4, 8, dice.energy - 12),
            choose_sessions=lambda budget: ["SEUIL5"], rpe_authorized=0,
            rng=FixedRng((6, 6, 6, 1)))
        self.assertEqual(result.sessions.busted_session, "SEUIL5")
        self.assertEqual((state.training_energy_ef, state.training_energy_threshold, state.training_energy_vma), (4, 8, 6))
        self.assertEqual(state.progression_threshold, 0)
        self.assertEqual(state.fatigue, 13)

    def test_saturation_and_preview(self):
        state = PlayerState(turns_played=10, training_energy_ef=30,
            training_energy_threshold=25, training_energy_vma=40, fatigue=4)
        result = preview_race_reserve(state, self.profile())
        self.assertEqual((result.credited_ef, result.credited_threshold, result.credited_vma), (20, 25, 20))
        self.assertEqual((result.saturated_ef, result.saturated_threshold, result.saturated_vma), (10, 0, 20))
        self.assertAlmostEqual(result.preparation_ratio, 65 / 80)
        self.assertEqual((result.preparation_reserve, result.freshness_bonus, result.total_reserve), (65, 1, 66))
        self.assertEqual(result, preview_race_reserve(state, self.profile()))

    def test_freshness_requires_minimum_preparation(self):
        state = PlayerState(turns_played=8, fatigue=0, training_energy_ef=10)
        self.assertEqual(preview_race_reserve(state, self.profile()).freshness_bonus, 0)

    def test_no_training_gives_no_reserve_or_freshness(self):
        result = preview_race_reserve(PlayerState(fatigue=0), self.profile())
        self.assertEqual((result.preparation_reserve, result.freshness_bonus, result.total_reserve), (0, 0, 0))

    def test_freshness_bonus_is_capped(self):
        state = PlayerState(turns_played=8, training_energy_ef=20,
            training_energy_threshold=40, training_energy_vma=20, fatigue=0)
        self.assertEqual(preview_race_reserve(state, self.profile()).freshness_bonus, 3)

    def test_clone_preserves_independent_energy_counters(self):
        state = PlayerState(training_energy_ef=4, training_energy_threshold=5, training_energy_vma=6)
        clone = state.clone()
        self.assertEqual((clone.training_energy_ef, clone.training_energy_threshold, clone.training_energy_vma), (4, 5, 6))
        clone.training_energy_ef += 1
        self.assertEqual(state.training_energy_ef, 4)

if __name__ == "__main__": unittest.main()
