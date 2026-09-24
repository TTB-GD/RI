"""Détection minimale du risque et du premier bust d'un plan de séances."""

from dice_types import Die
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG


def base_bust_threshold(session_rpe, rpe_max):
    """Seuil CURRENT : dépassement positif de la zone sûre."""
    return max(0, session_rpe - rpe_max)


def apply_optional_risk_modifier(threshold, context=None):
    """Frontière neutre CURRENT pour de futures modulations expérimentales."""
    return threshold


def is_risky_quality(session_name, rpe_max):
    category, rpe = SESSION_CATALOG[session_name]
    return category in QUALITY_CATEGORIES and rpe > rpe_max


def is_risk_tentable(session_name, rpe_max, best_die_size):
    """Écarte uniquement les prises de risque dont le bust est certain."""
    if not is_risky_quality(session_name, rpe_max):
        return True
    threshold = apply_optional_risk_modifier(
        base_bust_threshold(SESSION_CATALOG[session_name][1], rpe_max),
        context={"session": session_name},
    )
    return threshold < best_die_size


def first_bust_index(planned, rpe_max, pool_sizes, roll_face=None):
    """Teste les qualités risquées dans l'ordre et retourne le premier index.

    ``roll_face`` reçoit la taille du meilleur dé et facilite les tests. En
    production, ``Die.roll`` fournit une paire (face brute, valeur bonifiée) :
    seule la face brute est comparée au seuil.
    """
    if not pool_sizes:
        raise ValueError("pool_sizes must not be empty")
    die_size = max(pool_sizes)

    def default_roll(size):
        raw_face, _ = Die(size).roll()
        return raw_face

    roller = roll_face or default_roll
    for index, name in enumerate(planned):
        if not is_risky_quality(name, rpe_max):
            continue
        threshold = apply_optional_risk_modifier(
            base_bust_threshold(SESSION_CATALOG[name][1], rpe_max),
            context={"session": name, "index": index},
        )
        raw_face = roller(die_size)
        if not 1 <= raw_face <= die_size:
            raise ValueError("risk roll outside die range")
        if raw_face <= threshold:
            return index
    return None
