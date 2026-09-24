"""External, deterministic experimental harness for Fatigue V1.

This module deliberately does not alter production rules.  It reuses the
prototype's dice decision engine, catalogue, progression and current selector,
then applies Fatigue V1 only to copied simulation state.  Run it directly to
write audit CSV/JSON/Markdown artefacts (100 seeds × 16 turns by default).
"""
from __future__ import annotations

import argparse
import copy
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

from decision_engine import choose_weighted_action, energy_and_fatigue
from dice_progression import DEFAULT_UPGRADE_WEIGHTS
from dice_types import make_pool, pool_tn
from game_logger import write_csv
from player_state import Player
from session_effects import session_outcome
from session_selector import (DEFAULT_SESSION_WEIGHTS, _SelectionState, _commit,
                              _is_affordable, _marginal_utility,
                              _prioritize_long_run)
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG
from simulate_player import DEFAULT_WEIGHTS, _split_active_reserve

NORMAL = "normal_realisee"
RISK_SUCCESS = "risque_reussi"
BUST = "risque_annulee_bust"
UNTESTED = "risque_non_testee_apres_bust"


@dataclass
class FatigueState:
    fatigue: int = 0
    suspended_index: int | None = None
    suspension_started_turn: int | None = None
    removed_turns: int = 0


def _pool_label(sizes):
    return "-".join(f"d{s}" for s in sizes)


def _active_indices(player, fatigue):
    """Return permanent die indices currently usable; recovery is boundary based."""
    if fatigue.suspended_index is not None and fatigue.fatigue <= max(player.dice_pool.sizes):
        fatigue.suspended_index = None
        fatigue.suspension_started_turn = None
        return list(range(len(player.dice_pool.sizes))), True
    return [i for i in range(len(player.dice_pool.sizes)) if i != fatigue.suspended_index], False


def _roll(active_sizes, weights):
    """Production dice decision engine, fed only the externally active pool."""
    dice = make_pool(active_sizes)
    active, reserve = _split_active_reserve(dice)
    tn = pool_tn(dice)
    faces, values = [], []
    for die in active:
        face, value = die.roll(); faces.append(face); values.append(value)
    choice, index, _ = choose_weighted_action(active, reserve, faces, len(dice), tn, **weights)
    if choice in ("add", "add+reroll"):
        face, value = reserve.roll(); faces.append(face); values.append(value)
    if choice in ("reroll", "add+reroll"):
        face, value = active[index].roll(); faces[index] = face; values[index] = value
    outcome = session_outcome(faces, values, len(dice))
    return {"energy_budget": outcome["total"], "rpe_max": outcome["rpe_max"], "tn": tn,
            "action": choice, "faces": faces, "values": values}


def choose_sessions_allowing_risk(available, energy, rpe_max, tn, weights=None):
    """POLITIQUE EXPÉRIMENTALE: production greedy order, with only RPE gate removed.

    All existing energy, EF/quality, SL and seven-session constraints remain.
    No risk bonus or global objective is introduced.  The production marginal
    utility is retained and evaluated against the rolled RPE maximum.
    """
    weights = weights or DEFAULT_SESSION_WEIGHTS
    state, trace = _SelectionState(), []
    # Existing SL preamble is retained but temporarily opens the RPE gate only.
    _prioritize_long_run(available, state, energy, max(SESSION_CATALOG[n][1] for n in available), trace)
    while True:
        candidates = [n for n in available
                      if _is_affordable(n, state, energy, max(SESSION_CATALOG[x][1] for x in available))]
        if not candidates:
            break
        scored = sorted(((n, _marginal_utility(n, state, energy, rpe_max, tn, weights)) for n in candidates),
                        key=lambda item: item[1], reverse=True)
        name, utility = scored[0]
        if utility < 0:
            break
        _commit(name, state)
        trace.append({"session": name, "marginal_utility": round(utility, 4), "note": "politique_experimentale"})
    return state.chosen, trace


def resolve_sessions(chosen, rpe_max, best_die, bust_enabled=True):
    """Resolve chosen order and retain the four required mutually exclusive statuses."""
    rows, busted = [], False
    for order, name in enumerate(chosen, 1):
        category, rpe = SESSION_CATALOG[name]
        exceedance = max(0, rpe - rpe_max)
        roll = None
        if exceedance == 0:
            status = NORMAL
        elif busted:
            status = UNTESTED
        elif not bust_enabled:
            # Consume the same draw as V1 so subsequent dice rolls remain
            # aligned until realised work causes a genuine divergence.
            roll = random.randint(1, best_die)
            status = RISK_SUCCESS
        else:
            roll = random.randint(1, best_die)
            status = BUST if roll <= exceedance else RISK_SUCCESS
            busted = status == BUST
        realized = status in (NORMAL, RISK_SUCCESS)
        rows.append({"resolution_order": order, "session": name, "category": category, "rpe": rpe,
                     "exceedance": exceedance, "bust_roll": roll, "status": status, "realized": realized})
    return rows


def _component(spend, tn, q_enabled):
    value = energy_and_fatigue(spend, tn)[1]
    return (max(value, 0) if q_enabled else 0), min(value, 0)


def simulate(seed, turns=16, policy="fixed", bust_enabled=True, q_enabled=True, s_enabled=True):
    """One reproducible trajectory. `policy=fixed` is A; `risk` is B."""
    random.seed(seed)
    player, fatigue = Player(), FatigueState()
    turn_rows, session_rows = [], []
    for turn in range(1, turns + 1):
        # Permanent progression stays independent of the externally reduced active pool.
        player.dice_pool.maybe_add_dice(player.cumulative_ctl)
        player.dice_pool.maybe_upgrade(player.progress.quality_total, DEFAULT_UPGRADE_WEIGHTS)
        active_indices, recovered = _active_indices(player, fatigue)
        permanent = player.dice_pool.sizes.copy()
        active = [permanent[i] for i in active_indices]
        roll = _roll(active, DEFAULT_WEIGHTS)
        available = player.progress.available_sessions()
        if policy == "fixed":
            from session_selector import choose_sessions_weighted
            chosen, _ = choose_sessions_weighted(available, roll["energy_budget"], roll["rpe_max"], roll["tn"])
        elif policy == "risk":
            chosen, _ = choose_sessions_allowing_risk(available, roll["energy_budget"], roll["rpe_max"], roll["tn"])
        else:
            raise ValueError("policy must be 'fixed' or 'risk'")
        accessible_risk = [n for n in available if SESSION_CATALOG[n][1] > roll["rpe_max"]
                           and SESSION_CATALOG[n][1] <= roll["energy_budget"]]
        best_die = max(active)
        resolutions = resolve_sessions(chosen, roll["rpe_max"], best_die, bust_enabled)
        planned = sum(SESSION_CATALOG[n][1] for n in chosen)
        realized_names = [r["session"] for r in resolutions if r["realized"]]
        effective = sum(SESSION_CATALOG[n][1] for n in realized_names)
        potential_s = sum(max(0, SESSION_CATALOG[n][1] - roll["rpe_max"]) for n in chosen)
        actual_s = sum(max(0, SESSION_CATALOG[n][1] - roll["rpe_max"]) for n in realized_names) if s_enabled else 0
        q, recovery = _component(effective, roll["tn"], q_enabled)
        before = fatigue.fatigue
        raw = before + q + actual_s + recovery
        negative_bound = -best_die
        fatigue.fatigue = max(negative_bound, raw)
        threshold = best_die
        overtraining = fatigue.fatigue > threshold
        removed = None
        if overtraining and fatigue.suspended_index is None:
            # Smallest active die; equal sizes prefer latest permanent die, matching production reserve tie-break.
            removed = min(active_indices, key=lambda i: (permanent[i], -i))
            fatigue.suspended_index = removed
            fatigue.suspension_started_turn = turn
        if fatigue.suspended_index is not None:
            fatigue.removed_turns += 1
        next_active = [s for i, s in enumerate(permanent) if i != fatigue.suspended_index]
        row = {"seed": seed, "turn": turn, "policy": policy, "pool_permanent": _pool_label(permanent),
               "pool_active": _pool_label(active), "pool_active_next": _pool_label(next_active),
               "tn": roll["tn"], "rpe_max": roll["rpe_max"], "energy": roll["energy_budget"],
               "spend_planned": planned, "spend_effective": effective, "spend_lost": planned-effective,
               "sessions_chosen": "-".join(chosen), "risk_accessible": "-".join(accessible_risk),
               "q": q, "s_potential": potential_s, "s_effective": actual_s, "recovery": recovery,
               "fatigue_before": before, "fatigue_raw": raw, "negative_bound": negative_bound,
               "fatigue_final": fatigue.fatigue, "best_die": best_die, "overtraining_threshold": threshold,
               "overtraining": overtraining, "die_removed": None if removed is None else f"#{removed}:d{permanent[removed]}",
               "die_suspended": fatigue.suspended_index is not None, "die_recovered": recovered,
               "recovery_boundary_equal": fatigue.fatigue == best_die,
               "recovery_boundary_plus_one": fatigue.fatigue == best_die + 1,
               "ctl": player.cumulative_ctl + effective, "quality_total": player.progress.quality_total,
               "dice_action": roll["action"]}
        for resolution in resolutions:
            session_rows.append({**{"seed": seed, "turn": turn, "policy": policy}, **resolution})
        for name in realized_names:
            player.progress.record_session(name)
        player.cumulative_ctl += effective
        row["quality_total"] = player.progress.quality_total
        row["ctl"] = player.cumulative_ctl
        turn_rows.append(row)
    return turn_rows, session_rows


def _totals(turns, sessions):
    c = Counter(r["status"] for r in sessions)
    return {"turns": len(turns), "sessions_selected": len(sessions), "normal_sessions": c[NORMAL],
            "risk_sessions": c[RISK_SUCCESS] + c[BUST] + c[UNTESTED], "risk_successes": c[RISK_SUCCESS],
            "busts": c[BUST], "risk_untested": c[UNTESTED], "planned_energy": sum(r["spend_planned"] for r in turns),
            "effective_energy": sum(r["spend_effective"] for r in turns), "lost_energy": sum(r["spend_lost"] for r in turns),
            "q": sum(r["q"] for r in turns), "s_potential": sum(r["s_potential"] for r in turns),
            "s_effective": sum(r["s_effective"] for r in turns), "recovery": sum(r["recovery"] for r in turns),
            "overtraining_events": sum(r["overtraining"] for r in turns),
            "suspended_turns": sum(r["die_suspended"] for r in turns), "recoveries": sum(r["die_recovered"] for r in turns),
            "final_fatigue_mean": mean(r["fatigue_final"] for r in turns if r["turn"] == max(t["turn"] for t in turns))}


def run_experiment(seeds=range(100), turns=16):
    """Run A, B, and same-seed counterfactuals for bust/S/Q sensitivity."""
    data, session_data, summaries = {}, {}, {}
    variants = {"A_fixed_v1": ("fixed", True, True, True), "B_risk_v1": ("risk", True, True, True),
                # Sensitivity needs risky choices; A has no RPE exceedance by construction.
                "B_no_bust": ("risk", False, True, True), "B_s_zero": ("risk", True, True, False),
                "B_q_zero": ("risk", True, False, True)}
    for label, args in variants.items():
        rows, sessions = [], []
        for seed in seeds:
            t, s = simulate(seed, turns, *args); rows.extend(t); sessions.extend(s)
        data[label], session_data[label], summaries[label] = rows, sessions, _totals(rows, sessions)
    return data, session_data, summaries


def write_report(output_dir="fatigue_v1_results", seeds=range(100), turns=16):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    data, sessions, summaries = run_experiment(seeds, turns)
    for label in data:
        write_csv(out / f"{label}_turns.csv", data[label])
        write_csv(out / f"{label}_sessions.csv", sessions[label])
    (out / "summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    a, b = summaries["A_fixed_v1"], summaries["B_risk_v1"]
    representative = {
        "sans_overtraining": next((r["seed"] for r in data["B_risk_v1"] if not r["overtraining"]), None),
        "overtraining_bref": next((r["seed"] for r in data["B_risk_v1"] if r["overtraining"]), None),
        "bust_precoce": next((r["seed"] for r in sessions["B_risk_v1"]
                               if r["status"] == BUST and r["turn"] <= 4), None),
    }
    (out / "representative_trajectories.json").write_text(json.dumps(representative, indent=2), encoding="utf-8")
    lines = ["# Fatigue V1 — rapport expérimental", "", "## FAIT", "",
             f"- Protocole : {len(list(seeds))} seeds × {turns} tours, mêmes seeds pour tous les contrefactuels.",
             f"- A : {a['busts']} busts, {a['lost_energy']} énergie annulée, Q={a['q']}, S effectif={a['s_effective']}, {a['overtraining_events']} tours en overtraining.",
             f"- B : {b['busts']} busts, {b['lost_energy']} énergie annulée, Q={b['q']}, S effectif={b['s_effective']}, {b['overtraining_events']} tours en overtraining.",
             "- Sensibilités : `B_no_bust`, `B_s_zero` et `B_q_zero` conservent la politique B et les mêmes seeds.",
             "", "## OBSERVATION", "", "- Les CSV permettent de filtrer les six trajectoires demandées par seed (bust, overtraining, récupération et progression). Les catégories absentes sont `null` dans `representative_trajectories.json`, jamais fabriquées.",
             "- La comparaison A/B est descriptive : B−A est calculable dans `summary.json`; aucune valeur de design n'est attribuée.",
             "", "## INTERPRÉTATION", "", "- Aucune interprétation de balance n'est produite par ce harnais.",
             "", "## QUESTION DE DESIGN", "", "- Les résultats ne constituent pas une décision de modification des règles."]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="External Fatigue V1 experimental harness")
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--turns", type=int, default=16)
    parser.add_argument("--output", default="fatigue_v1_results")
    args = parser.parse_args()
    summary = write_report(args.output, range(args.seeds), args.turns)
    print(json.dumps(summary, indent=2))
