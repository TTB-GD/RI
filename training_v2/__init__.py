"""Experimental, playable Training B turn engine."""
from .engine import RollResult, TurnResult, resolve_turn, roll_pool, roll_and_resolve_turn
from .programs import ProgramOption, SessionAllocation, list_program_options
from .catalog import SessionOption, SESSION_CATALOG
from .state import PlayerState, PhysiologyProfile

__all__ = [
    "PlayerState", "PhysiologyProfile", "RollResult", "TurnResult",
    "ProgramOption", "SessionAllocation", "SessionOption", "SESSION_CATALOG",
    "list_program_options", "resolve_turn", "roll_pool", "roll_and_resolve_turn",
]
