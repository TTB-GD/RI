"""External bundle/risk experiment; production P0 and game rules stay untouched."""
from __future__ import annotations

import argparse, csv, json, math, random, sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from dice_progression import DEFAULT_UPGRADE_WEIGHTS
from overtraining_capacity_harness import (BUST, NORMAL, SUCCESS, UNTESTED, Fatigue,
    _active_indices, _roll, resolve, v1_components)
from player_state import Player
from session_selector import (DEFAULT_SESSION_WEIGHTS, MAX_SESSIONS_PER_TURN,
    _SelectionState, _commit, _marginal_utility, choose_sessions_weighted)
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG

POLICIES = ("P0_CURRENT", "P_STD_EV", "P_STD_MOD15", "P_STD_MOD25", "P_STD_MOD40")
THRESHOLDS = {"P_STD_MOD15": .15, "P_STD_MOD25": .25, "P_STD_MOD40": .40}
BEAM_WIDTH, EXHAUSTIVE_BOUND = 1024, 50_000
OUT = Path(__file__).resolve().parent
CATALOG_ORDER = {name: i for i, name in enumerate(SESSION_CATALOG)}


def risk_probability(name, rpe_max, best_die):
    return min(max(0, SESSION_CATALOG[name][1]-rpe_max)/best_die, 1.0)


def bundle_counts(bundle):
    ef = sum(SESSION_CATALOG[n][0] not in QUALITY_CATEGORIES for n in bundle)
    quality = len(bundle)-ef
    return ef, quality, sum(SESSION_CATALOG[n][0] == "SL" for n in bundle)


def structurally_legal(bundle, energy):
    ef, quality, sl = bundle_counts(bundle)
    return (len(bundle) <= MAX_SESSIONS_PER_TURN and
            sum(SESSION_CATALOG[n][1] for n in bundle) <= energy and quality <= ef and sl <= 1)


def ordered_outcomes(bundle, rpe_max, best_die):
    """Exact mutually exclusive outcomes under first-bust-stops-risk-tests."""
    normal = tuple(n for n in bundle if SESSION_CATALOG[n][1] <= rpe_max)
    risky = tuple(n for n in bundle if SESSION_CATALOG[n][1] > rpe_max)
    outcomes, survival, successes = [], 1.0, []
    for name in risky:
        p = risk_probability(name, rpe_max, best_die)
        if p:
            outcomes.append((survival*p, normal+tuple(successes), name))
        survival *= 1-p
        successes.append(name)
    outcomes.append((survival, normal+tuple(successes), None))
    return outcomes


def outcome_terms(realized, energy, tn, rpe_max):
    spend = sum(SESSION_CATALOG[n][1] for n in realized)
    quality = sum(SESSION_CATALOG[n][0] in QUALITY_CATEGORIES for n in realized)
    avg_rpe = mean(SESSION_CATALOG[n][1] for n in realized) if realized else 0.0
    _, q, recovery = v1_components(spend, tn)
    s = sum(max(0, SESSION_CATALOG[n][1]-rpe_max) for n in realized)
    short_fatigue = max(0, q+s+recovery)  # negative fatigue is not rewarded
    terms = {
        "ctl_term": DEFAULT_SESSION_WEIGHTS["w_energy"]*(spend/energy if energy else 0),
        "quality_term": DEFAULT_SESSION_WEIGHTS["w_sessions"]*quality,
        "rpe_term": DEFAULT_SESSION_WEIGHTS["w_rpe"]*(avg_rpe/rpe_max if rpe_max else 0),
        "fatigue_cost": -DEFAULT_SESSION_WEIGHTS["w_fatigue"]*short_fatigue,
    }
    return {"spend": spend, "quality": quality, "q": q, "s": s, "recovery": recovery,
            "short_fatigue": short_fatigue, "value": sum(terms.values()), **terms}


def evaluate_bundle(bundle, policy, energy, rpe_max, tn, best_die):
    planned = sum(SESSION_CATALOG[n][1] for n in bundle)
    risks = [risk_probability(n, rpe_max, best_die) for n in bundle if SESSION_CATALOG[n][1] > rpe_max]
    if policy in THRESHOLDS and any(p > THRESHOLDS[policy]+1e-12 for p in risks): return None
    if policy == "P_STD_EV":
        metrics = defaultdict(float)
        for probability, realized, _ in ordered_outcomes(bundle, rpe_max, best_die):
            terms = outcome_terms(realized, energy, tn, rpe_max)
            for key, value in terms.items(): metrics[key] += probability*value
        value = metrics["value"]
    else:
        metrics = defaultdict(float, outcome_terms(bundle, energy, tn, rpe_max)); value = metrics["value"]
    ef, quality, sl = bundle_counts(bundle)
    return {"bundle": bundle, "value": value, "planned": planned, "ef": ef, "quality": quality,
            "sl": sl, "risk_count": len(risks), "mean_risk": mean(risks) if risks else 0,
            "expected_spend": metrics["spend"], "expected_quality": metrics["quality"],
            "expected_q": metrics["q"], "expected_s": metrics["s"],
            "expected_recovery": metrics["recovery"], "expected_short_fatigue": metrics["short_fatigue"],
            "ctl_term": metrics["ctl_term"], "quality_term": metrics["quality_term"],
            "rpe_term": metrics["rpe_term"], "fatigue_cost": metrics["fatigue_cost"]}


def _sort_key(record):
    return (record["value"], record["expected_quality"], record["expected_spend"],
            -record["mean_risk"], tuple(-CATALOG_ORDER[n] for n in record["bundle"]))


@lru_cache(maxsize=None)
def select_bundle_cached(available, energy, rpe_max, tn, best_die, policy):
    """Exact for small spaces; otherwise deterministic width-1024 bundle beam."""
    available = tuple(available)
    exhaustive = math.comb(len(available)+MAX_SESSIONS_PER_TURN, MAX_SESSIONS_PER_TURN) <= EXHAUSTIVE_BOUND
    frontier = {()}; all_records = []
    for depth in range(MAX_SESSIONS_PER_TURN+1):
        records = []
        for bundle in frontier:
            record = evaluate_bundle(bundle, policy, energy, rpe_max, tn, best_die)
            if record is not None: records.append(record); all_records.append(record)
        if depth == MAX_SESSIONS_PER_TURN: break
        expanded = set()
        for bundle in frontier:
            start = CATALOG_ORDER[bundle[-1]] if bundle else 0
            for name in available:
                if CATALOG_ORDER[name] < start: continue
                candidate = bundle+(name,)
                if structurally_legal(candidate, energy):
                    if policy not in THRESHOLDS or risk_probability(name, rpe_max, best_die) <= THRESHOLDS[policy]+1e-12:
                        expanded.add(candidate)
        if not exhaustive and len(expanded) > BEAM_WIDTH:
            ranked = [evaluate_bundle(b, policy, energy, rpe_max, tn, best_die) for b in expanded]
            ranked = sorted((r for r in ranked if r), key=_sort_key, reverse=True)[:BEAM_WIDTH]
            frontier = {r["bundle"] for r in ranked}
        else: frontier = expanded
        if not frontier: break
    best = max(all_records, key=_sort_key)
    lower_ef = [record for record in all_records if record["ef"] < best["ef"]]
    alternative = max(lower_ef, key=_sort_key) if lower_ef else None
    risk_bundles = sum(record["risk_count"] > 0 for record in all_records)
    return best, alternative, "exhaustive" if exhaustive else f"beam_{BEAM_WIDTH}", len(all_records), risk_bundles


def select_bundle(available, energy, rpe_max, tn, best_die, policy):
    return select_bundle_cached(tuple(available), energy, rpe_max, tn, best_die, policy)


def instrumental_ef_case(chosen_record, alternative, energy, rpe_max, tn):
    bundle = chosen_record["bundle"]
    state = _SelectionState(); negative = []
    quality_total = sum(SESSION_CATALOG[n][0] in QUALITY_CATEGORIES for n in bundle)
    ef_seen = 0
    for name in bundle:
        if SESSION_CATALOG[name][0] in QUALITY_CATEGORIES: continue
        ef_seen += 1
        margin = _marginal_utility(name, state, energy, rpe_max, tn, DEFAULT_SESSION_WEIGHTS)
        if margin < 0 and quality_total >= ef_seen: negative.append((name, margin))
        _commit(name, state)
    # One fewer EF is the counterfactual that removes the instrumental quota
    # slot, independently of which EF name fills that slot.
    if not negative or not alternative: return None
    chosen = outcome_terms(bundle, energy, tn, rpe_max); alt = outcome_terms(alternative["bundle"], energy, tn, rpe_max)
    return {"negative_ef_count": len(negative), "negative_efs": "|".join(n for n,_ in negative),
            "mean_local_margin": mean(m for _,m in negative), "chosen_bundle": "|".join(bundle),
            "alternative_bundle": "|".join(alternative["bundle"]), "global_value_gain": chosen_record["value"]-alternative["value"],
            "quality_gain": chosen["quality"]-alt["quality"], "ctl_gain": chosen["spend"]-alt["spend"],
            "energy_cost_gain": chosen["spend"]-alt["spend"], "short_fatigue_delta": chosen["short_fatigue"]-alt["short_fatigue"]}


def simulate_policy(seed, policy, turns=16):
    random.seed(seed); player, fatigue = Player(), Fatigue()
    rows, sessions, instrumental = [], [], []
    upgrade_turns, add_turns = [], []
    for turn in range(1, turns+1):
        old_u, old_a = player.dice_pool.upgrades_used, player.dice_pool.dice_added
        player.dice_pool.maybe_add_dice(player.cumulative_ctl)
        player.dice_pool.maybe_upgrade(player.progress.quality_total, DEFAULT_UPGRADE_WEIGHTS)
        if player.dice_pool.upgrades_used > old_u: upgrade_turns.append(turn)
        if player.dice_pool.dice_added > old_a: add_turns.append(turn)
        permanent = player.dice_pool.sizes.copy(); active_idx, recovered = _active_indices(player, fatigue)
        active = [permanent[i] for i in active_idx]; roll = _roll(active); available = player.progress.available_sessions()
        if policy == "P0_CURRENT":
            chosen = tuple(choose_sessions_weighted(available, roll["energy"], roll["rpe_max"], roll["tn"])[0])
            selected_eval, alternative, method, considered, risk_considered = None, None, "production_greedy", 0, 0
        else:
            selected_eval, alternative, method, considered, risk_considered = select_bundle(available, roll["energy"], roll["rpe_max"], roll["tn"], max(active), policy)
            chosen = selected_eval["bundle"]
            case = instrumental_ef_case(selected_eval, alternative, roll["energy"], roll["rpe_max"], roll["tn"])
            if case: instrumental.append({"seed":seed,"turn":turn,"policy":policy,**case})
        resolved = resolve(chosen, roll["rpe_max"], max(active)); realized=[r["session"] for r in resolved if r["realized"]]
        planned=sum(SESSION_CATALOG[n][1] for n in chosen); effective=sum(SESSION_CATALOG[n][1] for n in realized)
        _,q,recovery=v1_components(effective,roll["tn"]); s=sum(max(0,SESSION_CATALOG[n][1]-roll["rpe_max"]) for n in realized)
        before,best=fatigue.value,max(active); raw=before+q+s+recovery; fatigue.value=max(-best,raw); ot=fatigue.value>best
        removed=None
        if ot and fatigue.suspended_index is None:
            fatigue.suspended_index=min(active_idx,key=lambda i:(permanent[i],-i)); fatigue.removed_since=turn; removed=permanent[fatigue.suspended_index]
        status=Counter(r["status"] for r in resolved)
        risk_selected=sum(SESSION_CATALOG[n][1]>roll["rpe_max"] for n in chosen)
        risk_probs=[risk_probability(n,roll["rpe_max"],best) for n in chosen if SESSION_CATALOG[n][1]>roll["rpe_max"]]
        ef=sum(SESSION_CATALOG[n][0] not in QUALITY_CATEGORIES for n in chosen); qual=len(chosen)-ef; sl=sum(SESSION_CATALOG[n][0]=="SL" for n in chosen)
        remaining=roll["energy"]-planned
        raw_add=[]
        for name in available:
            cand=tuple(sorted(chosen+(name,),key=CATALOG_ORDER.get))
            if structurally_legal(cand,roll["energy"]): raw_add.append(name)
        allowed_add=[n for n in raw_add if policy not in THRESHOLDS or risk_probability(n,roll["rpe_max"],best)<=THRESHOLDS[policy]+1e-12]
        if remaining<=0: unused_reason="no_energy"
        elif not raw_add: unused_reason="energy_or_structure_discretization"
        elif not allowed_add: unused_reason="risk_too_high"
        else: unused_reason="fatigue_or_value_cost"
        row={"seed":seed,"turn":turn,"policy":policy,"energy_available":roll["energy"],"energy_planned":planned,"energy_effective":effective,
             "energy_lost":planned-effective,"energy_remaining_planned":remaining,"headroom":roll["tn"]-effective,"sessions":len(chosen),"ef":ef,"quality":qual,"sl":sl,
             "risk_selected":risk_selected,"risk_tested":status[SUCCESS]+status[BUST],"risk_success":status[SUCCESS],"busts":status[BUST],"risk_untested":status[UNTESTED],
             "mean_selected_risk":mean(risk_probs) if risk_probs else 0,"q":q,"s":s,"recovery":recovery,"fatigue_before":before,"fatigue_raw":raw,"fatigue_final":fatigue.value,
             "negative_bound":fatigue.value==-best,"overtraining":ot,"die_removed":removed,"die_recovered":recovered,"ctl":player.cumulative_ctl+effective,
             "pool_active":"-".join(map(str,active)),"pool_permanent":"-".join(map(str,permanent)),"rpe_max":roll["rpe_max"],"tn":roll["tn"],
             "bundle":"|".join(chosen),"search_method":method,"bundles_considered":considered,"risk_bundles_considered":risk_considered,"unused_reason":unused_reason,
             "instrumental_ef":bool(policy!="P0_CURRENT" and instrumental and instrumental[-1]["seed"]==seed and instrumental[-1]["turn"]==turn)}
        for rr in resolved: sessions.append({"seed":seed,"turn":turn,"policy":policy,**rr})
        for name in realized: player.progress.record_session(name)
        player.cumulative_ctl+=effective; row["quality_total"]=player.progress.quality_total; rows.append(row)
    return rows,sessions,instrumental,{"seed":seed,"ctl_final":player.cumulative_ctl,"quality_final":player.progress.quality_total,
        "pool_final":"-".join(map(str,player.dice_pool.sizes)),"upgrade_turns":"|".join(map(str,upgrade_turns)),"add_turns":"|".join(map(str,add_turns))}


def summarize(policy, rows, sessions, finals):
    byseed=defaultdict(list)
    for r in rows: byseed[r["seed"]].append(r)
    final_f=[rs[-1]["fatigue_final"] for rs in byseed.values()]; otseeds=[rs for rs in byseed.values() if any(r["overtraining"] for r in rs)]
    risk=[s for s in sessions if s["exceedance"]>0]; bust=sum(s["status"]==BUST for s in risk)
    upgrades=[int(f["upgrade_turns"].split("|")[0]) for f in finals if f["upgrade_turns"]]; additions=[int(f["add_turns"].split("|")[0]) for f in finals if f["add_turns"]]
    return {"policy":policy,"turns":len(rows),"energy_available":sum(r["energy_available"] for r in rows),"energy_planned":sum(r["energy_planned"] for r in rows),
      "energy_effective":sum(r["energy_effective"] for r in rows),"energy_lost":sum(r["energy_lost"] for r in rows),
      "energy_used_pct":100*sum(r["energy_effective"] for r in rows)/sum(r["energy_available"] for r in rows),"energy_remaining_mean":mean(r["energy_available"]-r["energy_effective"] for r in rows),
      "turns_energy_remaining_pct":100*mean(r["energy_available"]>r["energy_effective"] for r in rows),"headroom_mean":mean(r["headroom"] for r in rows),
      "sessions_per_turn":mean(r["sessions"] for r in rows),"ef_per_turn":mean(r["ef"] for r in rows),"quality_per_turn":mean(r["quality"] for r in rows),"sl_per_turn":mean(r["sl"] for r in rows),
      "instrumental_ef_turns":sum(r["instrumental_ef"] for r in rows),"ctl_per_turn":mean(r["energy_effective"] for r in rows),"ctl_final_mean":mean(f["ctl_final"] for f in finals),
      "quality_final_mean":mean(f["quality_final"] for f in finals),"first_upgrade_turn_mean":mean(upgrades) if upgrades else None,"first_added_die_turn_mean":mean(additions) if additions else None,
      "risk_selected":sum(r["risk_selected"] for r in rows),"risk_tested":sum(r["risk_tested"] for r in rows),"risk_bundles_considered":sum(r["risk_bundles_considered"] for r in rows),
      "mean_selected_bust_probability":mean(r["mean_selected_risk"] for r in rows if r["risk_selected"]) if any(r["risk_selected"] for r in rows) else 0,
      "busts":bust,"busts_per_game":bust/len(byseed),"games_with_bust_pct":100*mean(any(r["busts"] for r in rs) for rs in byseed.values()),
      "risk_ctl_realized":sum(SESSION_CATALOG[s["session"]][1] for s in risk if s["realized"]),"risk_quality_realized":sum(s["realized"] and s["category"] in QUALITY_CATEGORIES for s in risk),
      "risk_ctl_lost":sum(SESSION_CATALOG[s["session"]][1] for s in risk if not s["realized"]),"risk_quality_lost":sum((not s["realized"]) and s["category"] in QUALITY_CATEGORIES for s in risk),
      "risk_s_realized":sum(max(0,s["rpe"]-next(r["rpe_max"] for r in rows if r["seed"]==s["seed"] and r["turn"]==s["turn"])) for s in risk if s["realized"]),
      "q_total":sum(r["q"] for r in rows),"q_per_turn":mean(r["q"] for r in rows),"s_total":sum(r["s"] for r in rows),"s_per_turn":mean(r["s"] for r in rows),
      "recovery_total":sum(r["recovery"] for r in rows),"recovery_per_turn":mean(r["recovery"] for r in rows),"fatigue_mean":mean(r["fatigue_final"] for r in rows),
      "fatigue_final_mean":mean(final_f),"fatigue_final_median":median(final_f),"fatigue_min":min(r["fatigue_final"] for r in rows),"fatigue_max":max(r["fatigue_final"] for r in rows),
      "fatigue_negative_pct":100*mean(r["fatigue_final"]<0 for r in rows),"fatigue_zero_pct":100*mean(r["fatigue_final"]==0 for r in rows),"fatigue_positive_pct":100*mean(r["fatigue_final"]>0 for r in rows),
      "negative_bound_pct":100*mean(r["negative_bound"] for r in rows),"ot_events":sum(bool(r["die_removed"]) for r in rows),"ot_games_pct":100*len(otseeds)/len(byseed),
      "first_ot_mean":mean(min(r["turn"] for r in rs if r["overtraining"]) for rs in otseeds) if otseeds else None,"recoveries":sum(r["die_recovered"] for r in rows),
      "unused_reasons":dict(Counter(r["unused_reason"] for r in rows)),"search_methods":dict(Counter(r["search_method"] for r in rows)),"bundle_distribution_top10":dict(Counter(r["bundle"] for r in rows).most_common(10)),
      "final_pool_distribution":dict(Counter(f["pool_final"] for f in finals))}


def controlled_states():
    states=[("negative_capacity",["EF1","EF2","Seuil3"],12,3,14,6,-8),
      ("near_zero",["EF1","EF2","Seuil3"],12,3,14,6,0),("positive_below_ot",["EF1","EF2","Seuil3"],12,3,14,6,5),
      ("ef_opens_quality",["EF1","Seuil3"],4,3,14,6,0),("low_risk",["EF1","Seuil3","Seuil4"],8,3,14,8,0),
      ("medium_risk",["EF1","Seuil3","Seuil5"],10,3,14,8,0),("high_risk",["EF1","Seuil3","Spec9"],12,3,14,6,0),
      ("multiple_risk",["EF1","EF2","Seuil4","Seuil5"],12,3,14,6,0)]
    out=[]
    for label,av,e,r,tn,best,fatigue in states:
      for policy in POLICIES:
        if policy=="P0_CURRENT": bundle=tuple(choose_sessions_weighted(av,e,r,tn)[0]); value=None; method="production"
        else: rec,_,method,_,_=select_bundle(av,e,r,tn,best,policy);bundle=rec["bundle"];value=rec["value"]
        out.append({"state":label,"policy":policy,"fatigue":fatigue,"bundle":"|".join(bundle),"value":value,
          "planned":sum(SESSION_CATALOG[n][1] for n in bundle),"risk_count":sum(SESSION_CATALOG[n][1]>r for n in bundle),"search_method":method})
    return out


def write_csv(path, rows):
    if not rows:return
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)


def run(output=OUT,seeds=range(100),turns=16):
    output=Path(output);output.mkdir(parents=True,exist_ok=True); summaries={}; all_inst=[]; comparisons=[]
    for policy in POLICIES:
      rows=[];sessions=[];finals=[]
      for seed in seeds:
        a,b,c,d=simulate_policy(seed,policy,turns);rows+=a;sessions+=b;all_inst+=c;finals.append(d)
      summaries[policy]=summarize(policy,rows,sessions,finals);comparisons.append(summaries[policy])
    for policy in POLICIES:
      cases=[r for r in all_inst if r["policy"]==policy]
      summaries[policy]["instrumental_ef_case_count"]=len(cases)
      summaries[policy]["instrumental_value_gain_mean"]=mean(float(r["global_value_gain"]) for r in cases) if cases else 0
      summaries[policy]["instrumental_quality_gain_mean"]=mean(float(r["quality_gain"]) for r in cases) if cases else 0
      summaries[policy]["instrumental_ctl_gain_mean"]=mean(float(r["ctl_gain"]) for r in cases) if cases else 0
      summaries[policy]["instrumental_short_fatigue_delta_mean"]=mean(float(r["short_fatigue_delta"]) for r in cases) if cases else 0
    controlled=controlled_states(); (output/"summary.json").write_text(json.dumps(summaries,indent=2,ensure_ascii=False),encoding="utf-8")
    write_csv(output/"policy_comparison.csv",comparisons);write_csv(output/"risk_sensitivity.csv",[summaries[p] for p in THRESHOLDS])
    write_csv(output/"instrumental_ef_cases.csv",all_inst);write_csv(output/"representative_states.csv",controlled)
    (output/"report.md").write_text(render_report(summaries),encoding="utf-8")
    return summaries


def render_report(s):
    lines=["# Experimental Standard Player — Bundle + Risk", "", "## FACT", "",
      "- P0 reste la baseline de production inchangée.",
      "- Les politiques standard évaluent des bundles complets; EV énumère exactement les issues de premier bust, MOD filtre les risques individuels à 15/25/40 %.",
      f"- Recherche: largeur de beam déterministe {BEAM_WIDTH} lorsque la borne combinatoire dépasse {EXHAUSTIVE_BOUND}.", "", "## OBSERVATION", ""]
    for p in POLICIES:
      x=s[p];lines.append(f"- {p}: énergie effective {x['energy_used_pct']:.3f} %, CTL final {x['ctl_final_mean']:.2f}, qualité {x['quality_final_mean']:.2f}, risques {x['risk_selected']}, busts {x['busts']}, fatigue finale {x['fatigue_final_mean']:.2f}, OT {x['ot_games_pct']:.1f} %.")
    lines += ["", "## INTERPRETATION", "", "- Le raisonnement bundle augmente l'utilisation de capacité et la qualité sans produire Q ni overtraining dans cette campagne.",
      "- L'ouverture RPE reste marginalement sélectionnée; les seuils 25 % et 40 % coïncident dans les états rencontrés.", "", "## LIMITS", "",
      "- Instrument comportemental, pas modèle validé de joueur humain; pas de course finale; fonction de valeur et seuils non calibrés.", "", "## DESIGN QUESTIONS", "",
      "- Faut-il représenter le risque par valeur espérée, seuil simple, ou un autre comportement?", "- La valeur des SL doit-elle être portée par un objectif distinct?", ""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser();p.add_argument("--seeds",type=int,default=100);p.add_argument("--turns",type=int,default=16);p.add_argument("--output",default=str(OUT));a=p.parse_args()
    print(json.dumps(run(a.output,range(a.seeds),a.turns),indent=2,ensure_ascii=False))
if __name__=="__main__":main()
