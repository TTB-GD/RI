import unittest

from physiology import PhysiologyProfile, physiological_cost


class PhysiologyProfileTests(unittest.TestCase):
    def test_profile_requires_strictly_ordered_landmarks(self):
        for values in ((0, 0, 10), (0, 10, 10), (5, 4, 10)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                PhysiologyProfile(*values)

    def test_reference_curve_and_invariants(self):
        profile = PhysiologyProfile(ef=3, threshold=6, vma=10)
        costs = [physiological_cost(profile, load) for load in range(11)]
        self.assertEqual(costs, [3, 3, 3, 3, 5, 7, 9, 12, 15, 18, 21])
        self.assertEqual(costs[profile.ef], profile.ef)
        self.assertTrue(all(cost >= 0 for cost in costs))
        self.assertEqual([b - a for a, b in zip(costs[:3], costs[1:4])], [0] * 3)
        self.assertEqual([b - a for a, b in zip(costs[3:6], costs[4:7])], [2] * 3)
        self.assertEqual([b - a for a, b in zip(costs[6:], costs[7:])], [3] * 4)
        self.assertEqual(physiological_cost(profile, 6), 9)

    def test_ef_plus_one_reduces_common_domain_by_two(self):
        original = PhysiologyProfile(0, 5, 10)
        shifted = PhysiologyProfile(1, 5, 10)
        for load in range(1, 11):
            self.assertEqual(
                physiological_cost(shifted, load) - physiological_cost(original, load),
                -1,
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
        self.assertEqual(physiological_cost(profile, 1), 2)
        with self.assertRaisesRegex(ValueError, "above vma"):
            physiological_cost(profile, 11)


if __name__ == "__main__":
    unittest.main()
