"""Multi-player, multi-sector Race V2 orchestration prototype.

Dice rolling and reroll interaction are intentionally external: each sector
receives the energy each player has chosen to spend after those decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Mapping

from .sector import RacePhysiologyTable, SectorResolution, resolve_sector


SECTOR_COUNTS = {"5k": 7, "10k": 10, "21k": 13, "42k": 16}
REVEAL_SCHEDULES = {
    "5k": (2, 4, 6),
    "10k": (3, 6, 9),
    "21k": (4, 8, 12),
    "42k": (4, 8, 12),
}
FORM_RECIPES = {
    "exceptionnelle": ("excellent", "excellent", "bon"),
    "excellente": ("excellent", "bon", "bon"),
    "bonne": ("bon", "bon", "moyen"),
    "moyenne": ("bon", "moyen", "mauvais"),
    "difficile": ("moyen", "mauvais", "mauvais"),
}
FORM_DECKS = {
    "excellent": (2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0),
    "bon": (2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, -1, -1, 0),
    "moyen": (1, 1, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, 0),
    "mauvais": (0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -2, -2, -2, -2, -2),
}
FORM_BANDS = (
    (3, 5, "difficile"),
    (6, 8, "moyenne"),
    (9, 12, "bonne"),
    (13, 15, "excellente"),
    (16, 18, "exceptionnelle"),
)


@dataclass(frozen=True)
class RacePlayerConfig:
    player_id: str
    table: RacePhysiologyTable
    specific_pace: int
    initial_credit: int


@dataclass(frozen=True)
class FormCard:
    category: str
    value: int


@dataclass
class PlayerRaceState:
    config: RacePlayerConfig
    form_day_roll: int
    form_level: str
    cards: list[FormCard]
    score: int = 0
    cumulative_form: int = 0
    cumulative_consumption: int = 0
    revealed_card_count: int = 0
    revealed_cards: list[FormCard] = field(default_factory=list)
    sector_results: list[SectorResolution] = field(default_factory=list)
    group_id: int = 0
    is_hare: bool = True
    aspiration_bonus: int = 0


@dataclass(frozen=True)
class PlayerSectorResult:
    player_id: str
    resolution: SectorResolution
    score: int
    revealed_card: FormCard | None
    group_id_next: int
    is_hare_next: bool
    aspiration_bonus_next: int


@dataclass(frozen=True)
class RaceSectorResult:
    sector_number: int
    players: Mapping[str, PlayerSectorResult]
    finished: bool


@dataclass
class RaceState:
    race_type: str
    terrain: tuple[int, ...]
    players: dict[str, PlayerRaceState]
    sector_number: int = 0
    history: list[RaceSectorResult] = field(default_factory=list)
    finished: bool = False
    final_unrevealed_cards: dict[str, tuple[FormCard, ...]] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        race_type: str,
        terrain: tuple[int, ...],
        player_configs: tuple[RacePlayerConfig, ...],
        seed: int,
    ) -> "RaceState":
        if race_type not in SECTOR_COUNTS:
            raise ValueError(f"unsupported race_type: {race_type}")
        sector_count = SECTOR_COUNTS[race_type]
        if len(terrain) != sector_count:
            raise ValueError(f"{race_type} requires exactly {sector_count} terrain values")
        if any(type(value) is not int for value in terrain):
            raise TypeError("terrain values must be integers")
        if not player_configs:
            raise ValueError("at least one player is required")
        ids = [config.player_id for config in player_configs]
        if any(not player_id for player_id in ids) or len(set(ids)) != len(ids):
            raise ValueError("player IDs must be non-empty and unique")

        root_rng = random.Random(seed)
        players: dict[str, PlayerRaceState] = {}
        for config in player_configs:
            if not 0 <= config.initial_credit:
                raise ValueError("initial_credit must be non-negative")
            if not 0 < config.specific_pace <= config.table.vma_energy:
                raise ValueError("specific_pace must be within the physiology table")
            player_rng = random.Random(root_rng.getrandbits(64))
            form_day_roll = sum(player_rng.randint(1, 6) for _ in range(3))
            form_level = next(
                level for low, high, level in FORM_BANDS
                if low <= form_day_roll <= high
            )
            cards = _draw_form_cards(form_level, player_rng)
            players[config.player_id] = PlayerRaceState(
                config=config,
                form_day_roll=form_day_roll,
                form_level=form_level,
                cards=cards,
            )

        state = cls(
            race_type=race_type,
            terrain=terrain,
            players=players,
        )
        _recalculate_groups(state)
        return state

    @property
    def sector_count(self) -> int:
        return SECTOR_COUNTS[self.race_type]

    def play_sector(self, energy_spent: Mapping[str, int]) -> RaceSectorResult:
        if self.finished:
            raise RuntimeError("race is already finished")
        expected_ids = set(self.players)
        if set(energy_spent) != expected_ids:
            missing = expected_ids - set(energy_spent)
            extra = set(energy_spent) - expected_ids
            raise ValueError(f"energy_spent player IDs mismatch; missing={missing}, extra={extra}")
        if any(type(value) is not int or value < 0 for value in energy_spent.values()):
            raise ValueError("all expenditures must be non-negative integers")

        next_sector = self.sector_number + 1
        terrain_difficulty = self.terrain[self.sector_number]
        reveal_at = REVEAL_SCHEDULES[self.race_type]
        player_results: dict[str, PlayerSectorResult] = {}

        # Reveal and apply scheduled form cards before any player resolves this sector.
        revealed_this_sector: dict[str, FormCard | None] = {}
        for player_id, player in self.players.items():
            card = None
            if next_sector in reveal_at:
                card = player.cards[player.revealed_card_count]
                player.revealed_card_count += 1
                player.revealed_cards.append(card)
                player.cumulative_form += card.value
            revealed_this_sector[player_id] = card

        # Every player's group/aspiration status was established after the
        # previous sector; all players therefore resolve from the same snapshot.
        resolutions: dict[str, SectorResolution] = {}
        for player_id, player in self.players.items():
            resolutions[player_id] = resolve_sector(
                table=player.config.table,
                energy_result=energy_spent[player_id],
                group_bonus=player.aspiration_bonus,
                terrain_difficulty=terrain_difficulty,
                specific_pace=player.config.specific_pace,
                initial_credit=player.config.initial_credit,
                cumulative_form=player.cumulative_form,
                cumulative_consumption=player.cumulative_consumption,
            )

        for player_id, player in self.players.items():
            resolution = resolutions[player_id]
            player.score += resolution.speed
            player.cumulative_consumption = resolution.cumulative_consumption_next
            player.sector_results.append(resolution)

        _recalculate_groups(self)
        self.sector_number = next_sector
        self.finished = self.sector_number == self.sector_count

        for player_id, player in self.players.items():
            player_results[player_id] = PlayerSectorResult(
                player_id=player_id,
                resolution=resolutions[player_id],
                score=player.score,
                revealed_card=revealed_this_sector[player_id],
                group_id_next=player.group_id,
                is_hare_next=player.is_hare,
                aspiration_bonus_next=player.aspiration_bonus,
            )

        result = RaceSectorResult(
            sector_number=next_sector,
            players=player_results,
            finished=self.finished,
        )
        self.history.append(result)

        if self.finished:
            # Remaining cards are revealed only after the final sector, for information.
            for player_id, player in self.players.items():
                self.final_unrevealed_cards[player_id] = tuple(
                    player.cards[player.revealed_card_count:]
                )
        return result


def _draw_form_cards(form_level: str, rng: random.Random) -> list[FormCard]:
    categories = list(FORM_RECIPES[form_level])
    rng.shuffle(categories)
    cards: list[FormCard] = []
    for category in categories:
        deck = list(FORM_DECKS[category])
        rng.shuffle(deck)
        cards.append(FormCard(category=category, value=deck.pop()))
    return cards


def _recalculate_groups(state: RaceState) -> None:
    # Stable tie order by player_id makes equal-score grouping reproducible.
    ranked = sorted(state.players.values(), key=lambda p: (-p.score, p.config.player_id))
    groups: list[list[PlayerRaceState]] = []
    for player in ranked:
        if not groups or groups[-1][-1].score - player.score > 1:
            groups.append([player])
        else:
            groups[-1].append(player)

    for group_id, group in enumerate(groups):
        leading_score = group[0].score
        for player in group:
            player.group_id = group_id
            player.is_hare = player.score == leading_score
            player.aspiration_bonus = (
                1 if len(group) > 1 and player.score < leading_score else 0
            )
