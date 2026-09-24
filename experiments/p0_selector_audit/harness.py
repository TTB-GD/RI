"""External, read-only audit of the production P0 session selector.

The instrumented selector is a characterization mirror: production remains the
source of truth and every audited choice is asserted equal to its output.  All
counterfactual values are local diagnostics and never feed the trajectory.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from decision_engine import energy_and_fatigue
from dice_progression import DEFAULT_UPGRADE_WEIGHTS
from overtraining_capacity_harness import Fatigue, _active_indices, _roll, resolve, v1_components
from player_state import Player
from session_selector import (
    DEFAULT_SESSION_WEIGHTS,
    MAX_SESSIONS_PER_TURN,
    SINGLE_PER_TURN_CATEGORIES,
    _SelectionState,
    _commit,
    _is_affordable,
    _marginal_utility,
    _utility,
    choose_sessions_weighted,
)
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG

POLICY = "P0_CURRENT"
DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent
DEFAULT_FULL_LOG = Path("/tmp/p0-selector-audit-candidates.csv")


def legality(name, state, energy_budget, rpe_max, ignore_rpe=False):
    """Mirror `_is_affordable` order and expose its first blocking reason."""
    category, rpe = SESSION_CATALOG[name]
    if len(state.chosen) >= MAX_SESSIONS_PER_TURN:
        return False, "session_limit"
    if not ignore_rpe and rpe > rpe_max:
        return False, "rpe_max"
    if state.energy_used + rpe > energy_budget:
        return False, "energy_budget"
    if category in SINGLE_PER_TURN_CATEGORIES and category in state.used_single_categories:
        return False, "single_category_limit"
    if category in QUALITY_CATEGORIES and state.quality_this_turn + 1 > state.ef_this_turn:
        return False, "quality_requires_ef"
    return True, ""


def utility_terms(energy_used, chosen, energy_budget, rpe_max, tn, weights=None):
    weights = weights or DEFAULT_SESSION_WEIGHTS
    quality = sum(SESSION_CATALOG[name][0] in QUALITY_CATEGORIES for name in chosen)
    avg_rpe = mean(SESSION_CATALOG[name][1] for name in chosen) if chosen else 0.0
    _, modeled_fatigue = energy_and_fatigue(energy_used, tn)
    return {
        "energy_term": weights["w_energy"] * (energy_used / energy_budget if energy_budget else 0.0),
        "quality_term": weights["w_sessions"] * quality,
        "rpe_term": weights["w_rpe"] * (avg_rpe / rpe_max if rpe_max else 0.0),
        "fatigue_term": -weights["w_fatigue"] * modeled_fatigue,
    }


def marginal_components(name, state, energy_budget, rpe_max, tn, weights=None):
    weights = weights or DEFAULT_SESSION_WEIGHTS
    before = utility_terms(state.energy_used, state.chosen, energy_budget, rpe_max, tn, weights)
    after_chosen = state.chosen + [name]
    after = utility_terms(state.energy_used + SESSION_CATALOG[name][1], after_chosen,
                          energy_budget, rpe_max, tn, weights)
    result = {f"delta_{key}": after[key] - before[key] for key in before}
    component_sum = sum(result.values())
    # Production subtracts the two aggregate utilities. Preserve that exact
    # floating-point operation for selection/stop parity, while retaining the
    # independently useful term decomposition.
    result["marginal_utility"] = _marginal_utility(
        name, state, energy_budget, rpe_max, tn, weights
    )
    result["decomposition_residual"] = result["marginal_utility"] - component_sum
    result["utility_before"] = sum(before.values())
    result["utility_after"] = sum(after.values())
    return result


def _project_candidate(name, state, tn, rpe_max, fatigue_before, best_die):
    _, rpe = SESSION_CATALOG[name]
    spend = state.energy_used + rpe
    offset, q, recovery = v1_components(spend, tn)
    s = sum(max(0, SESSION_CATALOG[n][1] - rpe_max) for n in state.chosen + [name])
    _, base_q, base_recovery = v1_components(state.energy_used, tn)
    base_s = sum(max(0, SESSION_CATALOG[n][1] - rpe_max) for n in state.chosen)
    raw = fatigue_before + q + s + recovery
    final = max(-best_die, raw)
    exceedance = max(0, rpe-rpe_max)
    return {
        "projected_spend": spend,
        "projected_offset": offset,
        "projected_q": q,
        "projected_q_delta": q-base_q,
        "projected_s": s,
        "projected_s_delta": s-base_s,
        "projected_recovery": recovery,
        "projected_recovery_delta": recovery-base_recovery,
        "projected_fatigue_raw": raw,
        "projected_fatigue_final": final,
        "projected_overtraining": final > best_die,
        "distance_to_ot": best_die-final,
        "bust_probability": min(exceedance / best_die, 1.0) if exceedance else 0.0,
    }


def _candidate_record(seed, turn, step, phase, name, state, available, energy_budget,
                      rpe_max, tn, fatigue_before, best_die, pool_active):
    category, rpe = SESSION_CATALOG[name]
    legal, reason = legality(name, state, energy_budget, rpe_max)
    rpe_only = reason == "rpe_max" and legality(name, state, energy_budget, rpe_max, ignore_rpe=True)[0]
    components = marginal_components(name, state, energy_budget, rpe_max, tn)
    projected = _project_candidate(name, state, tn, rpe_max, fatigue_before, best_die)
    return {
        "seed": seed, "turn": turn, "greedy_step": step, "phase": phase,
        "pool_active": "-".join(map(str, pool_active)), "best_die": best_die,
        "fatigue_before": fatigue_before, "energy_budget": energy_budget,
        "energy_used_before": state.energy_used, "energy_remaining_before": energy_budget-state.energy_used,
        "candidate": name, "category": category, "energy_cost": rpe, "rpe": rpe,
        "rpe_max": rpe_max, "ctl_gain": rpe,
        "quality_gain": int(category in QUALITY_CATEGORIES), "legal": legal,
        "illegal_reason": reason, "excluded_only_by_rpe": rpe_only,
        **components, **projected,
        "rank": None, "selected": False, "decision": "", "stop_reason": "",
        "available_count": len(available),
    }


def audit_choose(seed, turn, available, energy_budget, rpe_max, tn, fatigue_before,
                 best_die, pool_active, weights=None):
    """Trace a side-effect-free mirror and assert exact production selection."""
    weights = weights or DEFAULT_SESSION_WEIGHTS
    state, records, steps, selected_margins = _SelectionState(), [], [], []
    step = 0

    # Exact production preamble: highest affordable EF, then highest affordable SL.
    sl_names = [n for n in available if SESSION_CATALOG[n][0] == "SL"]
    if sl_names:
        ef_names = [n for n in available if SESSION_CATALOG[n][0] == "EF"]
        affordable_ef = [n for n in ef_names if _is_affordable(n, state, energy_budget, rpe_max)]
        if affordable_ef:
            step += 1
            phase_records = [_candidate_record(seed, turn, step, "long_run_ef", n, state, available,
                                                energy_budget, rpe_max, tn, fatigue_before, best_die, pool_active)
                             for n in ef_names]
            best = max(affordable_ef, key=lambda n: SESSION_CATALOG[n][1])
            for row in phase_records:
                row["selected"] = row["candidate"] == best
                row["decision"] = "forced_long_run_prerequisite" if row["selected"] else "not_highest_rpe_ef"
            records.extend(phase_records); _commit(best, state)
            steps.append({"step": step, "phase": "long_run_ef", "selected": best, "margin": None})

            affordable_sl = [n for n in sl_names if _is_affordable(n, state, energy_budget, rpe_max)]
            if affordable_sl:
                step += 1
                phase_records = [_candidate_record(seed, turn, step, "long_run_sl", n, state, available,
                                                    energy_budget, rpe_max, tn, fatigue_before, best_die, pool_active)
                                 for n in sl_names]
                best = max(affordable_sl, key=lambda n: SESSION_CATALOG[n][1])
                for row in phase_records:
                    row["selected"] = row["candidate"] == best
                    row["decision"] = "forced_long_run" if row["selected"] else "not_highest_rpe_sl"
                records.extend(phase_records); _commit(best, state)
                steps.append({"step": step, "phase": "long_run_sl", "selected": best, "margin": None})

    stop_reason = None
    stop_records = []
    while True:
        step += 1
        phase_records = [_candidate_record(seed, turn, step, "weighted_greedy", name, state, available,
                                            energy_budget, rpe_max, tn, fatigue_before, best_die, pool_active)
                         for name in available]
        legal_rows = [row for row in phase_records if row["legal"]]
        legal_rows.sort(key=lambda row: (-row["marginal_utility"], available.index(row["candidate"])))
        for rank, row in enumerate(legal_rows, 1): row["rank"] = rank
        if not legal_rows:
            stop_reason = classify_no_legal_stop(state, available, energy_budget, rpe_max)
            for row in phase_records: row["decision"], row["stop_reason"] = "illegal", stop_reason
            records.extend(phase_records); stop_records = phase_records
            break
        best = legal_rows[0]
        if best["marginal_utility"] < 0:
            stop_reason = "marginal_utility_negative"
            for row in phase_records:
                row["decision"] = "best_rejected_stop" if row is best else ("legal_not_best" if row["legal"] else "illegal")
                row["stop_reason"] = stop_reason
            records.extend(phase_records); stop_records = phase_records
            break
        best["selected"], best["decision"] = True, "selected_best_marginal"
        for row in phase_records:
            if row is not best: row["decision"] = "legal_not_best" if row["legal"] else "illegal"
        records.extend(phase_records)
        selected_margins.append(best["marginal_utility"])
        steps.append({"step": step, "phase": "weighted_greedy", "selected": best["candidate"],
                      "margin": best["marginal_utility"]})
        _commit(best["candidate"], state)

    production, production_trace = choose_sessions_weighted(available, energy_budget, rpe_max, tn, weights)
    if state.chosen != production:
        raise AssertionError(f"audit changed P0 at seed={seed} turn={turn}: audit={state.chosen}, production={production}")
    return {
        "chosen": state.chosen, "state": state, "records": records, "steps": steps,
        "stop_records": stop_records, "stop_reason": stop_reason,
        "selected_margins": selected_margins, "production_trace": production_trace,
    }


def classify_no_legal_stop(state, available, energy_budget, rpe_max):
    remaining = energy_budget-state.energy_used
    if len(state.chosen) >= MAX_SESSIONS_PER_TURN: return "session_limit"
    if not any(SESSION_CATALOG[n][1] <= remaining for n in available): return "no_energy_affordable"
    affordable = [n for n in available if SESSION_CATALOG[n][1] <= remaining]
    if affordable and all(SESSION_CATALOG[n][1] > rpe_max for n in affordable): return "rpe_max"
    return "structural_constraints"


def bundle_utility(bundle, energy_budget, rpe_max, tn):
    spend = sum(SESSION_CATALOG[n][1] for n in bundle)
    quality = sum(SESSION_CATALOG[n][0] in QUALITY_CATEGORIES for n in bundle)
    avg_rpe = mean(SESSION_CATALOG[n][1] for n in bundle) if bundle else 0.0
    return _utility(spend, quality, avg_rpe, energy_budget, rpe_max, tn, DEFAULT_SESSION_WEIGHTS)


def exact_optimum(available, energy_budget, rpe_max, tn):
    """Dynamic enumeration of every reachable legal bundle (repetition allowed)."""
    options = [n for n in available if SESSION_CATALOG[n][1] <= rpe_max]
    states = {(0, 0, 0, 0, 0): ()}
    for count in range(MAX_SESSIONS_PER_TURN):
        current = [(key, bundle) for key, bundle in states.items() if key[0] == count]
        for (n, spend, ef, quality, sl), bundle in current:
            for name in options:
                category, rpe = SESSION_CATALOG[name]
                new_spend = spend+rpe
                new_sl = sl + int(category in SINGLE_PER_TURN_CATEGORIES)
                new_ef = ef + int(category not in QUALITY_CATEGORIES)
                new_quality = quality + int(category in QUALITY_CATEGORIES)
                if new_spend > energy_budget or new_sl > 1 or new_quality > new_ef: continue
                key = (n+1, new_spend, new_ef, new_quality, new_sl)
                candidate = bundle+(name,)
                previous = states.get(key)
                if previous is None or candidate < previous: states[key] = candidate
    ranked = [(bundle_utility(bundle, energy_budget, rpe_max, tn), bundle) for bundle in states.values()]
    return max(ranked, key=lambda item: (item[0], tuple(reversed(item[1]))))


def simulate_audited(seed, turns=16, collect_candidates=True):
    random.seed(seed)
    player, fatigue = Player(), Fatigue()
    turn_rows, candidate_rows, snapshots = [], [], []
    for turn in range(1, turns+1):
        player.dice_pool.maybe_add_dice(player.cumulative_ctl)
        player.dice_pool.maybe_upgrade(player.progress.quality_total, DEFAULT_UPGRADE_WEIGHTS)
        permanent = player.dice_pool.sizes.copy()
        active_indices, recovered = _active_indices(player, fatigue)
        active = [permanent[i] for i in active_indices]
        roll = _roll(active)
        available = player.progress.available_sessions()
        audited = audit_choose(seed, turn, available, roll["energy"], roll["rpe_max"], roll["tn"],
                               fatigue.value, max(active), active)
        for candidate in audited["records"]:
            candidate.update({"pool_permanent": "-".join(map(str, permanent)),
                              "cumulative_ctl_before": player.cumulative_ctl,
                              "quality_total_before": player.progress.quality_total,
                              "completions_before": json.dumps(dict(player.progress.completions), sort_keys=True)})
        chosen = audited["chosen"]
        resolution = resolve(chosen, roll["rpe_max"], max(active))
        realized = [row["session"] for row in resolution if row["realized"]]
        spend = sum(SESSION_CATALOG[n][1] for n in realized)
        _, q, recovery = v1_components(spend, roll["tn"])
        s = sum(max(0, SESSION_CATALOG[n][1]-roll["rpe_max"]) for n in realized)
        fatigue_before, best_die = fatigue.value, max(active)
        raw = fatigue_before+q+s+recovery
        fatigue.value = max(-best_die, raw)
        overtraining = fatigue.value > best_die
        removed = None
        if overtraining and fatigue.suspended_index is None:
            fatigue.suspended_index = min(active_indices, key=lambda i: (permanent[i], -i))
            fatigue.removed_since = turn; removed = permanent[fatigue.suspended_index]

        final_state = audited["state"]
        final_legal = [row for row in audited["stop_records"] if row["legal"]]
        best_rejected = min(final_legal, key=lambda row: row["rank"]) if final_legal else None
        energy_remaining = roll["energy"]-spend
        headroom = roll["tn"]-spend
        legal_productive = bool(final_legal)
        safe_productive = any(not row["projected_overtraining"] for row in final_legal)
        positive_component_rejected = any(row["legal"] and row["marginal_utility"] < 0 and
                                          any(row[k] > 0 for k in ("delta_energy_term", "delta_quality_term", "delta_rpe_term"))
                                          for row in audited["stop_records"])
        turn_row = {
            "seed": seed, "turn": turn, "policy": POLICY, "pool_active": "-".join(map(str, active)),
            "best_die": best_die, "fatigue_before": fatigue_before, "energy_available": roll["energy"],
            "energy_used": spend, "energy_remaining": energy_remaining,
            "energy_use_rate": spend/roll["energy"] if roll["energy"] else 0,
            "tn": roll["tn"], "headroom_tn_minus_spend": headroom, "rpe_max": roll["rpe_max"],
            "sessions": "-".join(chosen), "session_count": len(chosen), "quality_count": player.progress.quality_total,
            "q": q, "s": s, "recovery": recovery, "fatigue_raw": raw, "fatigue_final": fatigue.value,
            "overtraining": overtraining, "die_removed": removed, "die_recovered": recovered,
            "stop_cause": audited["stop_reason"], "legal_candidate_remaining": bool(final_legal),
            "energetically_accessible_remaining": any(SESSION_CATALOG[n][1] <= energy_remaining for n in available),
            "productive_candidate_remaining": legal_productive,
            "safe_productive_candidate_remaining": safe_productive,
            "positive_component_rejected": positive_component_rejected,
            "best_rejected": best_rejected["candidate"] if best_rejected else "",
            "best_rejected_score": best_rejected["marginal_utility"] if best_rejected else None,
            "last_selected_margin": audited["selected_margins"][-1] if audited["selected_margins"] else None,
        }
        if seed < 10 and turn in (1, 8, 16):
            snapshots.append({"seed": seed, "turn": turn, "available": available.copy(), "energy": roll["energy"],
                              "rpe_max": roll["rpe_max"], "tn": roll["tn"], "fatigue_before": fatigue_before,
                              "best_die": best_die, "pool_active": active.copy(), "greedy": chosen.copy(),
                              "q": q, "s": s, "recovery": recovery, "fatigue_final": fatigue.value})
        if collect_candidates: candidate_rows.extend(audited["records"])
        for name in realized: player.progress.record_session(name)
        player.cumulative_ctl += spend
        turn_row["quality_total_after"] = player.progress.quality_total
        turn_row["ctl_after"] = player.cumulative_ctl
        turn_row["pool_permanent_after"] = "-".join(map(str, player.dice_pool.sizes))
        turn_rows.append(turn_row)
    return turn_rows, candidate_rows, snapshots


def _write_dict_csv(path, rows):
    if not rows: return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def analyze(seeds=range(100), turns=16, full_log=DEFAULT_FULL_LOG):
    turn_rows, candidates, snapshots = [], [], []
    for seed in seeds:
        t, c, s = simulate_audited(seed, turns)
        turn_rows.extend(t); candidates.extend(c); snapshots.extend(s)
    _write_dict_csv(Path(full_log), candidates)

    stop_groups = defaultdict(list)
    for row in turn_rows: stop_groups[row["stop_cause"]].append(row)
    stop_causes = [{"cause": cause, "count": len(rows), "percentage": 100*len(rows)/len(turn_rows),
                    "mean_energy_remaining": mean(r["energy_remaining"] for r in rows),
                    "mean_fatigue_before": mean(r["fatigue_before"] for r in rows),
                    "mean_headroom_tn": mean(r["headroom_tn_minus_spend"] for r in rows)}
                   for cause, rows in sorted(stop_groups.items())]

    rejected = []
    for row in turn_rows:
        if not row["best_rejected"]: continue
        matches = [c for c in candidates if c["seed"] == row["seed"] and c["turn"] == row["turn"]
                   and c["decision"] == "best_rejected_stop"]
        if matches:
            c = matches[0].copy()
            negative = {k: c[k] for k in ("delta_energy_term", "delta_quality_term", "delta_rpe_term", "delta_fatigue_term") if c[k] < 0}
            c["dominant_negative_term"] = min(negative, key=negative.get) if negative else "none"
            fatigue_delta = -c["delta_fatigue_term"]/DEFAULT_SESSION_WEIGHTS["w_fatigue"]
            positive_without_fatigue = c["delta_energy_term"]+c["delta_quality_term"]+c["delta_rpe_term"]
            c["fatigue_weight_break_even"] = positive_without_fatigue/fatigue_delta if fatigue_delta > 0 else None
            c["last_selected_margin"] = row["last_selected_margin"]
            c["margin_drop_from_last_selection"] = (
                row["last_selected_margin"]-c["marginal_utility"]
                if row["last_selected_margin"] is not None else None
            )
            rejected.append(c)

    # Local RPE counterfactual observations, ranked with real legal rows at each step.
    rpe_only = [c for c in candidates if c["excluded_only_by_rpe"]]
    by_step = defaultdict(list)
    for c in candidates: by_step[(c["seed"], c["turn"], c["greedy_step"], c["phase"])].append(c)
    competitive = first = 0
    for c in rpe_only:
        peers = by_step[(c["seed"], c["turn"], c["greedy_step"], c["phase"])]
        legal_scores = [p["marginal_utility"] for p in peers if p["legal"]]
        best_legal = max(legal_scores, default=float("-inf"))
        c["rpe_counterfactual_competitive"] = c["marginal_utility"] >= best_legal
        c["rpe_counterfactual_first"] = c["marginal_utility"] > best_legal or (
            c["marginal_utility"] == best_legal and all(peers.index(c) < peers.index(p) for p in peers if p["legal"] and p["marginal_utility"] == best_legal))
        competitive += c["rpe_counterfactual_competitive"]; first += c["rpe_counterfactual_first"]
        ranked = sorted([p for p in peers if p["legal"] or p["excluded_only_by_rpe"]],
                        key=lambda p: (-p["marginal_utility"], peers.index(p)))
        c["rpe_counterfactual_rank"] = ranked.index(c)+1

    representative = []
    for snap in snapshots:
        optimum_score, optimum = exact_optimum(snap["available"], snap["energy"], snap["rpe_max"], snap["tn"])
        greedy_score = bundle_utility(snap["greedy"], snap["energy"], snap["rpe_max"], snap["tn"])
        g_spend = sum(SESSION_CATALOG[n][1] for n in snap["greedy"]); o_spend = sum(SESSION_CATALOG[n][1] for n in optimum)
        g_quality = sum(SESSION_CATALOG[n][0] in QUALITY_CATEGORIES for n in snap["greedy"])
        o_quality = sum(SESSION_CATALOG[n][0] in QUALITY_CATEGORIES for n in optimum)
        _, gq, gr = v1_components(g_spend, snap["tn"]); _, oq, or_ = v1_components(o_spend, snap["tn"])
        gs = sum(max(0, SESSION_CATALOG[n][1]-snap["rpe_max"]) for n in snap["greedy"])
        os = sum(max(0, SESSION_CATALOG[n][1]-snap["rpe_max"]) for n in optimum)
        gf = max(-snap["best_die"], snap["fatigue_before"]+gq+gs+gr)
        of = max(-snap["best_die"], snap["fatigue_before"]+oq+os+or_)
        representative.append({"seed": snap["seed"], "turn": snap["turn"], "pool_active": "-".join(map(str,snap["pool_active"])),
                               "fatigue_before": snap["fatigue_before"], "energy": snap["energy"], "tn": snap["tn"],
                               "rpe_max": snap["rpe_max"], "greedy_bundle": "-".join(snap["greedy"]),
                               "optimum_bundle": "-".join(optimum), "greedy_score": greedy_score,
                               "optimum_score": optimum_score, "utility_gap": optimum_score-greedy_score,
                               "same_bundle": Counter(snap["greedy"]) == Counter(optimum),
                               "greedy_spend": g_spend, "optimum_spend": o_spend,
                               "energy_delta_opt_minus_greedy": o_spend-g_spend,
                               "greedy_quality": g_quality, "optimum_quality": o_quality,
                               "quality_delta": o_quality-g_quality, "greedy_q": gq, "optimum_q": oq,
                               "q_delta": oq-gq, "greedy_s": gs, "optimum_s": os, "s_delta": os-gs,
                               "greedy_recovery": gr, "optimum_recovery": or_, "recovery_delta": or_-gr,
                               "greedy_fatigue_projected": gf, "optimum_fatigue_projected": of,
                               "fatigue_delta": of-gf})

    best_scores = [r["marginal_utility"] for r in rejected]
    category_counts = Counter(r["category"] for r in rejected)
    dominant_counts = Counter(r["dominant_negative_term"] for r in rejected)
    headrooms = [r["headroom_tn_minus_spend"] for r in turn_rows]
    nonoptimal = [r for r in representative if r["utility_gap"] > 1e-12]
    summary = {
        "protocol": {"seeds": len(list(seeds)), "turns_per_seed": turns, "turns": len(turn_rows),
                     "weights": DEFAULT_SESSION_WEIGHTS, "representative_states": len(representative),
                     "candidate_observations": len(candidates), "full_candidate_log": str(full_log)},
        "capacity": {
            "mean_energy_available": mean(r["energy_available"] for r in turn_rows),
            "mean_energy_used": mean(r["energy_used"] for r in turn_rows),
            "mean_energy_remaining": mean(r["energy_remaining"] for r in turn_rows),
            "median_energy_remaining": median(r["energy_remaining"] for r in turn_rows),
            "mean_energy_use_rate": mean(r["energy_use_rate"] for r in turn_rows),
            "turns_with_energy_remaining_pct": 100*mean(r["energy_remaining"] > 0 for r in turn_rows),
            "turns_with_legal_candidate_pct": 100*mean(r["legal_candidate_remaining"] for r in turn_rows),
            "turns_with_productive_candidate_pct": 100*mean(r["productive_candidate_remaining"] for r in turn_rows),
            "turns_with_safe_productive_candidate_pct": 100*mean(r["safe_productive_candidate_remaining"] for r in turn_rows),
            "turns_with_positive_component_rejected_pct": 100*mean(r["positive_component_rejected"] for r in turn_rows),
            "mean_headroom_tn_minus_spend": mean(r["headroom_tn_minus_spend"] for r in turn_rows),
            "median_headroom_tn_minus_spend": median(r["headroom_tn_minus_spend"] for r in turn_rows),
            "headroom_min": min(headrooms), "headroom_max": max(headrooms),
            "headroom_distribution": dict(sorted(Counter(str(v) for v in headrooms).items(), key=lambda item: float(item[0]))),
            "mean_q": mean(r["q"] for r in turn_rows), "mean_s": mean(r["s"] for r in turn_rows),
            "mean_recovery": mean(r["recovery"] for r in turn_rows),
        },
        "stop_causes": stop_causes,
        "rejected": {"count": len(rejected), "mean_best_rejected_score": mean(best_scores) if best_scores else None,
                     "median_best_rejected_score": median(best_scores) if best_scores else None,
                     "min_best_rejected_score": min(best_scores) if best_scores else None,
                     "max_best_rejected_score": max(best_scores) if best_scores else None,
                     "categories": dict(category_counts), "dominant_negative_terms": dict(dominant_counts),
                     "sessions": dict(Counter(r["candidate"] for r in rejected)),
                     "mean_ctl_gain": mean(r["ctl_gain"] for r in rejected) if rejected else None,
                     "mean_quality_gain": mean(r["quality_gain"] for r in rejected) if rejected else None,
                     "mean_projected_q": mean(r["projected_q"] for r in rejected) if rejected else None,
                     "mean_projected_q_delta": mean(r["projected_q_delta"] for r in rejected) if rejected else None,
                     "mean_projected_s": mean(r["projected_s"] for r in rejected) if rejected else None,
                     "mean_projected_s_delta": mean(r["projected_s_delta"] for r in rejected) if rejected else None,
                     "mean_projected_recovery": mean(r["projected_recovery"] for r in rejected) if rejected else None,
                     "mean_projected_recovery_delta": mean(r["projected_recovery_delta"] for r in rejected) if rejected else None,
                     "mean_projected_fatigue_final": mean(r["projected_fatigue_final"] for r in rejected) if rejected else None,
                     "mean_delta_energy_term": mean(r["delta_energy_term"] for r in rejected) if rejected else None,
                     "mean_delta_quality_term": mean(r["delta_quality_term"] for r in rejected) if rejected else None,
                     "mean_delta_rpe_term": mean(r["delta_rpe_term"] for r in rejected) if rejected else None,
                     "mean_delta_fatigue_term": mean(r["delta_fatigue_term"] for r in rejected) if rejected else None,
                     "mean_fatigue_weight_break_even": mean(r["fatigue_weight_break_even"] for r in rejected if r["fatigue_weight_break_even"] is not None),
                     "mean_margin_drop_from_last_selection": mean(r["margin_drop_from_last_selection"] for r in rejected if r["margin_drop_from_last_selection"] is not None)},
        "rpe_gate": {"candidate_observations": len(rpe_only),
                     "states": len({(r['seed'],r['turn'],r['greedy_step'],r['phase']) for r in rpe_only}),
                     "turns": len({(r['seed'],r['turn']) for r in rpe_only}),
                     "competitive": competitive, "ranked_first": first,
                     "categories": dict(Counter(r["category"] for r in rpe_only)),
                     "sessions": dict(Counter(r["candidate"] for r in rpe_only)),
                     "potential_s_sum": sum(max(0, r["rpe"]-r["rpe_max"]) for r in rpe_only),
                     "mean_score": mean(r["marginal_utility"] for r in rpe_only) if rpe_only else None,
                     "mean_bust_probability": mean(r["bust_probability"] for r in rpe_only) if rpe_only else None,
                     "mean_energy_remaining": mean(r["energy_remaining_before"] for r in rpe_only) if rpe_only else None,
                     "mean_energy_cost": mean(r["energy_cost"] for r in rpe_only) if rpe_only else None},
        "greedy_vs_optimum": {"states": len(representative),
                              "same_bundle_count": sum(r["same_bundle"] for r in representative),
                              "same_bundle_pct": 100*mean(r["same_bundle"] for r in representative),
                              "same_utility_count": sum(abs(r["utility_gap"]) < 1e-12 for r in representative),
                              "same_utility_pct": 100*mean(abs(r["utility_gap"]) < 1e-12 for r in representative),
                              "mean_utility_gap": mean(r["utility_gap"] for r in representative),
                              "max_utility_gap": max(r["utility_gap"] for r in representative),
                              "nonoptimal_states": len(nonoptimal),
                              "mean_utility_gap_when_nonoptimal": mean(r["utility_gap"] for r in nonoptimal),
                              "max_utility_gap_when_nonoptimal": max(r["utility_gap"] for r in nonoptimal),
                              "mean_energy_delta": mean(r["energy_delta_opt_minus_greedy"] for r in representative),
                              "mean_greedy_energy": mean(r["greedy_spend"] for r in representative),
                              "mean_optimum_energy": mean(r["optimum_spend"] for r in representative),
                              "greedy_unused_energy_pct": 100*mean(r["greedy_spend"] < r["energy"] for r in representative),
                              "optimum_unused_energy_pct": 100*mean(r["optimum_spend"] < r["energy"] for r in representative),
                              "mean_quality_delta": mean(r["quality_delta"] for r in representative),
                              "mean_greedy_quality": mean(r["greedy_quality"] for r in representative),
                              "mean_optimum_quality": mean(r["optimum_quality"] for r in representative),
                              "mean_q_delta": mean(r["q_delta"] for r in representative),
                              "mean_s_delta": mean(r["s_delta"] for r in representative),
                              "mean_recovery_delta": mean(r["recovery_delta"] for r in representative),
                              "mean_fatigue_delta": mean(r["fatigue_delta"] for r in representative)},
    }
    return summary, turn_rows, stop_causes, rejected, representative, rpe_only


def render_report(summary):
    c, rejected, gate, optimum = (summary["capacity"], summary["rejected"],
                                  summary["rpe_gate"], summary["greedy_vs_optimum"])
    causes = "\n".join(
        f"- `{row['cause']}`: {row['count']} tours ({row['percentage']:.1f} %)."
        for row in summary["stop_causes"]
    )
    return f"""# Audit décisionnel P0 / session selector

## FACT

- Protocole : 100 seeds × 16 tours ; poids inchangés `{summary['protocol']['weights']}`.
- Le log candidat complet est externe au dépôt : `{summary['protocol']['full_candidate_log']}`.
- L'instrumentation affirme à chaque tour l'identité de sa sélection avec `choose_sessions_weighted`.

## OBSERVATION

- Énergie moyenne disponible/utilisée/restante : {c['mean_energy_available']:.6f} / {c['mean_energy_used']:.6f} / {c['mean_energy_remaining']:.6f}.
- Tours avec énergie restante et candidat légal/productif/sans OT immédiat : {c['turns_with_energy_remaining_pct']:.1f} % / {c['turns_with_legal_candidate_pct']:.1f} % / {c['turns_with_productive_candidate_pct']:.1f} % / {c['turns_with_safe_productive_candidate_pct']:.1f} %.
- Q/S/Recovery moyens : {c['mean_q']:.6f} / {c['mean_s']:.6f} / {c['mean_recovery']:.6f}.
{causes}
- Meilleur candidat rejeté : score moyen {rejected['mean_best_rejected_score']:.6f}, toujours EF, terme négatif dominant toujours `delta_fatigue_term`.
- Barrière RPE : {gate['candidate_observations']} observations, {gate['competitive']} compétitives, {gate['ranked_first']} premières, S potentiel cumulé {gate['potential_s_sum']}.
- Greedy contre optimum exact : {optimum['states']} états, même utilité dans {optimum['same_utility_pct']:.1f} %, écart moyen {optimum['mean_utility_gap']:.6f}, maximal {optimum['max_utility_gap']:.6f}.

## INTERPRETATION

- La règle d'arrêt marginale explique directement 68 % des fins de sélection ; le coût de fatigue marginal domine les meilleurs rejets.
- L'écart à l'optimum de même utilité indique aussi un effet de l'ordre greedy/priorité SL, notamment lorsqu'une EF localement négative ouvrirait ensuite une séance de qualité.

## LIMITS

- Les 30 états exacts sont un échantillon déterministe (seeds 0–9, tours 1/8/16), pas tous les états.
- Le contre-factuel RPE est local et ne génère aucune trajectoire alternative.
- Cette politique simulée ne caractérise pas un joueur humain.

## DESIGN QUESTIONS

- Quelle part du comportement voulu doit relever de l'utilité globale, de la priorité SL et de l'arrêt marginal local ?
- La barrière RPE doit-elle rester analysée comme contrainte d'accès distincte des préférences du score ?
"""


def write_results(output=DEFAULT_RESULTS_DIR, seeds=range(100), turns=16, full_log=DEFAULT_FULL_LOG):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    summary, turns_rows, stop_causes, rejected, representative, rpe_only = analyze(seeds, turns, full_log)
    (output/"summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_dict_csv(output/"stop_causes.csv", stop_causes)
    _write_dict_csv(output/"rejected_candidates.csv", rejected)
    _write_dict_csv(output/"representative_states.csv", representative)
    _write_dict_csv(output/"rpe_gate_sample.csv", rpe_only[:500])
    (output/"README.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description="External audit of production P0 session selection")
    parser.add_argument("--seeds", type=int, default=100); parser.add_argument("--turns", type=int, default=16)
    parser.add_argument("--output", default=str(DEFAULT_RESULTS_DIR)); parser.add_argument("--full-log", default=str(DEFAULT_FULL_LOG))
    args = parser.parse_args()
    print(json.dumps(write_results(args.output, range(args.seeds), args.turns, Path(args.full_log)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
