"""Treize états déterministes ciblant D99, répétition, limite 7 et bust."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from session_resolution import resolve_session_plan
from session_selector import choose_sessions_weighted
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG


WEIGHTS = {"w_energy": 3.0, "w_sessions": 10.0, "w_fatigue": 0.0, "w_rpe": 0.25}
AVAILABLE = list(SESSION_CATALOG)


def summarize(identifier, d99, planned, resolution, energy_available, bust=None):
    qualities = [n for n in resolution.completed_sessions if SESSION_CATALOG[n][0] in QUALITY_CATEGORIES]
    ef_count = sum(SESSION_CATALOG[n][0] == "EF" for n in resolution.completed_sessions)
    effective = [f"{n}(bust)" if i == bust else n for i, n in enumerate(planned)]
    if bust is not None:
        effective = [n for n in effective if n.replace("(bust)", "") not in resolution.cancelled_sessions]
        effective += list(resolution.replacement_sessions)
    return {
        "state": identifier,
        "d99": d99,
        "planned": list(planned),
        "bust": "no" if bust is None else f"yes:{planned[bust]}",
        "effective": effective,
        "ef": ef_count,
        "qualities": qualities,
        "sl": any(SESSION_CATALOG[n][0] == "SL" for n in resolution.completed_sessions),
        "energy_available": energy_available,
        "energy_effective": resolution.energy_effective,
        "energy_lost": resolution.energy_lost,
        "ctl_effective": resolution.energy_effective,
        "counted_sessions": len(resolution.counted_sessions),
        "stop_reason": resolution.stop_reason,
    }


def selected(identifier, d99, names, energy, reason, rpe=9):
    planned, _ = choose_sessions_weighted(names, energy, rpe, 20, d99, weights=WEIGHTS)
    row = summarize(identifier, d99, planned, resolve_session_plan(planned, names, rpe), energy)
    row["stop_reason"] = reason
    return row


def busted(identifier, d99, planned, bust, rpe=4):
    energy = sum(SESSION_CATALOG[n][1] for n in planned)
    result = resolve_session_plan(planned, AVAILABLE, rpe, bust)
    return summarize(identifier, d99, planned, result, energy, bust)


def scenarios():
    return [
        selected("D0", 0, ["EF1", "Seuil3"], 10, "d99_limit"),
        selected("D1", 1, ["EF1", "Seuil3", "VMA3"], 20, "d99_limit"),
        selected("D-CAP", 2, ["EF1", "Seuil3", "VMA3", "Force3"], 30, "d99_limit"),
        selected("D-SL", 1, ["EF1", "Seuil3", "SL5"], 20, "d99_limit"),
        selected("R-EF", 0, ["EF1"], 20, "seven_session_limit", 1),
        selected("R-QUAL", 3, ["EF1", "Seuil3"], 20, "quality_entry_uniqueness"),
        selected("R-DIFF", 2, ["EF1", "Seuil3", "VMA3"], 20, "d99_limit"),
        selected("L7", 0, ["EF1"], 20, "seven_session_limit", 1),
        selected("L6", 0, ["EF5"], 31, "energy_budget", 5),
        busted("B-ONE", 1, ["EF4", "Seuil5"], 1),
        busted("B-FIRST", 2, ["EF1", "Seuil5", "EF1", "VMA5"], 1),
        busted("B-MULTI", 3, ["EF1", "EF1", "EF1", "Seuil5", "VMA5", "Force5"], 3),
        busted("B-SLOTS", 3, ["EF1", "EF1", "EF1", "Seuil5", "Spec9", "SL9"], 3),
    ]


if __name__ == "__main__":
    import json

    print(json.dumps(scenarios(), ensure_ascii=False, indent=2))
