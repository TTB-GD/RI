"""Persistent state for the isolated Training V2 prototype.

Milestone values are provisional calibration from the B2 experimental harness.
They are not CURRENT game rules.
"""
from dataclasses import dataclass, field


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
    profile: PhysiologyProfile = field(default_factory=PhysiologyProfile)
    dice_pool: list[int] = field(default_factory=lambda: [6, 6, 6, 6])
    progression_ef: int = 0
    progression_q: int = 0
    progression_spec: int = 0
    fatigue: int = 0
    turns_played: int = 0
    upgrades_used: int = 0
    dice_added: int = 0
    ef_milestones_claimed: set[int] = field(default_factory=set)
    q_milestones_claimed: set[int] = field(default_factory=set)

    def __post_init__(self):
        self.profile.validate()
        if len(self.dice_pool) < 4 or len(self.dice_pool) > 6:
            raise ValueError("dice pool must contain between four and six dice")
        if any(size not in (6, 8, 10, 12) for size in self.dice_pool):
            raise ValueError("dice pool supports only d6, d8, d10 and d12")
        if self.fatigue < 0:
            raise ValueError("fatigue cannot be negative")

    def clone(self):
        """Return an independent state suitable for branching a playtest."""
        return PlayerState(
            profile=PhysiologyProfile(
                self.profile.ef, self.profile.threshold, self.profile.vma
            ),
            dice_pool=list(self.dice_pool),
            progression_ef=self.progression_ef,
            progression_q=self.progression_q,
            progression_spec=self.progression_spec,
            fatigue=self.fatigue,
            turns_played=self.turns_played,
            upgrades_used=self.upgrades_used,
            dice_added=self.dice_added,
            ef_milestones_claimed=set(self.ef_milestones_claimed),
            q_milestones_claimed=set(self.q_milestones_claimed),
        )
