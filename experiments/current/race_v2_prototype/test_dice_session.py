import unittest

from .dice_session import PlayerDiceChoice, RaceDiceSession
from .race import RacePlayerConfig, RaceState
from .sector import RacePhysiologyTable


TABLE = RacePhysiologyTable(
    speeds=(5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
    ef_energy=1,
    threshold_energy=6,
    vma_energy=12,
)


def config(player_id, sizes=(6, 8, 10), tier=4):
    return RacePlayerConfig(
        player_id=player_id,
        table=TABLE,
        specific_pace=7,
        initial_credit=3,
        dice_sizes=sizes,
        affutage_level=tier,
    )


class RaceDiceSessionTests(unittest.TestCase):
    def make_session(self):
        race = RaceState.create(
            race_type="5k",
            terrain=(0,) * 7,
            player_configs=(config("A"), config("B", sizes=(6, 6), tier=2)),
            seed=123,
        )
        return race, RaceDiceSession.create(race, seed=456)

    def test_prepare_reveals_cards_before_exposing_dice(self):
        race, session = self.make_session()
        prepared = session.prepare_sector()
        self.assertEqual(prepared.sector_number, 1)
        self.assertEqual(prepared.revealed_cards, {"A": None, "B": None})
        self.assertEqual(set(prepared.rolled_faces), {"A", "B"})
        self.assertEqual(len(prepared.rolled_faces["A"]), 3)
        self.assertEqual(race._prepared_reveal_sector, 1)

    def test_scheduled_card_is_visible_before_player_choice(self):
        race, session = self.make_session()
        for _ in range(1):
            prepared = session.prepare_sector()
            session.resolve_sector({
                "A": PlayerDiceChoice(selected_indices=()),
                "B": PlayerDiceChoice(selected_indices=()),
            })
        prepared = session.prepare_sector()
        self.assertIsNotNone(prepared.revealed_cards["A"])
        self.assertEqual(race.players["A"].cumulative_form, prepared.revealed_cards["A"].value)

    def test_selected_subset_energy_flows_into_race_resolution(self):
        race, session = self.make_session()
        prepared = session.prepare_sector()
        # Spend the entire pool; the resulting energy is passed to sector resolver.
        choices = {
            player_id: PlayerDiceChoice(selected_indices=tuple(range(len(faces))))
            for player_id, faces in prepared.rolled_faces.items()
        }
        resolved = session.resolve_sector(choices)
        for player_id, dice_result in resolved.dice_results.items():
            self.assertEqual(
                resolved.race_result.players[player_id].resolution.energy_spent,
                min(dice_result.energy_spent, TABLE.vma_energy),
            )

    def test_global_capital_decreases_and_does_not_regenerate(self):
        _, session = self.make_session()
        initial = dict(session.rerolls_remaining)
        prepared = session.prepare_sector()
        choices = {
            player_id: PlayerDiceChoice(
                reroll_indices=(0,),
                selected_indices=(),
            )
            for player_id in prepared.rolled_faces
        }
        session.resolve_sector(choices)
        self.assertEqual(session.rerolls_remaining["A"], initial["A"] - 1)
        self.assertEqual(session.rerolls_remaining["B"], initial["B"] - 1)

    def test_invalid_choice_does_not_resolve_or_consume_budget(self):
        race, session = self.make_session()
        prepared = session.prepare_sector()
        initial_budget = dict(session.rerolls_remaining)
        with self.assertRaises(ValueError):
            session.resolve_sector({
                "A": PlayerDiceChoice(reroll_indices=(0, 1, 2, 3), selected_indices=()),
                "B": PlayerDiceChoice(selected_indices=()),
            })
        self.assertEqual(race.sector_number, 0)
        self.assertEqual(session.rerolls_remaining, initial_budget)
        self.assertIsNotNone(session._prepared)

    def test_empty_selection_scores_zero_and_consumes_no_sustainability(self):
        race, session = self.make_session()
        prepared = session.prepare_sector()
        result = session.resolve_sector({
            "A": PlayerDiceChoice(selected_indices=()),
            "B": PlayerDiceChoice(selected_indices=()),
        })
        for player_id in race.players:
            resolution = result.race_result.players[player_id].resolution
            self.assertEqual(resolution.energy_spent, 0)
            self.assertEqual(resolution.speed, 0)
            self.assertEqual(resolution.sustainability_consumption, 0)

    def test_cannot_prepare_twice_or_resolve_without_preparation(self):
        _, session = self.make_session()
        with self.assertRaises(RuntimeError):
            session.resolve_sector({})
        session.prepare_sector()
        with self.assertRaises(RuntimeError):
            session.prepare_sector()


if __name__ == "__main__":
    unittest.main()
