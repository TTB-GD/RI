import unittest

from .race import (
    FORM_BANDS,
    FORM_DECKS,
    FORM_RECIPES,
    REVEAL_SCHEDULES,
    RacePlayerConfig,
    RaceState,
)
from .sector import RacePhysiologyTable


TABLE = RacePhysiologyTable(
    speeds=(5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
    ef_energy=1,
    threshold_energy=6,
    vma_energy=12,
)


def config(player_id):
    return RacePlayerConfig(
        player_id=player_id,
        table=TABLE,
        specific_pace=7,
        initial_credit=3,
    )


class RaceConfigurationTests(unittest.TestCase):
    def test_distance_sector_counts_and_reveal_schedules(self):
        self.assertEqual(
            {key: len(value) for key, value in REVEAL_SCHEDULES.items()},
            {"5k": 3, "10k": 3, "21k": 3, "42k": 3},
        )
        self.assertEqual(FORM_BANDS[0], (3, 5, "difficile"))
        self.assertEqual(FORM_BANDS[-1], (16, 18, "exceptionnelle"))

    def test_form_deck_counts_match_design(self):
        self.assertEqual(len(FORM_RECIPES), 5)
        self.assertEqual(
            {category: len(cards) for category, cards in FORM_DECKS.items()},
            {"excellent": 15, "bon": 15, "moyen": 15, "mauvais": 15},
        )
        self.assertEqual(
            {category: sum(cards) for category, cards in FORM_DECKS.items()},
            {"excellent": 14, "bon": 7, "moyen": -3, "mauvais": -17},
        )


class RaceStateTests(unittest.TestCase):
    def make_race(self, race_type="5k", configs=None, terrain=None):
        count = {"5k": 7, "10k": 10, "21k": 13, "42k": 16}[race_type]
        return RaceState.create(
            race_type=race_type,
            terrain=terrain or (0,) * count,
            player_configs=tuple(configs or (config("A"), config("B"), config("C"))),
            seed=1234,
        )

    def test_initial_group_has_only_co_hares_and_no_aspiration(self):
        race = self.make_race()
        self.assertEqual({p.group_id for p in race.players.values()}, {0})
        self.assertTrue(all(p.is_hare for p in race.players.values()))
        self.assertTrue(all(p.aspiration_bonus == 0 for p in race.players.values()))

    def test_grouping_uses_successive_gaps_and_local_hare(self):
        race = self.make_race(configs=(config("A"), config("B"), config("C")))
        race.players["A"].score = 10
        race.players["B"].score = 8
        race.players["C"].score = 7
        from .race import _recalculate_groups
        _recalculate_groups(race)
        self.assertEqual(race.players["A"].aspiration_bonus, 0)
        self.assertEqual(race.players["B"].aspiration_bonus, 0)
        self.assertEqual(race.players["C"].aspiration_bonus, 1)
        self.assertEqual(race.players["B"].group_id, race.players["C"].group_id)

    def test_10_9_7_creates_first_group_and_singleton(self):
        race = self.make_race()
        race.players["A"].score = 10
        race.players["B"].score = 9
        race.players["C"].score = 7
        from .race import _recalculate_groups
        _recalculate_groups(race)
        self.assertEqual(race.players["A"].aspiration_bonus, 0)
        self.assertEqual(race.players["B"].aspiration_bonus, 1)
        self.assertEqual(race.players["C"].aspiration_bonus, 0)

    def test_card_is_revealed_before_sector_conversion(self):
        race = self.make_race()
        player = race.players["A"]
        # Force a known card into the first scheduled reveal slot.
        player.cards[0] = type(player.cards[0])(category="excellent", value=2)
        player.revealed_card_count = 0
        for _ in range(7):
            result = race.play_sector({"A": 8, "B": 8, "C": 8})
        self.assertTrue(result.finished)
        self.assertEqual(player.cumulative_form, sum(c.value for c in player.revealed_cards))
        self.assertEqual(len(player.revealed_cards), 3)
        self.assertEqual(len(race.final_unrevealed_cards["A"]), 0)

    def test_card_values_do_not_apply_before_scheduled_sector(self):
        race = self.make_race()
        player = race.players["A"]
        initial_form = player.cumulative_form
        race.play_sector({"A": 7, "B": 7, "C": 7})
        self.assertEqual(player.cumulative_form, initial_form)
        race.play_sector({"A": 7, "B": 7, "C": 7})
        self.assertEqual(player.revealed_card_count, 1)

    def test_scores_are_sum_of_integer_sector_speeds(self):
        race = self.make_race(configs=(config("A"), config("B")))
        result = race.play_sector({"A": 7, "B": 8})
        self.assertEqual(race.players["A"].score, result.players["A"].resolution.speed)
        self.assertEqual(race.players["B"].score, result.players["B"].resolution.speed)

    def test_sector_count_and_final_card_reveal(self):
        race = self.make_race("10k", configs=(config("A"),))
        for _ in range(10):
            result = race.play_sector({"A": 7})
        self.assertTrue(result.finished)
        self.assertEqual(race.sector_number, 10)
        self.assertEqual(len(race.final_unrevealed_cards["A"]), 0)

    def test_invalid_energy_map_does_not_advance_race(self):
        race = self.make_race()
        with self.assertRaises(ValueError):
            race.play_sector({"A": 7})
        self.assertEqual(race.sector_number, 0)
        self.assertEqual(race.history, [])

    def test_cumulative_group_bonus_applies_next_sector(self):
        race = self.make_race(configs=(config("A"), config("B")))
        # Sector 1: B falls one point behind A, forming a group with aspiration.
        race.play_sector({"A": 8, "B": 7})
        self.assertEqual(race.players["B"].aspiration_bonus, 1)
        # Sector 2: B receives +1 conversion energy; expenditure remains 7.
        result = race.play_sector({"A": 7, "B": 7})
        self.assertEqual(result.players["B"].resolution.energy_spent, 7)
        self.assertEqual(result.players["B"].resolution.conversion_energy, 8)

    def test_deterministic_seed_reproduces_cards_and_form_day(self):
        a = self.make_race()
        b = self.make_race()
        for player_id in a.players:
            self.assertEqual(a.players[player_id].form_day_roll, b.players[player_id].form_day_roll)
            self.assertEqual(a.players[player_id].cards, b.players[player_id].cards)


if __name__ == "__main__":
    unittest.main()
