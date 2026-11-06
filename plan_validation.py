"""Pure, structured validation for a CURRENT Training session plan.

This boundary checks legality only. It does not choose sessions, resolve risk,
or define a player-selection policy.
"""

from dataclasses import dataclass

from session_risk import is_risk_tentable
from session_selector import MAX_SESSIONS_PER_TURN, SINGLE_PER_TURN_CATEGORIES
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG


@dataclass(frozen=True)
class PlanViolation:
    """One independently detectable reason a plan is illegal."""

    code: str
    message: str
    session: str | None = None


@dataclass(frozen=True)
class PlanValidation:
    """Immutable result of validating a proposed plan."""

    valid: bool
    violations: tuple[PlanViolation, ...]


def validate_plan(
    planned,
    accessible_session_names,
    energy_budget,
    rpe_max,
    quality_limit,
    best_die_size=None,
) -> PlanValidation:
    """Validate a proposed plan against CURRENT Training constraints.

    ``accessible_session_names`` is the caller's current tentable-session list.
    EF repetitions are legal; quality entries are unique. Risky quality is
    permitted only when a best die size is supplied and the existing CURRENT
    rule says the bust is not certain.
    """
    violations = []
    context_values = (
        ("invalid_energy_budget", energy_budget, "energy_budget must be a non-negative integer", False),
        ("invalid_rpe_max", rpe_max, "rpe_max must be a non-negative integer", False),
        ("invalid_quality_limit", quality_limit, "quality_limit must be a non-negative integer", False),
    )
    for code, value, message, _ in context_values:
        if type(value) is not int or value < 0:
            violations.append(PlanViolation(code, message))
    if best_die_size is not None and (type(best_die_size) is not int or best_die_size <= 0):
        violations.append(PlanViolation(
            "invalid_best_die_size", "best_die_size must be a positive integer when provided"
        ))
    if violations:
        return PlanValidation(False, tuple(violations))

    planned = tuple(planned)
    accessible = set(accessible_session_names)
    if len(planned) > MAX_SESSIONS_PER_TURN:
        violations.append(PlanViolation(
            "session_limit", f"plan exceeds {MAX_SESSIONS_PER_TURN} sessions"
        ))

    energy_used = 0
    ef_count = 0
    quality_count = 0
    quality_names = set()
    single_categories = set()

    for name in planned:
        if not isinstance(name, str) or name not in SESSION_CATALOG:
            violations.append(PlanViolation(
                "unknown_session", "session is not in the catalogue", str(name)
            ))
            continue

        category, cost = SESSION_CATALOG[name]
        energy_used += cost
        if name not in accessible:
            violations.append(PlanViolation(
                "session_not_accessible", "session is not currently accessible", name
            ))

        if category == "EF":
            ef_count += 1
            if cost > rpe_max:
                violations.append(PlanViolation(
                    "ef_above_rpe_max", "EF above RPE Max is unavailable", name
                ))
        elif category in QUALITY_CATEGORIES:
            quality_count += 1
            if name in quality_names:
                violations.append(PlanViolation(
                    "duplicate_quality", "quality entries cannot repeat", name
                ))
            quality_names.add(name)
            if cost > rpe_max:
                if best_die_size is None:
                    violations.append(PlanViolation(
                        "risky_quality_missing_die_size",
                        "best_die_size is required to validate risky quality", name
                    ))
                elif not is_risk_tentable(name, rpe_max, best_die_size):
                    violations.append(PlanViolation(
                        "risky_quality_certain_bust",
                        "risky quality would bust with certainty", name
                    ))

        if category in SINGLE_PER_TURN_CATEGORIES:
            if category in single_categories:
                violations.append(PlanViolation(
                    "single_category_limit",
                    f"only one {category} session is allowed per turn", name
                ))
            single_categories.add(category)

    if energy_used > energy_budget:
        violations.append(PlanViolation("energy_budget", "plan exceeds available energy"))
    if quality_count > quality_limit:
        violations.append(PlanViolation("quality_limit", "plan exceeds the D99 quality limit"))
    if quality_count > ef_count:
        violations.append(PlanViolation(
            "quality_requires_ef", "quality sessions cannot outnumber EF sessions"
        ))

    return PlanValidation(not violations, tuple(violations))
