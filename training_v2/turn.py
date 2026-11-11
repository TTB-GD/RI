"""Main Training B turn loop: dice, conserved budgets and session resolution."""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable, Sequence

from decision_engine import energy_and_fatigue
from .budget import TrainingEnergyBudget
from .dice import DiceActionResult, RollResult, roll_initial, resolve_dice_action
from .session_resolution import SessionResolution, resolve_session_plan
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
    sessions: SessionResolution | None = None


def resolve_training_turn(
    state: PlayerState,
    choose_dice_action: Callable[[RollResult], str | tuple[str, int]],
    allocate_budget: Callable[[DiceActionResult], TrainingEnergyBudget],
    *,
    choose_sessions: Callable[[TrainingEnergyBudget], Sequence[str]] | None = None,
    rpe_authorized: int | None = None,
    rng=None,
    overtraining: bool = False,
) -> TrainingTurnResult:
    """Resolve one complete turn when a session-plan callback is supplied.

    The player first allocates energy between EF, Seuil and VMA, then chooses
    dose-specific sessions. Dice fatigue is committed before any bust test.
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

    sessions = None
    if choose_sessions is not None:
        if rpe_authorized is None:
            raise ValueError("rpe_authorized is required when resolving sessions")
        plan = choose_sessions(budget)
        sessions = resolve_session_plan(
            state, budget, plan, rpe_authorized=rpe_authorized, rng=roller,
        )

    return TrainingTurnResult(
        turn=state.turns_played,
        initial_roll=initial,
        dice=dice,
        budget=budget,
        fatigue_before=fatigue_before,
        fatigue_delta=fatigue_delta,
        fatigue_after=state.fatigue,
        dice_pool_after=tuple(state.dice_pool),
        sessions=sessions,
    )
