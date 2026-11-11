"""Training B dose/session resolution.

All catalogue values in this module are EXPERIMENTAL calibration fixtures.
The resolver is deterministic when supplied with a deterministic risk roller.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable, Iterable

from .budget import TrainingEnergyBudget
from .state import PlayerState


@dataclass(frozen=True)
class SessionDose:
    key: str
    label: str
    family: str
    budget: str
    dose: int
    rpe: int
    primary_track: str
    primary_xp: int
    secondary_track: str
    secondary_xp: int
    fatigue: int
    max_per_turn: int = 1
    calibration: str = "EXPERIMENTAL"

    def __post_init__(self):
        if self.budget not in {"EF", "THRESHOLD", "VMA"}:
            raise ValueError("unknown session budget")
        if self.dose < 1 or self.rpe < 0 or self.fatigue < 0:
            raise ValueError("dose, RPE and fatigue must be non-negative")
        if self.primary_track not in {"ef", "threshold", "vma"}:
            raise ValueError("invalid primary adaptation track")
        if self.secondary_track not in {"ef", "threshold", "vma"}:
            raise ValueError("invalid secondary adaptation track")
        if self.primary_xp < 0 or self.secondary_xp < 0:
            raise ValueError("adaptation XP cannot be negative")
        if self.max_per_turn < 1:
            raise ValueError("max_per_turn must be positive")


# Provisional values chosen to make the complete loop executable.
# Dose, RPE, adaptation and fatigue are deliberately independent dimensions.
SESSION_DOSES = {
    "EF1": SessionDose("EF1", "Endurance fondamentale 1", "EF", "EF", 1, 1, "ef", 1, "threshold", 0, 0, 4),
    "EF2": SessionDose("EF2", "Endurance fondamentale 2", "EF", "EF", 2, 2, "ef", 2, "threshold", 1, 1, 3),
    "EF3": SessionDose("EF3", "Endurance fondamentale 3", "EF", "EF", 3, 3, "ef", 3, "threshold", 1, 2, 2),
    "EF4": SessionDose("EF4", "Endurance fondamentale 4", "EF", "EF", 4, 4, "ef", 4, "threshold", 2, 3, 1),
    "SEUIL3": SessionDose("SEUIL3", "Seuil dose 3", "SEUIL", "THRESHOLD", 3, 3, "threshold", 2, "ef", 1, 2),
    "SEUIL4": SessionDose("SEUIL4", "Seuil dose 4", "SEUIL", "THRESHOLD", 4, 4, "threshold", 3, "ef", 1, 3),
    "SEUIL5": SessionDose("SEUIL5", "Seuil dose 5", "SEUIL", "THRESHOLD", 5, 5, "threshold", 4, "ef", 2, 4),
    "VMA3": SessionDose("VMA3", "VMA dose 3", "VMA", "VMA", 3, 4, "vma", 2, "threshold", 1, 3),
    "VMA4": SessionDose("VMA4", "VMA dose 4", "VMA", "VMA", 4, 5, "vma", 3, "threshold", 1, 4),
    "VMA5": SessionDose("VMA5", "VMA dose 5", "VMA", "VMA", 5, 6, "vma", 4, "threshold", 2, 5),
}


@dataclass(frozen=True)
class ResolvedSession:
    key: str
    success: bool
    risk_excess: int
    risk_face: int | None
    fatigue: int
    adaptations: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class SessionResolution:
    planned: tuple[str, ...]
    resolved: tuple[ResolvedSession, ...]
    busted_session: str | None
    cancelled_sessions: tuple[str, ...]
    fatigue_added: int
    xp_added: tuple[tuple[str, int], ...]

    @property
    def successful_sessions(self) -> tuple[str, ...]:
        return tuple(row.key for row in self.resolved if row.success)


def validate_session_plan(
    state: PlayerState,
    budget: TrainingEnergyBudget,
    session_keys: Iterable[str],
) -> tuple[str, ...]:
    """Validate portfolio, per-session limits and exact EF/Seuil/VMA accounting."""
    keys = tuple(session_keys)
    counts: dict[str, int] = {}
    spent = {"EF": 0, "THRESHOLD": 0, "VMA": 0}
    for key in keys:
        if key not in SESSION_DOSES:
            raise ValueError(f"unknown Training B session: {key}")
        if key not in state.acquired_session_keys:
            raise ValueError(f"session is not acquired: {key}")
        option = SESSION_DOSES[key]
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > option.max_per_turn:
            raise ValueError(f"session repetition limit exceeded: {key}")
        spent[option.budget] += option.dose
    expected = {
        "EF": budget.ef_energy,
        "THRESHOLD": budget.threshold_energy,
        "VMA": budget.vma_energy,
    }
    if spent != expected:
        raise ValueError(f"session doses {spent} do not match budgets {expected}")
    return keys


def resolve_session_plan(
    state: PlayerState,
    budget: TrainingEnergyBudget,
    session_keys: Iterable[str],
    *,
    rpe_authorized: int,
    rng=None,
    risk_roll: Callable[[int], int] | None = None,
) -> SessionResolution:
    """Resolve ordered sessions; the first bust cancels itself and all later rows.

    EXPERIMENTAL bust rule: for a session above the authorized RPE, roll the
    largest persistent die. Bust occurs when its raw face is <= (session RPE
    - authorized RPE). A successful session applies both adaptations and its
    session fatigue. Dice-derived fatigue has already been applied by turn.py
    and is never rolled back by this function.
    """
    if isinstance(rpe_authorized, bool) or not isinstance(rpe_authorized, int) or rpe_authorized < 0:
        raise ValueError("rpe_authorized must be a non-negative integer")
    keys = validate_session_plan(state, budget, session_keys)
    roller = rng if rng is not None else random.Random()
    best_die = max(state.dice_pool)
    roll = risk_roll or (lambda size: roller.randint(1, size))

    rows: list[ResolvedSession] = []
    xp = {"ef": 0, "threshold": 0, "vma": 0}
    fatigue_added = 0
    busted = None
    cancelled: tuple[str, ...] = ()

    for index, key in enumerate(keys):
        option = SESSION_DOSES[key]
        excess = max(0, option.rpe - rpe_authorized)
        face = None
        success = True
        if excess:
            face = roll(best_die)
            if isinstance(face, bool) or not isinstance(face, int) or not 1 <= face <= best_die:
                raise ValueError("risk roll must be a raw face within the best die")
            success = face > excess
        if not success:
            busted = key
            rows.append(ResolvedSession(key, False, excess, face, 0, ()))
            cancelled = keys[index + 1:]
            break

        adaptations = (
            (option.primary_track, option.primary_xp),
            (option.secondary_track, option.secondary_xp),
        )
        for track, amount in adaptations:
            xp[track] += amount
        fatigue_added += option.fatigue
        rows.append(ResolvedSession(key, True, excess, face, option.fatigue, adaptations))

    state.progression_ef += xp["ef"]
    state.progression_threshold += xp["threshold"]
    state.progression_vma += xp["vma"]
    state.fatigue += fatigue_added
    return SessionResolution(
        planned=keys,
        resolved=tuple(rows),
        busted_session=busted,
        cancelled_sessions=cancelled,
        fatigue_added=fatigue_added,
        xp_added=tuple((track, value) for track, value in xp.items()),
    )
