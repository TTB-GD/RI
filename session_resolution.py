"""Résolution ordonnée d'un bundle après le bust d'une séance risquée."""

from dataclasses import dataclass

from session_selector import MAX_SESSIONS_PER_TURN
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG


@dataclass(frozen=True)
class SessionResolution:
    """Résultat mécanique séparant séances comptées et séances validées."""

    counted_sessions: tuple
    completed_sessions: tuple
    cancelled_sessions: tuple
    replacement_sessions: tuple
    energy_effective: int
    energy_lost: int
    redistribution_energy: int
    stop_reason: str


def _is_risky_quality(name, rpe_max):
    category, rpe = SESSION_CATALOG[name]
    return category in QUALITY_CATEGORIES and rpe > rpe_max


def resolve_session_plan(planned, available_session_names, rpe_max, bust_index=None):
    """Résout un plan, avec un bust injecté de façon déterministe si demandé.

    ``bust_index`` désigne l'index de la séance risquée qui bust. La séance
    compte mais n'est pas validée. Les qualités risquées suivantes sont
    annulées et leur seul budget est redistribuable en EF. Les séances non
    risquées prévues restent validées, même lorsqu'elles suivent le bust.
    """
    planned = tuple(planned)
    if len(planned) > MAX_SESSIONS_PER_TURN:
        raise ValueError("planned bundle exceeds seven sessions")
    if bust_index is None:
        energy = sum(SESSION_CATALOG[name][1] for name in planned)
        return SessionResolution(
            planned, planned, (), (), energy, 0, 0, "plan_completed",
        )
    if not 0 <= bust_index < len(planned):
        raise IndexError("bust_index outside planned bundle")
    busted = planned[bust_index]
    if not _is_risky_quality(busted, rpe_max):
        raise ValueError("only a quality session above RPE Max can bust")

    completed = []
    counted = []
    cancelled = []
    for index, name in enumerate(planned):
        if index == bust_index:
            counted.append(name)
        elif index > bust_index and _is_risky_quality(name, rpe_max):
            cancelled.append(name)
        else:
            counted.append(name)
            completed.append(name)

    redistribution_energy = sum(SESSION_CATALOG[name][1] for name in cancelled)
    remaining = redistribution_energy
    ef_candidates = sorted(
        {
            name for name in available_session_names
            if SESSION_CATALOG[name][0] == "EF"
            and SESSION_CATALOG[name][1] <= rpe_max
        },
        key=lambda name: (-SESSION_CATALOG[name][1], name),
    )
    replacements = []
    while len(counted) < MAX_SESSIONS_PER_TURN:
        affordable = next(
            (name for name in ef_candidates if SESSION_CATALOG[name][1] <= remaining),
            None,
        )
        if affordable is None:
            break
        replacements.append(affordable)
        counted.append(affordable)
        completed.append(affordable)
        remaining -= SESSION_CATALOG[affordable][1]

    energy_effective = sum(SESSION_CATALOG[name][1] for name in completed)
    if cancelled and len(counted) == MAX_SESSIONS_PER_TURN and remaining:
        stop_reason = "seven_session_limit"
    elif cancelled and remaining:
        stop_reason = "no_affordable_ef"
    elif cancelled:
        stop_reason = "redistribution_complete"
    else:
        stop_reason = "bust_no_later_risk"
    return SessionResolution(
        tuple(counted), tuple(completed), tuple(cancelled), tuple(replacements),
        energy_effective, SESSION_CATALOG[busted][1], redistribution_energy,
        stop_reason,
    )
