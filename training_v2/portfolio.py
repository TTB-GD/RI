"""Explicit eligibility and acquisition lifecycle for permanent sessions."""
from .catalog import SESSION_CATALOG
from .state import PlayerState


def make_session_eligible(state: PlayerState, session_key: str) -> None:
    """Expose a catalogue option without automatically acquiring it.

    Progression milestones call this function; their thresholds remain a
    separate, intentionally open design decision.
    """
    if session_key not in SESSION_CATALOG:
        raise ValueError("unknown session")
    state.eligible_session_keys.add(session_key)


def acquire_session(state: PlayerState, session_key: str) -> None:
    """Permanently add an eligible option to the player's portfolio."""
    if session_key not in SESSION_CATALOG:
        raise ValueError("unknown session")
    if session_key not in state.eligible_session_keys:
        raise ValueError("session is not eligible for acquisition")
    state.acquired_session_keys.add(session_key)
