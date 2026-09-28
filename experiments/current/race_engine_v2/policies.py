"""Deterministic technical probes. These are not official player behaviours."""

from .core import PolicyView, production_cost


def _affordable_continuation(view: PolicyView, production: int, buffer_per_turn: int = 1) -> bool:
    if view.final_reserve is None:
        budget = view.base_reserve + view.freshness_bonus - view.spent
    else:
        budget = view.final_reserve - view.spent
    remaining_turns = view.race_length - view.segment
    future_floor = sum(production_cost(1, difficulty, view.curve)
                       for difficulty in view.remaining_difficulty_profile)
    return production_cost(production, view.current_difficulty, view.curve) + max(
        remaining_turns * buffer_per_turn, future_floor) <= budget


def efficient_policy(view: PolicyView) -> int:
    return max(view.payable, key=lambda p: (p / production_cost(p, view.current_difficulty, view.curve), p))


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
