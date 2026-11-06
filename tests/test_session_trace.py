"""Tests for occurrence-level session trace attribution in Training turns."""

import unittest
from unittest.mock import patch

from player_state import Player
from simulate_player import _session_occurrence_traces, play_player_turn


class SessionOccurrenceTraceTests(unittest.TestCase):
    def test_trace_queue_preserves_distinct_repeated_session_occurrences(self):
        traces = [
            {"session": "EF1", "marginal_utility": 0.1},
            {"session": "Seuil5", "marginal_utility": 0.2},
            {"session": "EF1", "marginal_utility": 0.3},
        ]
        rows = _session_occurrence_traces(
            ("EF1", "Seuil5", "EF1"), (), traces,
        )
        ef_rows = [row for row in rows if row["session"] == "EF1"]
        self.assertEqual([row["trace"]["marginal_utility"] for row in ef_rows], [0.1, 0.3])
        self.assertEqual([row["trace_index"] for row in ef_rows], [0, 2])
        self.assertTrue(all(row["origin"] == "planned" for row in ef_rows))

    def test_replacement_same_name_is_marked_not_mapped_to_plan_trace(self):
        rows = _session_occurrence_traces(
            ("EF1", "EF1", "EF1"), ("EF1",),
            [
                {"session": "EF1", "marginal_utility": 0.1},
                {"session": "EF1", "marginal_utility": 0.3},
            ],
        )
        self.assertEqual([row["origin"] for row in rows],
                         ["planned", "planned", "redistribution"])
        self.assertEqual([row["trace_index"] for row in rows], [0, 1, None])
        self.assertEqual(rows[2]["trace"], {})

    def test_turn_logs_each_repeated_ef_and_redistribution_separately(self):
        player = Player()
        available = ["EF1", "EF2", "EF3", "EF4", "EF5", "Seuil5", "VMA5"]
        player.progress.available_sessions = lambda: available
        player.progress.tentable_sessions = lambda: available
        roll = {
            "energy_budget": 12, "rpe_max": 4, "quality_sessions_from_roll": 2,
            "tn": 20, "pool_size": 4, "final_values": [1, 1, 1],
            "pattern": "test", "action_chosen": "keep",
        }
        plan = ["EF1", "Seuil5", "EF1", "VMA5"]
        trace = [
            {"session": "EF1", "marginal_utility": 0.1,
             "alternatives_considered": 3, "note": "first EF"},
            {"session": "Seuil5", "marginal_utility": 0.2,
             "alternatives_considered": 2, "note": "quality"},
            {"session": "EF1", "marginal_utility": 0.3,
             "alternatives_considered": 1, "note": "second EF"},
            {"session": "VMA5", "marginal_utility": 0.4,
             "alternatives_considered": 1, "note": "cancelled risk"},
        ]
        with patch("simulate_player.roll_turn_budget", return_value=roll), patch(
            "simulate_player.choose_sessions_weighted", return_value=(plan, trace)
        ):
            _, session_rows = play_player_turn(1, player, bust_index=1)

        self.assertEqual([row["session"] for row in session_rows], ["EF1", "EF1", "EF4"])
        self.assertEqual([row["marginal_utility"] for row in session_rows], [0.1, 0.3, None])
        self.assertEqual([row["origin"] for row in session_rows],
                         ["planned", "planned", "redistribution"])
        self.assertEqual([row["occurrence_index"] for row in session_rows], [1, 2, 3])
        self.assertEqual([row["note"] for row in session_rows],
                         ["first EF", "second EF", "redistribution_EF"])
        self.assertIsNone(session_rows[2]["trace_index"])


if __name__ == "__main__":
    unittest.main()
