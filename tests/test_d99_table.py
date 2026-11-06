"""Exhaustive table tests for CURRENT D99 rows; 3-die policy is separate."""

import unittest

from session_effects import SESSION_EFFECTS, session_outcome


# Explicit fixtures from the current design table (4–6 dice), independent of
# SESSION_EFFECTS so changes, missing rows, and added rows are detected.
CURRENT_EXPECTED = {
    4: {
        (1, 1, 1, 1): (1, False),
        (2, 1, 1): (2, False),
        (3, 1): (2, True),
        (2, 2): (2, True),
        (4,): (3, True),
    },
    5: {
        (1, 1, 1, 1, 1): (1, False),
        (2, 1, 1, 1): (2, False),
        (2, 2, 1): (2, True),
        (3, 1, 1): (2, True),
        (3, 2): (3, True),
        (4, 1): (3, True),
        (5,): (3, True),
    },
    6: {
        (1, 1, 1, 1, 1, 1): (1, False),
        (2, 1, 1, 1, 1): (2, False),
        (2, 2, 1, 1): (2, True),
        (3, 1, 1, 1): (2, True),
        (3, 2, 1): (3, True),
        (2, 2, 2): (3, True),
        (4, 1, 1): (3, True),
        (4, 2): (3, True),
        (3, 3): (3, True),
        (5, 1): (3, True),
        (6,): (3, True),
    },
}

# Three-die rows are an open implementation policy, not design-validated.
THREE_DIE_IMPLEMENTATION_POLICY = {
    (1, 1, 1): (1, False),
    (2, 1): (2, False),
    (3,): (2, False),
}


def faces_for(signature):
    """Construct faces with exactly the requested multiplicity signature."""
    return [face for face, count in enumerate(signature, start=1) for _ in range(count)]


class D99TableTests(unittest.TestCase):
    def assert_table_rows(self, dice_count, rows):
        for signature, expected in rows.items():
            with self.subTest(dice_count=dice_count, signature=signature):
                faces = faces_for(signature)
                result = session_outcome(faces, faces, max_dice=dice_count)
                self.assertEqual((result["sessions"], result["bonus_pool"]), expected)

    def test_current_d99_tables_have_exactly_the_expected_rows(self):
        for dice_count, expected_rows in CURRENT_EXPECTED.items():
            with self.subTest(dice_count=dice_count):
                self.assertEqual(SESSION_EFFECTS[dice_count], expected_rows)
                self.assert_table_rows(dice_count, expected_rows)

    def test_three_die_open_implementation_policy_is_separately_characterized(self):
        self.assertEqual(SESSION_EFFECTS[3], THREE_DIE_IMPLEMENTATION_POLICY)
        self.assert_table_rows(3, THREE_DIE_IMPLEMENTATION_POLICY)


if __name__ == "__main__":
    unittest.main()
