"""Deterministic technical probes. These are not official player behaviours."""

from race_v2 import is_production_physiologically_legal

from .core import PolicyView, production_cost


def _cost_source(view: PolicyView):
    source = view.physiology_profile or view.curve
    if source is None:
        raise ValueError("policy view has no cost source")
    return source


def _normalized_cost(view: PolicyView, production: int, difficulty: int) -> float:
    return production_cost(production, difficulty, _cost_source(view)) / view.physiology_cost_divisor


def _affordable_continuation(view: PolicyView, production: int, buffer_per_turn: int = 1) -> bool:
    if view.final_reserve is None:
        budget = view.base_reserve + view.freshness_bonus - view.spent
    else:
        budget = view.final_reserve - view.spent
    remaining_turns = view.race_length - view.segment
    if view.physiology_profile is not None and any(
        not is_production_physiologically_legal(view.physiology_profile, 1, difficulty)
        for difficulty in view.remaining_difficulty_profile
    ):
        return False
    future_floor = sum(_normalized_cost(view, 1, difficulty)
                       for difficulty in view.remaining_difficulty_profile)
    return _normalized_cost(view, production, view.current_difficulty) + max(
        remaining_turns * buffer_per_turn, future_floor
    ) <= budget


def efficient_policy(view: PolicyView) -> int:
    return max(view.payable, key=lambda p: (p / _normalized_cost(view, p, view.current_difficulty), p))


def aggressive_policy(view: PolicyView) -> int:
    sustainable = [p for p in view.payable if _affordable_continuation(view, p)]
    return max(sustainable or view.payable)


def adaptive_policy(view: PolicyView) -> int:
    options = view.payable
    if view.segment < 3:
        target = view.pool_expected_total * (0.72 + 0.04 * view.observed_form)
    elif view.final_reserve is None:
        target = view.pool_expected_total * 0.75
    else:
        turns_left_including_now = view.race_length - view.segment + 1
        margin_per_turn = max(0.0, (view.final_reserve - view.spent) / turns_left_including_now)
        target = view.pool_expected_total * (0.62 + min(0.30, margin_per_turn * 0.06))
    if view.current_difficulty or any(view.remaining_difficulty_profile):
        sustainable = [p for p in options if _affordable_continuation(view, p)]
        options = tuple(sustainable) or options
    return min(options, key=lambda p: (abs(p - target), -p))


def greedy_policy(view: PolicyView) -> int:
    return max(view.payable)


POLICIES = {
    "EFFICIENT": efficient_policy,
    "AGGRESSIVE": aggressive_policy,
    "ADAPTIVE": adaptive_policy,
    "GREEDY": greedy_policy,
}
