"""Configurable local progression milestones for Training B portfolio unlocks."""
from dataclasses import dataclass

from .catalog import SESSION_CATALOG


@dataclass(frozen=True)
class PortfolioMilestone:
    key: str
    track: str
    threshold: int
    unlock_session_keys: tuple[str, ...]

    def __post_init__(self):
        if not self.key or self.track not in {"ef", "threshold", "vma"}:
            raise ValueError("milestone needs a key and a local EF/threshold/VMA track")
        if self.threshold <= 0:
            raise ValueError("milestone threshold must be positive")
        if not self.unlock_session_keys:
            raise ValueError("milestone must unlock at least one session")
        if len(set(self.unlock_session_keys)) != len(self.unlock_session_keys):
            raise ValueError("milestone unlock keys must be unique")
        if any(key not in SESSION_CATALOG for key in self.unlock_session_keys):
            raise ValueError("milestone references an unknown session")


def validate_portfolio_milestones(milestones):
    milestones = tuple(milestones)
    keys = [milestone.key for milestone in milestones]
    if len(keys) != len(set(keys)):
        raise ValueError("portfolio milestone keys must be unique")
    return milestones
