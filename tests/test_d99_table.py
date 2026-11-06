"""Exhaustive table tests for CURRENT D99 rows; 3-die policy is separate."""

import unittest

from session_effects import SESSION_EFFECTS, session_outcome


# Expected CURRENT rows, transcribed as explicit fixtures so missing, changed,
# or extra table entries are caught independently of SESSION_EFFECTS.
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


# OPEN / IMPLEMENTATION POLICY only; not a design-validated CURRENT table.
THREE_DIE_IMPLEMENTATION_POLICY = {
    (1, 1, 1): (1, False),
    (2, 1): (2, False),
    (3,): (2, False),
}


def faces_for(signature):
    return [face for face, count in enumerate(signature, start=1) for _ in range(count)]


class CurrentD99TableTests(unittest.TestCase):
    def test_every_current_row_matches_expected_and_runtime_behavior(self):
        self.assertEqual({n: SESSION_EFFECTS[n] for n in CURRENT_EXPECTED}, CURRENT_EXPECTED)
        for dice_count, rows in CURRENT_EXPECTED.items():
            for signature, expected in rows.items():
                with self.subTest(dice_count=dice_count, signature=signature):
                    result = session_outcome(
                        faces_for(signature), faces_for(signature), max_dice=dice_count,
                    )
                    self.assertEqual((result["sessions"], result["bonus_pool"]), expected)

    def test_three_die_implementation_policy_is_separately_characterized(self):
        self.assertEqual(SESSION_EFFECTS[3], THREE_DIE_IMPLEMENTATION_POLICY)
        for signature, expected in THREE_DIE_IMPLEMENTATION_POLICY.items():
            with self.subTest(signature=signature):
                result = session_outcome(faces_for(signature), faces_for(signature), max_dice=3)
                self.assertEqual((result["sessions"], result["bonus_pool"]), expected)


if __name__ == "__main__":
    unittest.main()
