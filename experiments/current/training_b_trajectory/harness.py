"""Deterministic-seed 16-turn trajectories for the experimental Training B engine.

Scenario thresholds and acquisition choices are test fixtures, not balance rules.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from training_v2 import (
    PlayerState, PortfolioMilestone, list_program_options, roll_and_resolve_turn,
    acquire_session,
)
from training_v2.catalog import SESSION_CATALOG, projected_profile


# Deliberately illustrative thresholds. They exist to exercise the unlock loop.
MILESTONES = (
    PortfolioMilestone("ef-option", "ef", 28, ("EF_SOUTENUE",)),
    PortfolioMilestone("threshold-option", "threshold", 8, ("SEUIL_LONG",)),
    PortfolioMilestone("vma-option", "vma", 8, ("INTERVALLES_COURTS",)),
)


def _score(option, focus):
    """Transparent policy heuristic; not a proposed player utility function."""
    adaptations = {"ef": 0, "threshold": 0, "vma": 0}
    fatigue_cost = 0
    for allocation in option.allocations:
        session = SESSION_CATALOG[allocation.session_key]
        for track, amount in session.adaptations:
            adaptations[track] += amount
        fatigue_cost += session.fatigue

    weights = {
        "balanced": {"ef": 1.0, "threshold": 1.0, "vma": 1.0},
        "ef": {"ef": 2.0, "threshold": 0.6, "vma": 0.6},
        "quality": {"ef": 0.6, "threshold": 1.3, "vma": 1.3},
    }[focus]
    # Prefer load balance; this term is a proxy, not the engine's fatigue rule.
    imbalance = max(0, option.quality_energy - option.ef_energy)
    return (
        sum(adaptations[k] * weights[k] for k in adaptations)
        + 0.015 * option.ef_energy
        + 0.005 * option.quality_energy
        - 0.15 * fatigue_cost
        - 0.025 * imbalance
    )


def _acquire_available(state):
    """A deliberately permissive player choice: acquire every newly eligible option."""
    acquired = []
    for key in sorted(state.eligible_session_keys - state.acquired_session_keys):
        acquire_session(state, key)
        acquired.append(key)
    return acquired


def run_trajectory(seed=1, focus="balanced", turns=16):
    if focus not in {"balanced", "ef", "quality"}:
        raise ValueError("focus must be balanced, ef or quality")
    if not 1 <= turns <= 16:
        raise ValueError("turn count must be between 1 and 16")

    rng = random.Random(seed)
    state = PlayerState()
    history = []

    for _ in range(turns):
        acquisitions_before = set(state.acquired_session_keys)

        def choose(roll):
            options = list_program_options(state, roll)
            if not options:
                raise RuntimeError("no feasible program for generated roll")
            return max(
                options,
                key=lambda option: (
                    _score(option, focus),
                    tuple(item.session_key for item in option.allocations),
                ),
            ).allocations

        result = roll_and_resolve_turn(
            state, choose, rng=rng, portfolio_milestones=MILESTONES
        )
        acquired_now = _acquire_available(state)
        history.append({
            "turn": result.turn,
            "raw_faces": list(result.raw_faces),
            "final_values": list(result.final_values),
            "sessions": [item.session_key for item in result.successful_sessions],
            "busted_session": result.busted_session,
            "ef_energy": result.ef_energy,
            "quality_energy": result.quality_energy,
            "fatigue_added": (
                result.fatigue_blackjack + result.fatigue_excess
                + result.fatigue_specific
            ),
            "fatigue_total": result.fatigue_after,
            "profile": {
                "ef": state.profile.ef,
                "threshold": state.profile.threshold,
                "vma": state.profile.vma,
            },
            "progression": {
                "ef": state.progression_ef,
                "threshold": state.progression_threshold,
                "vma": state.progression_vma,
            },
            "newly_eligible": list(result.newly_eligible_sessions),
            "acquired_this_turn": acquired_now,
            "dice_pool": list(state.dice_pool),
        })

    return {
        "seed": seed,
        "focus": focus,
        "turns": turns,
        "final_profile": {
            "ef": state.profile.ef,
            "threshold": state.profile.threshold,
            "vma": state.profile.vma,
        },
        "final_progression": {
            "ef": state.progression_ef,
            "threshold": state.progression_threshold,
            "vma": state.progression_vma,
        },
        "final_fatigue": state.fatigue,
        "dice_pool": list(state.dice_pool),
        "acquired_sessions": sorted(state.acquired_session_keys),
        "history": history,
    }


def run_matrix(seeds=(11, 23, 47), turns=16):
    return [
        run_trajectory(seed=seed, focus=focus, turns=turns)
        for focus in ("balanced", "ef", "quality")
        for seed in seeds
    ]


if __name__ == "__main__":
    print(json.dumps(run_matrix(), indent=2, sort_keys=True))
