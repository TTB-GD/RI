"""RULE / RESOLUTION only for EXP R1-A; policy selection lives elsewhere."""

from dataclasses import dataclass
from itertools import combinations
import random

from .energy import energy_cost
from .fixtures import RESERVE_PARAMETERS, DicePool
from .form import classify_form, form_value, pattern_features, structural_pattern_score


@dataclass(frozen=True)
class ProductionOptions:
    productions: tuple[int, ...]
    compositions: dict[int, tuple[tuple[int, ...], ...]]


@dataclass(frozen=True)
class PolicyView:
    segment: int
    race_length: int
    available: tuple[int, ...]
    payable: tuple[int, ...]
    spent: int
    base_reserve: int
    freshness_bonus: int
    observed_form: int
    final_reserve: int | None
    pool_expected_total: float
    curve: str
    current_difficulty: int = 0
    remaining_difficulty_profile: tuple[int, ...] = ()


def available_productions(roll: tuple[int, ...]) -> ProductionOptions:
    if not roll:
        raise ValueError("roll must be non-empty")
    compositions: dict[int, set[tuple[int, ...]]] = {}
    for count in range(1, len(roll) + 1):
        for indices in combinations(range(len(roll)), count):
            faces = tuple(roll[i] for i in indices)
            compositions.setdefault(sum(faces), set()).add(faces)
    frozen = {p: tuple(sorted(values)) for p, values in compositions.items()}
    return ProductionOptions(tuple(sorted(frozen)), frozen)


def physiological_load(production: int, difficulty: int) -> int:
    if difficulty < 0:
        raise ValueError("difficulty must be non-negative")
    return production + difficulty


def production_cost(production: int, difficulty: int, curve: str) -> int:
    return energy_cost(physiological_load(production, difficulty), curve)


def payable_productions(options: ProductionOptions, remaining: int, curve: str,
                        difficulty: int = 0) -> tuple[int, ...]:
    return tuple(p for p in options.productions if production_cost(p, difficulty, curve) <= remaining)


def base_reserve_from_ctl(ctl: int, race_length: int) -> int:
    if ctl < 0 or race_length <= 0:
        raise ValueError("ctl must be non-negative and length positive")
    cfg = RESERVE_PARAMETERS
    return race_length * cfg["per_segment"] + (ctl // cfg["ctl_step"]) * cfg["reserve_per_step"]


def generate_rolls(seed: int, pool: DicePool, race_length: int) -> tuple[tuple[int, ...], ...]:
    rng = random.Random(seed)
    return tuple(tuple(rng.randint(1, size) for size in pool.dice) for _ in range(race_length))


def run_race(*, seed: int, pool: DicePool, race_length: int, curve: str, policy,
             ctl: int, freshness_bonus: int, long_run_preparation: bool,
             form_mode: str = "SUM", difficulty_profile: tuple[int, ...] | None = None,
             profile_name: str = "D0_FLAT") -> dict:
    difficulty_profile = difficulty_profile or (0,) * race_length
    if len(difficulty_profile) != race_length or any(value < 0 for value in difficulty_profile):
        raise ValueError("difficulty profile must contain one non-negative value per segment")
    rolls = generate_rolls(seed, pool, race_length)
    base = base_reserve_from_ctl(ctl, race_length)
    signals: list[str] = []
    form_values: list[int] = []
    turns: list[dict] = []
    spent = 0
    final_reserve = None
    raw_final_reserve = None
    clamped = False
    dnf_turn = None

    for segment, roll in enumerate(rolls, start=1):
        difficulty = difficulty_profile[segment - 1]
        if segment <= 3:
            signal = classify_form(roll, pool, form_mode)
            signals.append(signal)
            form_values.append(form_value(signal, long_run_preparation))
            if segment == 3:
                raw_final_reserve = base + freshness_bonus + sum(form_values)

        options = available_productions(roll)
        # The first three commitments are never undone. At segment 3 the raw
        # final reserve is visible, but the post-choice floor is applied after it.
        remaining = None if final_reserve is None else final_reserve - spent
        payable = options.productions if remaining is None else payable_productions(options, remaining, curve, difficulty)
        if not payable:
            dnf_turn = segment
            break

        view = PolicyView(
            segment=segment, race_length=race_length, available=options.productions,
            payable=payable, spent=spent, base_reserve=base,
            freshness_bonus=freshness_bonus, observed_form=sum(form_values),
            final_reserve=raw_final_reserve if segment == 3 else final_reserve,
            pool_expected_total=pool.expected_total, curve=curve,
            current_difficulty=difficulty,
            remaining_difficulty_profile=difficulty_profile[segment:],
        )
        chosen = policy(view)
        if chosen not in payable:
            raise ValueError(f"policy selected illegal production {chosen}")
        load = physiological_load(chosen, difficulty)
        cost = production_cost(chosen, difficulty, curve)
        spent += cost
        if segment == 3:
            assert raw_final_reserve is not None
            final_reserve = max(raw_final_reserve, spent)
            clamped = final_reserve != raw_final_reserve
        features = pattern_features(roll)
        turns.append({
            "segment": segment, "roll": roll,
            "current_difficulty": difficulty,
            "remaining_difficulty_profile": difficulty_profile[segment:],
            "physiological_load": load,
            "raw_roll_sum": sum(roll), "max_available_production": max(options.productions),
            "structural_pattern_score": structural_pattern_score(roll, pool),
            "pattern_features": features,
            "signal": signals[-1] if segment <= 3 else None,
            "form_value": form_values[-1] if segment <= 3 else None,
            "form_cumulative": sum(form_values), "available": options.productions,
            "payable": payable, "choice": chosen, "cost": cost,
            "terrain_extra_cost": cost - energy_cost(chosen, curve),
            "spent": spent,
            "reserve_remaining": None if final_reserve is None else final_reserve - spent,
        })

    return {
        "seed": seed, "pool": pool.name, "length": race_length, "curve": curve,
        "form_mode": form_mode,
        "profile": profile_name, "difficulty_profile": difficulty_profile,
        "policy": policy.__name__.replace("_policy", "").upper(),
        "long_run_preparation": long_run_preparation, "freshness_bonus": freshness_bonus,
        "ctl": ctl, "base_reserve": base, "signals": tuple(signals),
        "form_values": tuple(form_values), "form_adjustment": sum(form_values),
        "raw_final_reserve": raw_final_reserve, "final_reserve": final_reserve,
        "reserve_floor_clamped": clamped, "spent": spent,
        "reserve_remaining": None if final_reserve is None else final_reserve - spent,
        "score": sum(t["choice"] for t in turns), "dnf": dnf_turn is not None,
        "dnf_turn": dnf_turn, "rolls": rolls, "turns": turns,
    }
