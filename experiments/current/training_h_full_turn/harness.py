"""EXPERIMENTAL H full-turn resolver.

This module is deliberately independent from the legacy Training engine.
The caller supplies player decisions and the result of any risk roll; this
module never chooses an action or a session for the player.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Session:
    name: str
    category: str  # "EF" or "QUALITY"
    cost: int
    intrinsic_fatigue: int = 0
    risky: bool = False

    def __post_init__(self):
        if self.category not in {"EF", "QUALITY"}:
            raise ValueError("category must be EF or QUALITY")
        if self.cost <= 0:
            raise ValueError("session cost must be positive")
        if self.intrinsic_fatigue < 0:
            raise ValueError("intrinsic fatigue cannot be negative")


@dataclass(frozen=True)
class DiceResolution:
    action: str
    final_dice: tuple[int, ...]
    energy: int
    tn: float
    blackjack_fatigue: int


@dataclass(frozen=True)
class ProgramResolution:
    completed: tuple[Session, ...]
    failed: Session | None
    cancelled: tuple[Session, ...]
    ef_spent: int
    quality_spent: int
    imbalance_fatigue: int
    intrinsic_fatigue: int
    progression_tokens: tuple[str, ...]


def pool_tn(pool_sizes: Iterable[int]) -> float:
    sizes = tuple(pool_sizes)
    if len(sizes) < 2 or any(size not in {6, 8, 10, 12} for size in sizes):
        raise ValueError("pool must contain at least two d6/d8/d10/d12 dice")
    return sum((size + 1) / 2 for size in sizes)


def blackjack_fatigue(energy: int, tn: float) -> int:
    """Legacy blackjack curve, evaluated once on the final dice result."""
    delta = energy - tn
    offset = int(delta + 0.5) if delta >= 0 else int(delta - 0.5)
    if offset >= -1:
        fib = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
        index = offset + 3
        return fib[index] if 0 <= index < len(fib) else fib[-1]
    if offset in (-2, -3):
        return 0
    return {-4: -1, -5: -1, -6: -2, -7: -2, -8: -3, -9: -5}.get(offset, -8)


def _reserve_index(pool_sizes):
    return min(range(len(pool_sizes)), key=lambda i: (pool_sizes[i], -i))


def _active_sizes(pool_sizes):
    reserve_index = _reserve_index(pool_sizes)
    return tuple(size for i, size in enumerate(pool_sizes) if i != reserve_index)


def resolve_dice_action(
    pool_sizes: Iterable[int],
    active_values: Iterable[int],
    reserve_value: int,
    action: str,
    reroll_index: int | None = None,
    rerolled_value: int | None = None,
    *,
    overtraining: bool = False,
) -> DiceResolution:
    """Resolve an explicit Keep/Reroll/Add/Add+Reroll player choice."""
    sizes = tuple(pool_sizes)
    tn = pool_tn(sizes)
    active_sizes = _active_sizes(sizes)
    active = list(active_values)
    if len(active) != len(sizes) - 1:
        raise ValueError("initial roll must contain n-1 active dice")
    if any(v < 1 or v > size for v, size in zip(active, active_sizes)):
        raise ValueError("active die result outside its die range")
    if action not in {"keep", "reroll", "add", "add+reroll"}:
        raise ValueError("unknown dice action")
    if overtraining and action in {"add", "add+reroll"}:
        raise ValueError("reserve actions are unavailable during overtraining")
    if action in {"reroll", "add+reroll"}:
        if reroll_index is None or not 0 <= reroll_index < len(active):
            raise ValueError("reroll action requires a valid active die index")
        if rerolled_value is None:
            raise ValueError("reroll action requires a rerolled value")
        if not 1 <= rerolled_value <= active_sizes[reroll_index]:
            raise ValueError("rerolled value outside die range")
        active[reroll_index] = rerolled_value
    elif reroll_index is not None or rerolled_value is not None:
        raise ValueError("reroll data supplied for an action without reroll")

    if action in {"add", "add+reroll"}:
        reserve_size = sizes[_reserve_index(sizes)]
        if not 1 <= reserve_value <= reserve_size:
            raise ValueError("reserve result outside its die range")
        active.append(reserve_value)

    energy = sum(active)
    return DiceResolution(action, tuple(active), energy, tn,
                          blackjack_fatigue(energy, tn))


def resolve_program(
    ef_budget: int,
    quality_budget: int,
    planned_sessions: Iterable[Session],
    bust_index: int | None = None,
    *,
    total_energy: int,
) -> ProgramResolution:
    """Resolve a player-composed H programme after the dice phase.

    The EF and Quality budgets must partition no more than the final dice
    energy. On bust, the indexed risky session fails. Later risky sessions
    are cancelled, while later safe sessions remain completable, matching
    the legacy session-resolution convention. No automatic redistribution.
    """
    sessions = tuple(planned_sessions)
    if ef_budget < 0 or quality_budget < 0 or total_energy < 0:
        raise ValueError("energy and budgets cannot be negative")
    if ef_budget + quality_budget > total_energy:
        raise ValueError("EF and Quality budgets exceed final dice energy")
    if bust_index is not None:
        if not 0 <= bust_index < len(sessions):
            raise IndexError("bust_index outside planned programme")
        if not sessions[bust_index].risky:
            raise ValueError("only a risky session can bust")

    ef_spent = quality_spent = 0
    completed, cancelled = [], []
    failed = None
    for index, session in enumerate(sessions):
        if bust_index is not None and index == bust_index:
            failed = session
            continue
        if bust_index is not None and index > bust_index and session.risky:
            cancelled.append(session)
            continue
        if session.category == "EF":
            ef_spent += session.cost
            if ef_spent > ef_budget:
                raise ValueError("EF sessions exceed EF budget")
        else:
            quality_spent += session.cost
            if quality_spent > quality_budget:
                raise ValueError("quality sessions exceed quality budget")
        completed.append(session)

    imbalance = (max(0, quality_spent - ef_spent) + 1) // 2
    intrinsic = sum(s.intrinsic_fatigue for s in completed)
    tokens = tuple(s.name for s in completed)
    return ProgramResolution(tuple(completed), failed, tuple(cancelled),
                             ef_spent, quality_spent, imbalance,
                             intrinsic, tokens)


def resolve_turn(dice: DiceResolution, program: ProgramResolution,
                 prior_fatigue: int = 0) -> dict:
    """Combine immutable roll fatigue with realized-program fatigue."""
    if prior_fatigue < 0:
        raise ValueError("prior fatigue cannot be negative")
    return {
        "energy": dice.energy,
        "tn": dice.tn,
        "fatigue_blackjack": dice.blackjack_fatigue,
        "fatigue_imbalance": program.imbalance_fatigue,
        "fatigue_intrinsic": program.intrinsic_fatigue,
        "fatigue_turn": (dice.blackjack_fatigue
                         + program.imbalance_fatigue
                         + program.intrinsic_fatigue),
        "fatigue_cumulative": (prior_fatigue + dice.blackjack_fatigue
                               + program.imbalance_fatigue
                               + program.intrinsic_fatigue),
        "completed_sessions": program.progression_tokens,
        "failed_session": program.failed.name if program.failed else None,
        "cancelled_sessions": tuple(s.name for s in program.cancelled),
    }
