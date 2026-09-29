import unittest

from physiology import PhysiologyProfile, physiological_cost


class PhysiologyProfileTests(unittest.TestCase):
    def test_profile_requires_strictly_ordered_landmarks(self):
        for values in ((0, 0, 10), (0, 10, 10), (5, 4, 10)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                PhysiologyProfile(*values)

    def test_reference_curve_and_invariants(self):
        profile = PhysiologyProfile(ef=0, threshold=5, vma=10)
        costs = [physiological_cost(profile, load) for load in range(11)]
        self.assertEqual(costs, [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25])
        self.assertEqual(costs[0], 0)
        self.assertTrue(all(cost >= 0 for cost in costs))
        self.assertTrue(all(left < right for left, right in zip(costs, costs[1:])))
        self.assertEqual([b - a for a, b in zip(costs[:5], costs[1:6])], [2] * 5)
        self.assertEqual([b - a for a, b in zip(costs[5:], costs[6:])], [3] * 5)
        self.assertEqual(physiological_cost(profile, 5), 2 * (5 - profile.ef))

    def test_ef_plus_one_reduces_common_domain_by_two(self):
        original = PhysiologyProfile(0, 5, 10)
        shifted = PhysiologyProfile(1, 5, 10)
        for load in range(1, 11):
            self.assertEqual(
                physiological_cost(shifted, load),
                physiological_cost(original, load) - 2,
            )

    def test_threshold_plus_one_changes_only_post_old_threshold_points(self):
        original = PhysiologyProfile(0, 5, 10)
        shifted = PhysiologyProfile(0, 6, 10)
        for load in range(11):
            difference = physiological_cost(shifted, load) - physiological_cost(original, load)
            self.assertEqual(difference, 0 if load <= original.threshold else -1)

    def test_vma_plus_one_preserves_old_domain_and_extends_marginal_cost(self):
        original = PhysiologyProfile(0, 5, 10)
        shifted = PhysiologyProfile(0, 5, 11)
        for load in range(11):
            self.assertEqual(physiological_cost(shifted, load), physiological_cost(original, load))
        self.assertEqual(
            physiological_cost(shifted, 11), physiological_cost(original, 10) + 3
        )

    def test_load_outside_integrated_domain_is_explicit(self):
        profile = PhysiologyProfile(2, 5, 10)
        with self.assertRaisesRegex(ValueError, "greater than or equal to ef"):
            physiological_cost(profile, 1)
        with self.assertRaisesRegex(ValueError, "OPEN"):
            physiological_cost(profile, 11)


if __name__ == "__main__":
    unittest.main()
