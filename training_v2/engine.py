"""Deterministic-testable Training B turn using direct session allocations."""
from dataclasses import dataclass
import math
import random

from decision_engine import energy_and_fatigue
from dice_types import make_pool, pool_tn
from session_effects import session_outcome

from .catalog import SESSION_CATALOG, projected_profile
from .programs import SessionAllocation
from .state import PlayerState
from .milestones import validate_portfolio_milestones
from .dice import RollResult, roll_initial, resolve_dice_action
from .portfolio import make_session_eligible


EF_MILESTONES = (10, 20, 35, 50, 70, 100, 120, 150)
EF_DIE_MILESTONES = {35, 100}
Q_MILESTONES = (7, 15, 25, 35, 50, 65, 80, 100)
Q_UPGRADE_MILESTONES = {15, 35, 65, 100}
DIE_SIZES = (6, 8, 10, 12)


@dataclass(frozen=True)
class TurnResult:
    turn: int
    raw_faces: tuple[int, ...]
    final_values: tuple[int, ...]
    tn: float
    allocations: tuple[SessionAllocation, ...]
    successful_sessions: tuple[SessionAllocation, ...]
    busted_session: str | None
    ef_energy: int
    quality_energy: int
    session_costs: tuple[tuple[str, int], ...]
    progression_spec_gained: int
    newly_eligible_sessions: tuple[str, ...]
    fatigue_blackjack: int
    fatigue_excess: int
    fatigue_specific: int
    fatigue_after: int
    dice_pool_after: tuple[int, ...]
    dice_action: str = "keep"


def _apply_milestones(state: PlayerState, old_ef: int, old_q: int) -> None:
    for milestone in EF_MILESTONES:
        if old_ef < milestone <= state.progression_ef:
            if milestone not in state.ef_milestones_claimed:
                state.ef_milestones_claimed.add(milestone)
                if milestone in EF_DIE_MILESTONES:
                    if state.dice_added < 2 and len(state.dice_pool) < 6:
                        state.dice_pool.append(6)
                        state.dice_added += 1
    for milestone in Q_MILESTONES:
        if old_q < milestone <= state.progression_q:
            if milestone in state.q_milestones_claimed:
                continue
            state.q_milestones_claimed.add(milestone)
            if milestone not in Q_UPGRADE_MILESTONES or state.upgrades_used >= 4:
                continue
            eligible = [i for i, size in enumerate(state.dice_pool) if size < 12]
            if eligible:
                index = min(eligible, key=lambda i: (state.dice_pool[i], i))
                current = state.dice_pool[index]
                state.dice_pool[index] = DIE_SIZES[DIE_SIZES.index(current) + 1]
                state.upgrades_used += 1


def _validate_allocations(state, values, allocations):
    allocations = tuple(allocations)
    if not allocations:
        raise ValueError("at least one session must be selected")
    all_indices = [index for item in allocations for index in item.die_indices]
    if sorted(all_indices) != list(range(len(values))):
        raise ValueError("every retained die must be allocated exactly once")
    for item in allocations:
        if item.session_key not in SESSION_CATALOG:
            raise ValueError("unknown session")
        if item.session_key not in state.acquired_session_keys:
            raise ValueError("session is not in the acquired portfolio")
        if not item.die_indices or len(set(item.die_indices)) != len(item.die_indices):
            raise ValueError("each session requires distinct allocated dice")
        if any(index < 0 or index >= len(values) for index in item.die_indices):
            raise ValueError("session allocation index is out of range")
        energy = sum(values[index] for index in item.die_indices)
        option = SESSION_CATALOG[item.session_key]
        if energy != item.energy or energy < option.energy_cost:
            raise ValueError("session allocation does not cover its energy cost")
    counts = {key: sum(item.session_key == key for item in allocations)
              for key in SESSION_CATALOG}
    for key, count in counts.items():
        limit = SESSION_CATALOG[key].max_per_turn
        if limit is not None and count > limit:
            raise ValueError("session exceeds its per-turn occurrence limit")
    return allocations


def resolve_turn(state: PlayerState, raw_faces, allocations, *, risk_faces=(), rng=None, portfolio_milestones=(), final_values_override=None, dice_action="keep"):
    """Resolve one roll and the player's direct allocation of retained dice."""
    portfolio_milestones = validate_portfolio_milestones(portfolio_milestones)
    raw_faces = tuple(raw_faces)
    if len(raw_faces) != len(state.dice_pool):
        raise ValueError("one initial raw face is required for every die in the pool")
    if any(face < 1 or face > size for face, size in zip(raw_faces, state.dice_pool)):
        raise ValueError("raw face is outside its die range")
    if final_values_override is None:
        outcome = session_outcome(raw_faces, raw_faces, len(state.dice_pool))
        values = tuple(outcome["dice_used"])
    else:
        values = tuple(final_values_override)
        if not 1 <= len(values) <= len(state.dice_pool):
            raise ValueError("final dice must be a non-empty subset of the pool")
        if any(value < 1 or value > max(state.dice_pool) for value in values):
            raise ValueError("final die value is outside the pool's die range")
    allocations = _validate_allocations(state, values, allocations)

    session_keys = tuple(item.session_key for item in allocations)
    projected = projected_profile(state.profile, session_keys)
    if not projected["ef"] < projected["threshold"] < projected["vma"]:
        raise ValueError("session adaptations would violate EF < Seuil < VMA")

    tn = pool_tn(make_pool(state.dice_pool))
    costs = tuple(
        (item.session_key, SESSION_CATALOG[item.session_key].energy_cost)
        for item in allocations
    )

    rng = rng if rng is not None else random.Random()
    risk_iter = iter(risk_faces)
    successful, busted = [], None
    fatigue_specific = 0
    for item in allocations:
        option = SESSION_CATALOG[item.session_key]
        if option.rpe > max(values):
            try:
                risk_face = next(risk_iter)
            except StopIteration:
                risk_face = rng.randint(1, max(state.dice_pool))
            if risk_face < 1 or risk_face > max(state.dice_pool):
                raise ValueError("risk face is outside the largest die range")
            if risk_face <= option.rpe - max(values):
                busted = item.session_key
                break
        successful.append(item)
        fatigue_specific += option.fatigue

    # Only completed sessions contribute to realized load and its fatigue.
    ef_energy = sum(
        item.energy for item in successful
        if SESSION_CATALOG[item.session_key].load_type == "EF"
    )
    quality_energy = sum(
        item.energy for item in successful
        if SESSION_CATALOG[item.session_key].load_type == "QUALITY"
    )

    old_ef, old_q = state.progression_ef, state.progression_q
    successful_ef_energy = sum(
        item.energy for item in successful
        if SESSION_CATALOG[item.session_key].load_type == "EF"
    )
    state.progression_ef += successful_ef_energy
    successful_quality_cost = sum(
        SESSION_CATALOG[item.session_key].energy_cost for item in successful
        if SESSION_CATALOG[item.session_key].load_type == "QUALITY"
    )
    state.progression_q += successful_quality_cost
    state.progression_threshold += sum(
        SESSION_CATALOG[item.session_key].energy_cost for item in successful
        if SESSION_CATALOG[item.session_key].family == "SEUIL"
    )
    state.progression_vma += sum(
        SESSION_CATALOG[item.session_key].energy_cost for item in successful
        if SESSION_CATALOG[item.session_key].family == "VMA"
    )

    # Keep the existing experimental Q remainder accounting until SPEC is designed.
    spec_gained = sum(
        item.energy - SESSION_CATALOG[item.session_key].energy_cost
        for item in successful
        if SESSION_CATALOG[item.session_key].load_type == "QUALITY"
    )
    state.progression_spec += spec_gained

    for item in successful:
        for attribute, amount in SESSION_CATALOG[item.session_key].adaptations:
            setattr(state.profile, attribute, getattr(state.profile, attribute) + amount)

    _apply_milestones(state, old_ef, old_q)
    newly_eligible = []
    progression_tracks = {
        "ef": state.progression_ef,
        "threshold": state.progression_threshold,
        "vma": state.progression_vma,
    }
    for milestone in portfolio_milestones:
        if milestone.key in state.portfolio_milestones_claimed:
            continue
        if progression_tracks[milestone.track] < milestone.threshold:
            continue
        state.portfolio_milestones_claimed.add(milestone.key)
        for session_key in milestone.unlock_session_keys:
            if session_key not in state.eligible_session_keys:
                make_session_eligible(state, session_key)
                newly_eligible.append(session_key)
    _, fatigue_blackjack = energy_and_fatigue(sum(values), tn)
    fatigue_excess = math.ceil(max(0, quality_energy - ef_energy) / 2)
    state.fatigue = max(
        0, state.fatigue + fatigue_blackjack + fatigue_excess + fatigue_specific
    )
    state.turns_played += 1
    return TurnResult(
        turn=state.turns_played, raw_faces=raw_faces, final_values=values,
        tn=tn, allocations=allocations,
        successful_sessions=tuple(successful), busted_session=busted,
        ef_energy=ef_energy, quality_energy=quality_energy,
        session_costs=costs, progression_spec_gained=spec_gained,
        newly_eligible_sessions=tuple(sorted(newly_eligible)),
        fatigue_blackjack=fatigue_blackjack, fatigue_excess=fatigue_excess,
        fatigue_specific=fatigue_specific, fatigue_after=state.fatigue,
        dice_pool_after=tuple(state.dice_pool), dice_action=dice_action,
    )


def roll_pool(state: PlayerState, *, rng=None) -> RollResult:
    """Roll all dice once; expose n-1 active dice and the reserve separately."""
    return roll_initial(state.dice_pool, rng=rng)


def roll_and_resolve_turn(
    state: PlayerState,
    choose_program,
    *,
    choose_dice_action=None,
    rng=None,
    risk_faces=(),
    portfolio_milestones=(),
    overtraining=False,
):
    """Resolve initial roll, player dice action, then direct session allocation.

    choose_dice_action returns an action string or (action, reroll_index).
    choose_program receives the resolved dice action. Keep is the default action.
    Overtraining is supplied by the caller because its fatigue threshold remains
    an explicit Training B rules parameter, not an inferred constant.
    """
    rng = rng if rng is not None else random.Random()
    initial_roll = roll_pool(state, rng=rng)
    choice = choose_dice_action(initial_roll) if choose_dice_action else "keep"
    if isinstance(choice, tuple):
        action, reroll_index = choice
    else:
        action, reroll_index = choice, None
    dice = resolve_dice_action(
        initial_roll, action, reroll_index=reroll_index, rng=rng,
        overtraining=overtraining,
    )
    allocations = choose_program(dice)
    return resolve_turn(
        state, initial_roll.raw_faces, allocations, risk_faces=risk_faces, rng=rng,
        portfolio_milestones=portfolio_milestones,
        final_values_override=dice.final_values, dice_action=dice.action,
    )
