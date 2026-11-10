"""Tests for the interactive Training B console."""
import random
import unittest

from training_v2 import PlayerState
from training_v2.console import play_turn, run_session


class TrainingBConsoleTests(unittest.TestCase):
    def test_play_turn_retries_invalid_input_then_resolves_choice(self):
        state = PlayerState()
        answers = iter(("invalid-action", "keep", "not-a-number", "0", "1"))
        output = []
        result = play_turn(
            state, input_fn=lambda _prompt: next(answers),
            output_fn=output.append, rng=random.Random(7),
        )
        self.assertEqual(result.turn, 1)
        self.assertEqual(state.turns_played, 1)
        self.assertTrue(any("Action invalide" in line for line in output))
        self.assertTrue(any("Saisie invalide" in line for line in output))
        self.assertTrue(any("Choix invalide" in line for line in output))
        self.assertTrue(any("Compositions de séances accessibles:" in line for line in output))
        self.assertTrue(any("Profil EF/Seuil/VMA:" in line for line in output))

    def test_session_preserves_state_between_consecutive_turns(self):
        answers = iter(("keep", "1", "", "keep", "1", "q"))
        output = []
        state = run_session(
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append, rng=random.Random(11),
        )
        self.assertEqual(state.turns_played, 2)
        self.assertTrue(any("Tour 1" in line for line in output))
        self.assertTrue(any("Tour 2" in line for line in output))


if __name__ == "__main__":
    unittest.main()
