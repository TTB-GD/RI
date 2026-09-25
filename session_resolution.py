"""Résolution ordonnée d'un programme et choix post-bust explicite."""

from dataclasses import dataclass

from session_selector import MAX_SESSIONS_PER_TURN
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG


@dataclass(frozen=True)
class RedistributionOptions:
    """Ressources et EF légalement disponibles après un bust."""

    replacement_energy: int
    replacement_slots: int
    legal_ef: tuple


@dataclass(frozen=True)
class SessionResolution:
    """Résultat mécanique séparant programme, choix et séances validées."""

    counted_sessions: tuple
    completed_sessions: tuple
    cancelled_sessions: tuple
    replacement_sessions: tuple
    energy_effective: int
    energy_lost: int
    redistribution_energy: int
    replacement_slots: int
    legal_replacement_sessions: tuple
    replacement_energy_used: int
    stop_reason: str


def _is_risky_quality(name, rpe_max):
    category, rpe = SESSION_CATALOG[name]
    return category in QUALITY_CATEGORIES and rpe > rpe_max


def _post_bust_state(planned, available_session_names, rpe_max, bust_index):
    """Valide le bust et calcule l'état initial, sans choisir de remplacement."""
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

    options = RedistributionOptions(
        replacement_energy=sum(SESSION_CATALOG[name][1] for name in cancelled),
        replacement_slots=len(cancelled),
        legal_ef=tuple(
            name for name in dict.fromkeys(available_session_names)
            if SESSION_CATALOG[name][0] == "EF"
            and SESSION_CATALOG[name][1] <= rpe_max
        ),
    )
    return busted, counted, completed, cancelled, options


def post_bust_redistribution_options(
    planned, available_session_names, rpe_max, bust_index
):
    """Retourne les ressources/options légales, sans appliquer de politique."""
    planned = tuple(planned)
    if len(planned) > MAX_SESSIONS_PER_TURN:
        raise ValueError("planned bundle exceeds seven sessions")
    return _post_bust_state(
        planned, available_session_names, rpe_max, bust_index
    )[4]


def resolve_session_plan(
    planned, available_session_names, rpe_max, bust_index=None,
    replacement_choices=(),
):
    """Résout le programme puis applique les EF explicitement choisies.

    Après un bust, ``replacement_choices`` peut contenir zéro ou plusieurs EF.
    Le moteur valide le choix contre les places, l'énergie et les EF accessibles
    sûres. Il ne choisit jamais une EF à la place du joueur.
    """
    planned = tuple(planned)
    replacement_choices = tuple(replacement_choices)
    if len(planned) > MAX_SESSIONS_PER_TURN:
        raise ValueError("planned bundle exceeds seven sessions")
    if bust_index is None:
        if replacement_choices:
            raise ValueError("replacement sessions require a bust")
        energy = sum(SESSION_CATALOG[name][1] for name in planned)
        return SessionResolution(
            planned, planned, (), (), energy, 0, 0, 0, (), 0,
            "plan_completed",
        )

    busted, counted, completed, cancelled, options = _post_bust_state(
        planned, available_session_names, rpe_max, bust_index
    )
    if any(name not in options.legal_ef for name in replacement_choices):
        raise ValueError("replacement session is not an accessible safe EF")
    replacement_energy_used = sum(
        SESSION_CATALOG[name][1] for name in replacement_choices
    )
    if replacement_energy_used > options.replacement_energy:
        raise ValueError("replacement sessions exceed redistribution energy")
    if len(replacement_choices) > options.replacement_slots:
        raise ValueError("replacement sessions exceed available slots")
    if len(counted) + len(replacement_choices) > MAX_SESSIONS_PER_TURN:
        raise ValueError("replacement sessions exceed seven sessions")

    counted.extend(replacement_choices)
    completed.extend(replacement_choices)
    energy_effective = sum(SESSION_CATALOG[name][1] for name in completed)
    if not cancelled:
        stop_reason = "bust_no_later_risk"
    elif not replacement_choices:
        stop_reason = "redistribution_declined"
    elif (len(replacement_choices) < options.replacement_slots
          and replacement_energy_used < options.replacement_energy):
        stop_reason = "redistribution_partial"
    else:
        stop_reason = "redistribution_resolved"
    return SessionResolution(
        tuple(counted), tuple(completed), tuple(cancelled), replacement_choices,
        energy_effective, SESSION_CATALOG[busted][1],
        options.replacement_energy, options.replacement_slots,
        options.legal_ef, replacement_energy_used, stop_reason,
    )
