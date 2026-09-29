import unittest

from physiology import PhysiologyProfile
from race_v2 import is_production_physiologically_legal, resolve_segment


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

    def test_legality_is_a_load_boundary_not_a_production_cap(self):
        profile = PhysiologyProfile(3, 6, 10)
        self.assertTrue(is_production_physiologically_legal(profile, 1, 0))
        self.assertEqual(resolve_segment(profile, 1, 0).cost, 3)
        self.assertTrue(is_production_physiologically_legal(profile, 8, 2))
        self.assertFalse(is_production_physiologically_legal(profile, 9, 2))
        with self.assertRaisesRegex(ValueError, "above vma"):
            resolve_segment(profile, 9, 2)


if __name__ == "__main__":
    unittest.main()
