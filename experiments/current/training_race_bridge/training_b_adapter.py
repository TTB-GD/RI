"""Direct state adapter from the Training B engine to Race V2.

The adapter performs structural conversion only. It does not invent mappings
for CTL, freshness, long-run preparation, or physiological calibration.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from physiology import PhysiologyProfile as RacePhysiologyProfile
from experiments.current.race_engine_v2.core import run_race
from experiments.current.race_engine_v2.fixtures import DicePool


SUPPORTED_DIE_SIZES = (6, 8, 10, 12)


def _read(source, key):
    if isinstance(source, Mapping):
        return source[key]
    return getattr(source, key)


def race_profile_from_training(training_profile):
    """Copy Training B's EF/Seuil/VMA landmarks without rescaling them."""
    profile = RacePhysiologyProfile(
        ef=int(_read(training_profile, "ef")),
        threshold=int(_read(training_profile, "threshold")),
        vma=int(_read(training_profile, "vma")),
    )
    return profile


def race_pool_from_training(dice_pool):
    """Convert the persistent Training B die sizes into Race V2's DicePool."""
    dice = tuple(int(size) for size in dice_pool)
    if not 4 <= len(dice) <= 6:
        raise ValueError("Training B race pool must contain four to six dice")
    if any(size not in SUPPORTED_DIE_SIZES for size in dice):
        raise ValueError("Training B race pool contains an unsupported die size")
    counts = Counter(dice)
    name = "+".join(
        f"{counts[size]}d{size}" for size in sorted(counts, reverse=True)
    )
    return DicePool(
        name=name,
        dice=dice,
        provenance="Converted directly from a Training B persistent dice pool",
    )


def race_inputs_from_training(training_state):
    """Convert a PlayerState or a trajectory snapshot into Race V2 inputs."""
    profile = _read(training_state, "profile")
    dice_pool = _read(training_state, "dice_pool")
    if isinstance(profile, Mapping) and set(("ef", "threshold", "vma")) <= profile.keys():
        race_profile = race_profile_from_training(profile)
    else:
        race_profile = race_profile_from_training(profile)
    return {
        "physiology_profile": race_profile,
        "pool": race_pool_from_training(dice_pool),
    }


def run_training_race(
    training_state,
    *,
    seed: int,
    race_length: int,
    policy,
    ctl: int,
    freshness_bonus: int,
    long_run_preparation: bool,
    difficulty_profile=None,
    profile_name="TRAINING_B",
):
    """Run Race V2 from a completed Training B state.

    CTL, freshness and long-run preparation remain explicit Race V2 inputs:
    Training B does not yet define conversion rules for them.
    """
    converted = race_inputs_from_training(training_state)
    return run_race(
        seed=seed,
        pool=converted["pool"],
        race_length=race_length,
        policy=policy,
        ctl=ctl,
        freshness_bonus=freshness_bonus,
        long_run_preparation=long_run_preparation,
        difficulty_profile=difficulty_profile,
        profile_name=profile_name,
        physiology_profile=converted["physiology_profile"],
    )
