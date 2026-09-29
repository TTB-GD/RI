import unittest

from physiology import PhysiologyProfile
from race_v2 import resolve_segment


class RaceV2IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.profile = PhysiologyProfile(ef=0, threshold=5, vma=10)

    def test_difficulty_contributes_to_load_and_cost_not_score(self):
        result = resolve_segment(self.profile, production=7, difficulty=2)
        self.assertEqual(result.load, 9)
        self.assertEqual(result.score, 7)
        self.assertEqual(result.cost, 22)

    def test_same_production_without_difficulty_changes_only_load_and_cost(self):
        flat = resolve_segment(self.profile, production=7, difficulty=0)
        difficult = resolve_segment(self.profile, production=7, difficulty=2)
        self.assertEqual(flat.score, difficult.score)
        self.assertEqual(flat.production, difficult.production)
        self.assertEqual(flat.load, 7)
        self.assertEqual(flat.cost, 16)
        self.assertEqual(difficult.cost, 22)

    def test_difficulty_has_no_persistent_state(self):
        first = resolve_segment(self.profile, production=7, difficulty=2)
        second = resolve_segment(self.profile, production=7, difficulty=0)
        self.assertEqual(second, resolve_segment(self.profile, production=7, difficulty=0))
        self.assertNotEqual(first.cost, second.cost)


if __name__ == "__main__":
    unittest.main()
