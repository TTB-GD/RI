"""Player-selected physiological progression at accumulated adaptation milestones.

Milestone thresholds and coordinate increments are supplied as configuration;
this module intentionally defines no numerical balance schedule.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .physiology import CHOICES, TRACKS
from .state import PlayerState


@dataclass(frozen=True)
class PhysiologyMilestone:
    key: str
    track: str
    threshold: int
    speed_gain: float
    energy_reduction: float

    def __post_init__(self):
        if not self.key or self.track not in TRACKS:
            raise ValueError("milestone needs a key and an EF/threshold/VMA track")
        if isinstance(self.threshold, bool) or not isinstance(self.threshold, int) or self.threshold <= 0:
            raise ValueError("milestone threshold must be a positive integer")
        for name, amount in (("speed_gain", self.speed_gain),
                             ("energy_reduction", self.energy_reduction)):
            if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
                raise ValueError(f"{name} must be positive")


@dataclass(frozen=True)
class PhysiologyUpgrade:
    milestone_key: str
    track: str
    choice: str
    amount: float
    profile_before: object
    profile_after: object


def validate_physiology_milestones(
    milestones: Iterable[PhysiologyMilestone],
) -> tuple[PhysiologyMilestone, ...]:
    rows = tuple(milestones)
    keys = [row.key for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("physiology milestone keys must be unique")
    for track in TRACKS:
        thresholds = [row.threshold for row in rows if row.track == track]
        if thresholds != sorted(thresholds) or len(thresholds) != len(set(thresholds)):
            raise ValueError(f"{track} milestone thresholds must be strictly increasing")
    return rows


def apply_physiology_milestones(
    state: PlayerState,
    milestones: Iterable[PhysiologyMilestone],
    choose_upgrade: Callable[[PhysiologyMilestone, tuple[str, ...]], str] | None,
) -> tuple[PhysiologyUpgrade, ...]:
    """Offer each reached milestone; consume XP only after a valid player choice.

    If no choice callback is supplied, XP remains banked and the milestone stays
    pending. This permits a UI to present the choice later without an auto-effect.
    """
    rows = validate_physiology_milestones(milestones)
    if not rows or choose_upgrade is None:
        return ()
    if state.race_curve is None:
        raise ValueError("race_curve must be configured before applying physiology milestones")

    xp_fields = {
        "ef": "progression_ef",
        "threshold": "progression_threshold",
        "vma": "progression_vma",
    }
    upgrades = []
    for track in TRACKS:
        for milestone in (row for row in rows if row.track == track):
            if milestone.key in state.physiology_milestones_claimed:
                continue
            xp_field = xp_fields[track]
            if getattr(state, xp_field) < milestone.threshold:
                break

            choices = state.race_curve.available_choices(
                track,
                speed_gain=milestone.speed_gain,
                energy_reduction=milestone.energy_reduction,
            )
            if not choices:
                # Preserve XP and leave the milestone pending for a later,
                # potentially different curve configuration.
                break
            choice = choose_upgrade(milestone, choices)
            if choice not in choices:
                raise ValueError(
                    f"choice {choice!r} is not available for milestone {milestone.key}"
                )
            amount = milestone.speed_gain if choice == "speed" else milestone.energy_reduction
            before = state.race_curve
            after = before.upgraded(track, choice, amount)
            state.race_curve = after
            setattr(state, xp_field, getattr(state, xp_field) - milestone.threshold)
            state.physiology_milestones_claimed.add(milestone.key)
            upgrades.append(PhysiologyUpgrade(
                milestone.key, track, choice, amount, before, after
            ))
    return tuple(upgrades)
