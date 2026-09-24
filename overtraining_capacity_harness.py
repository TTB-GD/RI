"""External experiment: Fatigue V1 capacity to reach overtraining.

No production module, GDD rule, catalogue, weight, or production behaviour is
modified.  P1/P2/P3 below are instruments for exploring legal selections, not
player strategies or design rules.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

from decision_engine import _round_half_away_from_zero, choose_weighted_action
from dice_progression import DEFAULT_UPGRADE_WEIGHTS
from dice_types import make_pool, pool_tn
from game_logger import write_csv
from player_state import Player
from session_effects import session_outcome
from session_selector import _SelectionState, _commit, _is_affordable, choose_sessions_weighted
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG
from simulate_player import DEFAULT_WEIGHTS, _split_active_reserve

NORMAL, SUCCESS, BUST, UNTESTED = "normal_realisee", "risque_reussi", "risque_annulee_bust", "risque_non_testee_apres_bust"
POLICIES = ("P0_CURRENT", "P1_HIGH_LOAD", "P2_MAX_Q", "P3_MAX_S")


@dataclass
class Fatigue:
    value: int = 0
    suspended_index: int | None = None
    removed_since: int | None = None


def v1_components(spend, tn):
    """The closed V1 Q/Recovery tables, independently of production fatigue."""
    x = _round_half_away_from_zero(spend - tn)
    q = 0 if x <= 0 else {1: 1, 2: 2, 3: 3, 4: 5, 5: 8}.get(x, 13)
    recovery = 0 if x >= -3 else {-4: -1, -5: -2, -6: -3}.get(x, -4)
    return x, q, recovery


def _roll(active_sizes):
    dice = make_pool(active_sizes)
    active, reserve = _split_active_reserve(dice)
    tn = pool_tn(dice)
    faces, values = [], []
    for die in active:
        face, value = die.roll(); faces.append(face); values.append(value)
    choice, index, _ = choose_weighted_action(active, reserve, faces, len(dice), tn, **DEFAULT_WEIGHTS)
    if choice in ("add", "add+reroll"):
        face, value = reserve.roll(); faces.append(face); values.append(value)
    if choice in ("reroll", "add+reroll"):
        face, value = active[index].roll(); faces[index] = face; values[index] = value
    outcome = session_outcome(faces, values, len(dice))
    return {"energy": outcome["total"], "rpe_max": outcome["rpe_max"], "tn": tn, "action": choice}


def _risk_allowed(policy):
    return policy != "P0_CURRENT"


def _choose_load_policy(available, energy, rpe_max, tn, policy):
    """Local deterministic experimental selectors.  Only the RPE gate opens."""
    state, chosen = _SelectionState(), []
    legal_rpe = max(SESSION_CATALOG[name][1] for name in available) if _risk_allowed(policy) else rpe_max
    while True:
        candidates = [name for name in available if _is_affordable(name, state, energy, legal_rpe)]
        if not candidates:
            return chosen
        scored = []
        for catalog_order, name in enumerate(available):
            if name not in candidates:
                continue
            _, rpe = SESSION_CATALOG[name]
            next_spend = state.energy_used + rpe
            _, potential_q, _ = v1_components(next_spend, tn)
            potential_s = sum(max(0, SESSION_CATALOG[n][1] - rpe_max) for n in state.chosen)
            potential_s += max(0, rpe - rpe_max)
            # Negative catalog position is an explicit stable tie-break.
            if policy == "P1_HIGH_LOAD":
                key = (potential_q, potential_s, next_spend, -catalog_order)
            elif policy == "P2_MAX_Q":
                key = (potential_q, next_spend, potential_s, -catalog_order)
            elif policy == "P3_MAX_S":
                key = (potential_s, potential_q, next_spend, -catalog_order)
            else:
                raise ValueError(policy)
            scored.append((key, name))
        _, name = max(scored)
        _commit(name, state)
        chosen.append(name)


def choose(policy, available, energy, rpe_max, tn):
    if policy == "P0_CURRENT":
        return choose_sessions_weighted(available, energy, rpe_max, tn)[0]
    return _choose_load_policy(available, energy, rpe_max, tn, policy)


def resolve(chosen, rpe_max, best_die):
    rows, has_busted = [], False
    for order, name in enumerate(chosen, 1):
        category, rpe = SESSION_CATALOG[name]
        exceedance, bust_roll = max(0, rpe-rpe_max), None
        if exceedance == 0:
            status = NORMAL
        elif has_busted:
            status = UNTESTED
        else:
            bust_roll = random.randint(1, best_die)
            status = BUST if bust_roll <= exceedance else SUCCESS
            has_busted = status == BUST
        rows.append({"resolution_order": order, "session": name, "category": category, "rpe": rpe,
                     "exceedance": exceedance, "bust_roll": bust_roll, "status": status,
                     "realized": status in (NORMAL, SUCCESS)})
    return rows


def _active_indices(player, fatigue):
    # This is the existing validated V1 recovery boundary: fatigue <= best die.
    if fatigue.suspended_index is not None and fatigue.value <= max(player.dice_pool.sizes):
        fatigue.suspended_index, fatigue.removed_since = None, None
        return list(range(len(player.dice_pool.sizes))), True
    return [i for i in range(len(player.dice_pool.sizes)) if i != fatigue.suspended_index], False


def simulate(seed, policy, turns=16):
    """One policy is independently seeded with `seed`; divergence is intentional and logged."""
    random.seed(seed)
    player, fatigue = Player(), Fatigue()
    turns_out, sessions_out = [], []
    previous_permanent, previous_active_best = None, None
    for turn in range(1, turns + 1):
        player.dice_pool.maybe_add_dice(player.cumulative_ctl)
        player.dice_pool.maybe_upgrade(player.progress.quality_total, DEFAULT_UPGRADE_WEIGHTS)
        permanent = player.dice_pool.sizes.copy()
        progression_this_turn = previous_permanent is not None and permanent != previous_permanent
        suspended_before_recovery = fatigue.suspended_index is not None
        removed_since_before_recovery = fatigue.removed_since
        active_indices, recovered = _active_indices(player, fatigue)
        active = [permanent[i] for i in active_indices]
        roll = _roll(active)
        available = player.progress.available_sessions()
        selected = choose(policy, available, roll["energy"], roll["rpe_max"], roll["tn"])
        resolution = resolve(selected, roll["rpe_max"], max(active))
        realized = [r["session"] for r in resolution if r["realized"]]
        planned, effective = sum(SESSION_CATALOG[n][1] for n in selected), sum(SESSION_CATALOG[n][1] for n in realized)
        potential_s = sum(max(0, SESSION_CATALOG[n][1] - roll["rpe_max"]) for n in selected)
        s = sum(max(0, SESSION_CATALOG[n][1] - roll["rpe_max"]) for n in realized)
        offset, q, recovery = v1_components(effective, roll["tn"])
        before, best_die = fatigue.value, max(active)
        raw, bound = before + q + s + recovery, -best_die
        fatigue.value = max(bound, raw)
        overtraining = fatigue.value > best_die
        removed = None
        duration = turn - removed_since_before_recovery if recovered else None
        if overtraining and fatigue.suspended_index is None:
            fatigue.suspended_index = min(active_indices, key=lambda i: (permanent[i], -i))
            fatigue.removed_since = turn
            removed = f"#{fatigue.suspended_index}:d{permanent[fatigue.suspended_index]}"
        next_active = [size for i, size in enumerate(permanent) if i != fatigue.suspended_index]
        statuses = Counter(r["status"] for r in resolution)
        row = {"seed": seed, "turn": turn, "policy": policy, "pool_permanent": "-".join(map(str, permanent)),
               "pool_active": "-".join(map(str, active)), "pool_active_next": "-".join(map(str, next_active)),
               "active_dice_next": len(next_active), "best_die": best_die, "tn": roll["tn"], "rpe_max": roll["rpe_max"],
               "energy": roll["energy"], "fatigue_before": before, "fatigue_after": fatigue.value,
               "fatigue_delta": fatigue.value-before, "fatigue_raw": raw, "negative_bound": bound,
               "overtraining_threshold": best_die, "spend_planned": planned, "spend_effective": effective,
               "sessions_selected": len(selected), "normal_sessions": statuses[NORMAL],
               "risk_sessions": statuses[SUCCESS]+statuses[BUST]+statuses[UNTESTED], "sessions_realized": len(realized),
               "busts": statuses[BUST], "risk_untested": statuses[UNTESTED], "s_potential": potential_s,
               "s_effective": s, "q": q, "recovery": recovery, "stress": q+s, "ctl": player.cumulative_ctl+effective,
               "overtraining": overtraining, "die_removed": removed, "removal_reason": "fatigue_gt_best_die" if removed else "",
               "die_suspended": fatigue.suspended_index is not None, "die_recovered": recovered,
               "amputation_duration_at_recovery": duration, "upgrades_used": player.dice_pool.upgrades_used,
               "dice_added": player.dice_pool.dice_added, "quality_total": player.progress.quality_total,
               "dice_action": roll["action"], "offset_effective_minus_tn": offset,
               "progression_this_turn": progression_this_turn,
               "threshold_changed_while_suspended": suspended_before_recovery and previous_active_best is not None and best_die != previous_active_best}
        for r in resolution:
            sessions_out.append({"seed": seed, "turn": turn, "policy": policy, **r})
        for name in realized:
            player.progress.record_session(name)
        player.cumulative_ctl += effective
        row["quality_total"], row["ctl"] = player.progress.quality_total, player.cumulative_ctl
        turns_out.append(row)
        previous_permanent, previous_active_best = permanent, best_die
    return turns_out, sessions_out


def deterministic_scenarios():
    """Rule-table scenarios; inputs are actual V1 state values, not changed rules."""
    cases = {
        "A_q_seul": [(20, 14, 0, 6)] * 3,
        "B_s_seul": [(14, 14, 3, 6)] * 3,
        "C_q_plus_s": [(20, 14, 3, 6)] * 2,
        "D_recuperation": [(20, 14, 3, 6)] * 2 + [(7, 14, 0, 6)] * 7,
        # The permanent pool advances from a legal d6 state to a legal d8
        # state while its d6 remains suspended; no die size is invented.
        "E_progression_pendant_overtraining": [(20, 14, 3, 6), (20, 14, 3, 6), (7, 14, 0, 8)],
    }
    output = {}
    for name, steps in cases.items():
        fatigue, rows, suspended = 0, [], False
        for turn, (spend, tn, s, best) in enumerate(steps, 1):
            _, q, recovery = v1_components(spend, tn)
            raw = fatigue + q + s + recovery
            fatigue = max(-best, raw)
            overtraining = fatigue > best
            suspended_before = suspended
            if overtraining: suspended = True
            recovered = suspended and fatigue <= best
            if recovered: suspended = False
            rows.append({"turn": turn, "spend": spend, "tn": tn, "q": q, "s": s, "recovery": recovery,
                         "fatigue": fatigue, "overtraining": overtraining, "removed": overtraining and not suspended_before,
                         "recovered": recovered})
        output[name] = rows
    return output


def _summary(turns, sessions):
    by_seed = defaultdict(list)
    for row in turns: by_seed[row["seed"]].append(row)
    over_seeds = [seed for seed, rs in by_seed.items() if any(r["overtraining"] for r in rs)]
    episodes, durations = 0, []
    for rs in by_seed.values():
        run = 0
        for r in rs:
            if r["die_suspended"]: run += 1
            elif run: episodes += 1; durations.append(run); run = 0
        if run: episodes += 1; durations.append(run)
    c = Counter(s["status"] for s in sessions)
    fs = [r["fatigue_after"] for r in turns]
    first = [min(r["turn"] for r in by_seed[seed] if r["overtraining"]) for seed in over_seeds]
    return {"overtraining_events": sum(bool(r["die_removed"]) for r in turns), "parties_with_overtraining": len(over_seeds),
            "share_parties_with_overtraining": len(over_seeds)/len(by_seed), "first_overtraining_turn_mean": mean(first) if first else None,
            "fatigue_max": max(fs), "fatigue_mean": mean(fs), "fatigue_median": median(fs),
            "mean_turns_fatigue_positive": mean(sum(r["fatigue_after"] > 0 for r in rs) for rs in by_seed.values()),
            "mean_turns_above_best_die": mean(sum(r["fatigue_after"] > r["best_die"] for r in rs) for rs in by_seed.values()),
            "overtraining_turns": sum(r["overtraining"] for r in turns), "amputation_episodes": episodes,
            "amputation_duration_mean": mean(durations) if durations else 0, "amputation_duration_max": max(durations, default=0),
            "dice_removed": sum(bool(r["die_removed"]) for r in turns), "recoveries": sum(r["die_recovered"] for r in turns),
            "busts": c[BUST], "lost_energy_bust": sum(r["spend_planned"]-r["spend_effective"] for r in turns),
            "q": sum(r["q"] for r in turns), "s": sum(r["s_effective"] for r in turns),
            "recovery": sum(r["recovery"] for r in turns), "stress": sum(r["stress"] for r in turns),
            "effective_ctl": sum(r["spend_effective"] for r in turns),
            "progression_while_suspended": sum(r["die_suspended"] and r["progression_this_turn"] for r in turns),
            "threshold_changes_while_suspended": sum(r["threshold_changed_while_suspended"] for r in turns)}


def run(seeds=range(100), turns=16):
    data, session_data, summaries = {}, {}, {}
    for policy in POLICIES:
        rows, sessions = [], []
        for seed in seeds:
            t, s = simulate(seed, policy, turns); rows.extend(t); sessions.extend(s)
        data[policy], session_data[policy], summaries[policy] = rows, sessions, _summary(rows, sessions)
    return data, session_data, summaries


def write_results(output="overtraining_capacity_results", seeds=range(100), turns=16):
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    data, sessions, summaries = run(seeds, turns)
    for policy in POLICIES:
        write_csv(out / f"{policy}_turns.csv", data[policy]); write_csv(out / f"{policy}_sessions.csv", sessions[policy])
    (out / "summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    (out / "deterministic_scenarios.json").write_text(json.dumps(deterministic_scenarios(), indent=2), encoding="utf-8")
    p0, p1 = summaries["P0_CURRENT"], summaries["P1_HIGH_LOAD"]
    report = ["# Capacité d'overtraining — Fatigue V1", "", "## FAITS", "",
              f"- Protocole : {len(list(seeds))} seeds × {turns} tours, chaque politique réinitialise le RNG avec la même seed.",
              f"- P0 : {p0['overtraining_events']} entrées en overtraining ; P1 : {p1['overtraining_events']} entrées dans {p1['parties_with_overtraining']} parties.",
              "- Les CSV par politique portent la trace tour et séance ; les scénarios déterministes sont dans `deterministic_scenarios.json`.",
              "", "## OBSERVATIONS", "", "- Les différences de décisions et de nombre de jets de bust font diverger le flux aléatoire après le premier choix divergent.",
              "", "## INTERPRÉTATIONS", "", "- Aucune conclusion d'équilibrage n'est tirée.",
              "", "## LIMITES", "", "- P2 et P3 maximisent une priorité locale; ils ne forcent pas artificiellement Q ou S à zéro.",
              "", "## QUESTIONS DE DESIGN", "", "- Les résultats ne proposent aucune modification de V1."]
    (out / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="External Fatigue V1 overtraining-capacity harness")
    parser.add_argument("--seeds", type=int, default=100); parser.add_argument("--turns", type=int, default=16)
    parser.add_argument("--output", default="overtraining_capacity_results")
    args = parser.parse_args()
    print(json.dumps(write_results(args.output, range(args.seeds), args.turns), indent=2))
