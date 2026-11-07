"""One complete, deterministic-testable Training B turn.

This is an experimental vertical slice on the selected replacement path for
historical Training CURRENT.
The player chooses a physical dice partition and a quality programme. The
engine validates the allocation, resolves quality risk, applies progression,
and persists the resulting player state.
"""
from dataclasses import dataclass
import math
import random

from decision_engine import energy_and_fatigue
from dice_types import make_pool, pool_tn
from session_effects import session_outcome

from .catalog import QUALITY_CATALOG
from .state import PlayerState


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
    ef_indices: tuple[int, ...]
    quality_indices: tuple[int, ...]
    ef_energy: int
    quality_energy: int
    planned_qualities: tuple[str, ...]
    successful_qualities: tuple[str, ...]
    busted_quality: str | None
    quality_costs: tuple[tuple[str, int], ...]
    progression_spec_gained: int
    fatigue_blackjack: int
    fatigue_excess: int
    fatigue_specific: int
    fatigue_after: int
    dice_pool_after: tuple[int, ...]


@dataclass(frozen=True)
class RollResult:
    raw_faces: tuple[int, ...]
    final_values: tuple[int, ...]
    tn: float


def _apply_milestones(state: PlayerState, old_ef: int, old_q: int) -> None:
    for milestone in EF_MILESTONES:
        if old_ef < milestone <= state.progression_ef:
            if milestone not in state.ef_milestones_claimed:
                state.ef_milestones_claimed.add(milestone)
                if milestone in EF_DIE_MILESTONES:
                    if state.dice_added < 2 and len(state.dice_pool) < 6:
                        state.dice_pool.append(6)
                        state.dice_added += 1
                elif state.profile.ef + 1 < state.profile.threshold:
                    state.profile.ef += 1

    for milestone in Q_MILESTONES:
        if old_q < milestone <= state.progression_q:
            if milestone in state.q_milestones_claimed:
                continue
            state.q_milestones_claimed.add(milestone)
            if milestone not in Q_UPGRADE_MILESTONES or state.upgrades_used >= 4:
                continue
            eligible = [
                index for index, size in enumerate(state.dice_pool) if size < 12
            ]
            if eligible:
                index = min(eligible, key=lambda i: (state.dice_pool[i], i))
                current = state.dice_pool[index]
                state.dice_pool[index] = DIE_SIZES[DIE_SIZES.index(current) + 1]
                state.upgrades_used += 1


def _validate_partition(values, ef_indices, quality_indices):
    ef_indices = tuple(ef_indices)
    quality_indices = tuple(quality_indices)
    all_indices = ef_indices + quality_indices
    if not ef_indices or not quality_indices:
        raise ValueError("EF and quality compartments must both be non-empty")
    if len(set(all_indices)) != len(all_indices):
        raise ValueError("a die cannot be allocated more than once")
    if set(all_indices) != set(range(len(values))):
        raise ValueError("every retained die must be allocated exactly once")
    ef_energy = sum(values[index] for index in ef_indices)
    quality_energy = sum(values[index] for index in quality_indices)
    if ef_energy < quality_energy:
        raise ValueError("the experimental partition requires EF energy >= quality energy")
    return ef_indices, quality_indices, ef_energy, quality_energy


def resolve_turn(
    state: PlayerState,
    raw_faces,
    ef_indices,
    quality_indices,
    planned_qualities,
    *,
    risk_faces=(),
    rng=None,
) -> TurnResult:
    """Resolve a supplied roll and player programme, mutating state.

    risk_faces optionally injects one raw risk die face per risky quality;
    otherwise the engine draws from the largest die in the persistent pool.
    This makes bust outcomes reproducible in unit tests.
    """
    raw_faces = tuple(raw_faces)
    if len(raw_faces) != len(state.dice_pool):
        raise ValueError("one raw face is required for every die in the pool")
    if any(face < 1 or face > size
           for face, size in zip(raw_faces, state.dice_pool)):
        raise ValueError("raw face is outside its die range")
    planned_qualities = tuple(planned_qualities)
    if len(set(planned_qualities)) != len(planned_qualities):
        raise ValueError("a quality option cannot be selected twice in one turn")
    if any(name not in QUALITY_CATALOG for name in planned_qualities):
        raise ValueError("unknown quality option")
    from .catalog import projected_profile
    projected = projected_profile(state.profile, planned_qualities)
    if not projected["ef"] < projected["threshold"] < projected["vma"]:
        raise ValueError("session adaptations would violate EF < Seuil < VMA")

    dice = make_pool(state.dice_pool)
    tn = pool_tn(dice)
    outcome = session_outcome(raw_faces, raw_faces, len(state.dice_pool))
    values = tuple(outcome["dice_used"])
    ef_indices, quality_indices, ef_energy, quality_energy = _validate_partition(
        values, ef_indices, quality_indices
    )

    costs = tuple(
        (name, QUALITY_CATALOG[name].energy_cost)
        for name in planned_qualities
    )
    total_cost = sum(cost for _, cost in costs)
    if total_cost > quality_energy:
        raise ValueError("quality programme exceeds its allocated energy")

    rng = rng if rng is not None else random.Random()
    rng_faces = iter(risk_faces)
    successful = []
    busted = None
    fatigue_specific = 0
    for name, cost in costs:
        option = QUALITY_CATALOG[name]
        rpe = QUALITY_CATALOG[name].rpe
        if rpe > max(values):
            try:
                risk_face = next(rng_faces)
            except StopIteration:
                risk_face = rng.randint(1, max(state.dice_pool))
            if risk_face < 1 or risk_face > max(state.dice_pool):
                raise ValueError("risk face is outside the largest die range")
            if risk_face <= rpe - max(values):
                if busted is None:
                    busted = name
                continue
        successful.append(name)
        fatigue_specific += option.fatigue

    old_ef, old_q = state.progression_ef, state.progression_q
    state.progression_ef += ef_energy
    state.progression_q += sum(
        cost for name, cost in costs if name in successful
    )
    # Unassigned quality energy becomes SPEC progression; assigned energy lost
    # to a bust is not refunded. This is the documented B2 Q_SPENT_SPEC variant.
    spec_gained = quality_energy - total_cost
    state.progression_spec += spec_gained

    for name in successful:
        for attribute, amount in QUALITY_CATALOG[name].adaptations:
            setattr(
                state.profile,
                attribute,
                getattr(state.profile, attribute) + amount,
            )

    _apply_milestones(state, old_ef, old_q)

    _, fatigue_blackjack = energy_and_fatigue(sum(values), tn)
    fatigue_excess = math.ceil(max(0, quality_energy - ef_energy) / 2)
    state.fatigue = max(
        0, state.fatigue + fatigue_blackjack + fatigue_excess + fatigue_specific
    )
    state.turns_played += 1

    return TurnResult(
        turn=state.turns_played,
        raw_faces=raw_faces,
        final_values=values,
        tn=tn,
        ef_indices=ef_indices,
        quality_indices=quality_indices,
        ef_energy=ef_energy,
        quality_energy=quality_energy,
        planned_qualities=planned_qualities,
        successful_qualities=tuple(successful),
        busted_quality=busted,
        quality_costs=costs,
        progression_spec_gained=spec_gained,
        fatigue_blackjack=fatigue_blackjack,
        fatigue_excess=fatigue_excess,
        fatigue_specific=fatigue_specific,
        fatigue_after=state.fatigue,
        dice_pool_after=tuple(state.dice_pool),
    )


def roll_pool(state: PlayerState, *, rng=None) -> RollResult:
    """Roll and resolve retained dice before the player chooses a partition."""
    rng = rng if rng is not None else random.Random()
    raw_faces = tuple(rng.randint(1, size) for size in state.dice_pool)
    outcome = session_outcome(raw_faces, raw_faces, len(state.dice_pool))
    return RollResult(
        raw_faces=raw_faces,
        final_values=tuple(outcome["dice_used"]),
        tn=pool_tn(make_pool(state.dice_pool)),
    )


def roll_and_resolve_turn(
    state: PlayerState,
    choose_program,
    *,
    rng=None,
    risk_faces=(),
) -> TurnResult:
    """Roll first, then call choose_program(RollResult) for the player's choice.

    choose_program returns (ef_indices, quality_indices, planned_qualities).
    """
    rng = rng if rng is not None else random.Random()
    roll = roll_pool(state, rng=rng)
    ef_indices, quality_indices, planned_qualities = choose_program(roll)
    return resolve_turn(
        state, roll.raw_faces, ef_indices, quality_indices, planned_qualities,
        risk_faces=risk_faces, rng=rng,
    )
