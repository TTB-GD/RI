"""Two-phase dice interaction adapter for the Race V2 race state.

Order: reveal scheduled form cards -> roll every die -> player rerolls ->
player selects a subset -> resolve the sector. Reroll capital is global for
the race and tracked independently for each player.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Mapping, Sequence

from .dice import (
    DiceDecisionResult,
    reroll_capital,
    resolve_dice_decision,
    roll_dice_pool,
)
from .race import RaceSectorResult, RaceState


@dataclass(frozen=True)
class PlayerDiceChoice:
    reroll_indices: tuple[int, ...] = ()
    selected_indices: tuple[int, ...] = ()


@dataclass(frozen=True)
class PreparedDiceSector:
    sector_number: int
    revealed_cards: Mapping[str, object]
    rolled_faces: Mapping[str, tuple[int, ...]]
    rerolls_remaining: Mapping[str, int]


@dataclass(frozen=True)
class ResolvedDiceSector:
    race_result: RaceSectorResult
    dice_results: Mapping[str, DiceDecisionResult]


@dataclass
class RaceDiceSession:
    """Stateful bridge from Training dice pools to RaceState sector resolution."""

    race: RaceState
    rngs: dict[str, random.Random]
    rerolls_remaining: dict[str, int]
    _prepared: PreparedDiceSector | None = None

    @classmethod
    def create(cls, race: RaceState, *, seed: int) -> "RaceDiceSession":
        if type(seed) is not int:
            raise TypeError("seed must be an integer")
        root_rng = random.Random(seed)
        rngs: dict[str, random.Random] = {}
        remaining: dict[str, int] = {}
        for player_id, player in race.players.items():
            rngs[player_id] = random.Random(root_rng.getrandbits(64))
            remaining[player_id] = reroll_capital(
                dice_sizes=player.config.dice_sizes,
                sector_count=race.sector_count,
                affutage_level=player.config.affutage_level,
            )
        return cls(race=race, rngs=rngs, rerolls_remaining=remaining)

    def prepare_sector(self) -> PreparedDiceSector:
        """Reveal cards first, then roll every die for every player."""
        if self._prepared is not None:
            raise RuntimeError("the current sector already has prepared dice")
        if self.race.finished:
            raise RuntimeError("race is already finished")

        revealed = self.race.reveal_sector_cards()
        faces = {
            player_id: roll_dice_pool(player.config.dice_sizes, self.rngs[player_id])
            for player_id, player in self.race.players.items()
        }
        prepared = PreparedDiceSector(
            sector_number=self.race.sector_number + 1,
            revealed_cards=dict(revealed),
            rolled_faces=faces,
            rerolls_remaining=dict(self.rerolls_remaining),
        )
        self._prepared = prepared
        return prepared

    def resolve_sector(
        self, choices: Mapping[str, PlayerDiceChoice]
    ) -> ResolvedDiceSector:
        """Apply all player choices atomically, then resolve the race sector."""
        if self._prepared is None:
            raise RuntimeError("prepare_sector must be called before resolve_sector")
        expected = set(self.race.players)
        if set(choices) != expected:
            missing, extra = expected - set(choices), set(choices) - expected
            raise ValueError(f"choice player IDs mismatch; missing={missing}, extra={extra}")

        # Work on cloned RNGs so one invalid player's choice cannot partially
        # consume another player's random stream or reroll capital.
        trial_rngs: dict[str, random.Random] = {}
        dice_results: dict[str, DiceDecisionResult] = {}
        for player_id, player in self.race.players.items():
            choice = choices[player_id]
            if not isinstance(choice, PlayerDiceChoice):
                raise TypeError("each choice must be a PlayerDiceChoice")
            trial_rng = random.Random()
            trial_rng.setstate(self.rngs[player_id].getstate())
            trial_rngs[player_id] = trial_rng
            dice_results[player_id] = resolve_dice_decision(
                dice_sizes=player.config.dice_sizes,
                initial_faces=self._prepared.rolled_faces[player_id],
                reroll_indices=choice.reroll_indices,
                selected_indices=choice.selected_indices,
                rerolls_remaining=self.rerolls_remaining[player_id],
                rng=trial_rng,
            )

        expenditures = {
            player_id: result.energy_spent
            for player_id, result in dice_results.items()
        }
        race_result = self.race.play_sector(expenditures)

        for player_id, result in dice_results.items():
            self.rngs[player_id].setstate(trial_rngs[player_id].getstate())
            self.rerolls_remaining[player_id] = result.rerolls_remaining
        self._prepared = None
        return ResolvedDiceSector(race_result=race_result, dice_results=dice_results)
