"""Main Training B turn loop: dice choice, conserved energy budget, fatigue.

Session-dose resolution is intentionally the next layer: the approved session
matrix (adaptations, RPE, bust tolerance and session fatigue) is still OPEN.
This module therefore completes the player-controlled dice and budget phases
without importing the obsolete direct-dice-to-session resolver.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable

from decision_engine import energy_and_fatigue
from .budget import TrainingEnergyBudget
from .dice import DiceActionResult, RollResult, roll_initial, resolve_dice_action
from .state import PlayerState


@dataclass(frozen=True)
class TrainingTurnResult:
    turn: int
    initial_roll: RollResult
    dice: DiceActionResult
    budget: TrainingEnergyBudget
    fatigue_before: int
    fatigue_delta: int
    fatigue_after: int
    dice_pool_after: tuple[int, ...]


def resolve_training_turn(
    state: PlayerState,
    choose_dice_action: Callable[[RollResult], str | tuple[str, int]],
    allocate_budget: Callable[[DiceActionResult], TrainingEnergyBudget],
    *,
    rng=None,
    overtraining: bool = False,
) -> TrainingTurnResult:
    """Resolve the approved dice and energy-budget phases of one Training turn.

    The fatigue contribution is applied immediately after the dice action,
    before session resolution. A later session bust must not roll it back.
    """
    roller = rng if rng is not None else random.Random()
    initial = roll_initial(state.dice_pool, rng=roller, defer_reserve=True)
    choice = choose_dice_action(initial)
    if isinstance(choice, tuple):
        if len(choice) != 2:
            raise ValueError("dice action tuple must contain action and reroll index")
        action, reroll_index = choice
    else:
        action, reroll_index = choice, None

    dice = resolve_dice_action(
        initial, action, reroll_index=reroll_index, rng=roller,
        overtraining=overtraining,
    )
    budget = allocate_budget(dice)
    if not isinstance(budget, TrainingEnergyBudget):
        raise TypeError("budget allocator must return TrainingEnergyBudget")
    if budget.total_energy != dice.energy:
        raise ValueError("budget total must equal final dice energy")

    _, fatigue_delta = energy_and_fatigue(dice.energy, dice.tn)
    fatigue_before = state.fatigue
    state.fatigue = max(0, fatigue_before + fatigue_delta)
    state.turns_played += 1
    return TrainingTurnResult(
        turn=state.turns_played,
        initial_roll=initial,
        dice=dice,
        budget=budget,
        fatigue_before=fatigue_before,
        fatigue_delta=fatigue_delta,
        fatigue_after=state.fatigue,
        dice_pool_after=tuple(state.dice_pool),
    )
