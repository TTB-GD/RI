"""Experimental, playable Training B turn engine."""
from .engine import RollResult, TurnResult, resolve_turn, roll_pool, roll_and_resolve_turn
from .programs import ProgramOption, SessionAllocation, list_program_options
from .catalog import SessionOption, SESSION_CATALOG
from .state import PlayerState, PhysiologyProfile
from .physiology import PhysiologyPoint, PhysiologyCurve
from .physiology_progression import (
    PhysiologyMilestone, PhysiologyUpgrade, validate_physiology_milestones,
    apply_physiology_milestones,
)
from .portfolio import make_session_eligible, acquire_session
from .milestones import PortfolioMilestone
from .dice import DiceActionResult, resolve_dice_action
from .budget import TrainingEnergyBudget
from .turn import TrainingTurnResult, resolve_training_turn
from .session_resolution import (
    SessionDose, SESSION_DOSES, ResolvedSession, SessionResolution,
    validate_session_plan, resolve_session_plan,
)

__all__ = [
    "PlayerState", "PhysiologyProfile", "PhysiologyPoint", "PhysiologyCurve",
    "PhysiologyMilestone", "PhysiologyUpgrade", "validate_physiology_milestones",
    "apply_physiology_milestones", "RollResult", "DiceActionResult", "TurnResult",
    "ProgramOption", "SessionAllocation", "SessionOption", "SESSION_CATALOG",
    "list_program_options", "resolve_turn", "roll_pool", "roll_and_resolve_turn", "resolve_dice_action",
    "make_session_eligible", "acquire_session", "PortfolioMilestone", "TrainingEnergyBudget",
    "TrainingTurnResult", "resolve_training_turn", "SessionDose", "SESSION_DOSES",
    "ResolvedSession", "SessionResolution", "validate_session_plan", "resolve_session_plan",
]
