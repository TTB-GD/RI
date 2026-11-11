"""Persistent state for the experimental Training B prototype."""
from dataclasses import dataclass, field

from .physiology import PhysiologyCurve


INITIAL_SESSION_PORTFOLIO = {
    "EF", "SEUIL", "VMA",  # historical prototype keys
    "EF1", "EF2", "EF3", "EF4",
    "SEUIL3", "SEUIL4", "SEUIL5",
    "VMA3", "VMA4", "VMA5",
}


@dataclass
class PhysiologyProfile:
    ef: int = 6
    threshold: int = 8
    vma: int = 10

    def validate(self):
        if not self.ef < self.threshold < self.vma:
            raise ValueError("profile must satisfy EF < Seuil < VMA")


@dataclass
class PlayerState:
    profile: PhysiologyProfile = field(default_factory=PhysiologyProfile)  # legacy direct-allocation path
    dice_pool: list[int] = field(default_factory=lambda: [6, 6, 6, 6])
    progression_ef: int = 0
    progression_q: int = 0
    progression_threshold: int = 0
    progression_vma: int = 0
    progression_spec: int = 0
    fatigue: int = 0
    turns_played: int = 0
    upgrades_used: int = 0
    dice_added: int = 0
    ef_milestones_claimed: set[int] = field(default_factory=set)
    q_milestones_claimed: set[int] = field(default_factory=set)
    portfolio_milestones_claimed: set[str] = field(default_factory=set)
    eligible_session_keys: set[str] = field(default_factory=lambda: set(INITIAL_SESSION_PORTFOLIO))
    acquired_session_keys: set[str] = field(default_factory=lambda: set(INITIAL_SESSION_PORTFOLIO))
    race_curve: PhysiologyCurve | None = None
    physiology_milestones_claimed: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.profile.validate()
        if self.race_curve is not None and not isinstance(self.race_curve, PhysiologyCurve):
            raise ValueError("race_curve must be a PhysiologyCurve")
        if len(self.dice_pool) < 4 or len(self.dice_pool) > 6:
            raise ValueError("dice pool must contain between four and six dice")
        if any(size not in (6, 8, 10, 12) for size in self.dice_pool):
            raise ValueError("dice pool supports only d6, d8, d10 and d12")
        if self.fatigue < 0:
            raise ValueError("fatigue cannot be negative")
        if not self.acquired_session_keys <= self.eligible_session_keys:
            raise ValueError("acquired sessions must also be eligible")

    def clone(self):
        """Return an independent state suitable for branching a playtest."""
        return PlayerState(
            profile=PhysiologyProfile(self.profile.ef, self.profile.threshold, self.profile.vma),
            race_curve=self.race_curve,
            physiology_milestones_claimed=set(self.physiology_milestones_claimed),
            dice_pool=list(self.dice_pool),
            progression_ef=self.progression_ef,
            progression_q=self.progression_q,
            progression_threshold=self.progression_threshold,
            progression_vma=self.progression_vma,
            progression_spec=self.progression_spec,
            fatigue=self.fatigue,
            turns_played=self.turns_played,
            upgrades_used=self.upgrades_used,
            dice_added=self.dice_added,
            ef_milestones_claimed=set(self.ef_milestones_claimed),
            q_milestones_claimed=set(self.q_milestones_claimed),
            portfolio_milestones_claimed=set(self.portfolio_milestones_claimed),
            eligible_session_keys=set(self.eligible_session_keys),
            acquired_session_keys=set(self.acquired_session_keys),
        )
