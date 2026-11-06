"""
Simulation multi-tours pour UN joueur : le moteur de dés produit le budget,
puis le joueur choisit des séances selon les règles de progression.

Le RNG est injectable depuis la simulation pour rejouer intégralement les
lancers de dés et de risque. Les changements de pool dus à la progression
restent appliqués au début du tour suivant.
"""
import sys
import os

# Garde-fou pour les imports plats lors d'un lancement depuis un autre dossier.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collections import defaultdict, deque
import random
from dice_types import pool_tn
from decision_engine import choose_weighted_action, energy_and_fatigue
from session_effects import session_outcome
from patterns import pattern_name
from sessions_catalog import SESSION_CATALOG
from session_selector import choose_sessions_weighted, DEFAULT_SESSION_WEIGHTS
from session_resolution import post_bust_redistribution_options, resolve_session_plan
from session_risk import first_bust_index
from dice_progression import DEFAULT_UPGRADE_WEIGHTS
from player_state import Player
from game_logger import write_csv

DEFAULT_WEIGHTS = {"w_energy": 1.0, "w_sessions": 1.0, "w_fatigue": 1.0, "w_rpe": 1.0}


def choose_replacement_ef_greedy(options):
    """Simulation policy only: greedily fills redistribution with safe EF."""
    candidates = sorted(options.legal_ef, key=lambda name: (-SESSION_CATALOG[name][1], name))
    remaining = options.replacement_energy
    chosen = []
    while len(chosen) < options.replacement_slots:
        affordable = next((name for name in candidates if SESSION_CATALOG[name][1] <= remaining), None)
        if affordable is None:
            break
        chosen.append(affordable)
        remaining -= SESSION_CATALOG[affordable][1]
    return tuple(chosen)


def _session_occurrence_traces(completed_sessions, replacement_sessions, trace):
    """Associate each completed planned occurrence with its own selector trace."""
    trace_by_name = defaultdict(deque)
    for trace_index, step in enumerate(trace):
        trace_by_name[step["session"]].append((trace_index, step))

    planned_count = len(completed_sessions) - len(replacement_sessions)
    occurrences = []
    for name in completed_sessions[:planned_count]:
        trace_index, step = trace_by_name[name].popleft() if trace_by_name[name] else (None, {})
        occurrences.append({"session": name, "origin": "planned",
                            "trace_index": trace_index, "trace": step})
    for name in replacement_sessions:
        occurrences.append({"session": name, "origin": "redistribution",
                            "trace_index": None, "trace": {}})
    return tuple(occurrences)


def _split_active_reserve(dice_objects):
    """Keep the smallest die in reserve; on ties, the last die remains reserve."""
    reserve_idx = min(range(len(dice_objects)), key=lambda i: (dice_objects[i].size, -i))
    reserve_die = dice_objects[reserve_idx]
    return [d for i, d in enumerate(dice_objects) if i != reserve_idx], reserve_die


def roll_turn_budget(dice_pool, weights=DEFAULT_WEIGHTS, rng=None):
    """Roll the persistent dice pool using the supplied random generator."""
    dice_objects = dice_pool.as_dice_objects()
    max_dice = len(dice_objects)
    active, reserve_die = _split_active_reserve(dice_objects)
    tn = pool_tn(dice_objects)
    faces, values = [], []
    for die in active:
        face, value = die.roll(rng=rng)
        faces.append(face)
        values.append(value)
    choice, index, _ = choose_weighted_action(active, reserve_die, faces, max_dice, tn, **weights)
    if choice == "add":
        face, value = reserve_die.roll(rng=rng)
        faces.append(face)
        values.append(value)
    elif choice == "reroll":
        face, value = active[index].roll(rng=rng)
        faces[index], values[index] = face, value
    elif choice == "add+reroll":
        face, value = reserve_die.roll(rng=rng)
        faces.append(face)
        values.append(value)
        face, value = active[index].roll(rng=rng)
        faces[index], values[index] = face, value
    outcome = session_outcome(faces, values, max_dice)
    return {
        "energy_budget": outcome["total"], "rpe_max": outcome["rpe_max"],
        "quality_sessions_from_roll": outcome["sessions"], "tn": tn,
        "pool_size": max_dice, "final_faces": faces, "final_values": values,
        "pattern": pattern_name(faces), "action_chosen": choice,
    }


def play_player_turn(turn_id, player, weights=DEFAULT_WEIGHTS,
                     session_weights=None, upgrade_weights=None, bust_index=None,
                     risk_roll_face=None, rng=None):
    """Resolve one Training turn; pass the same RNG through dice and bust rolls."""
    player.dice_pool.maybe_add_dice(player.cumulative_ctl)
    player.dice_pool.maybe_upgrade(player.progress.quality_total,
                                   upgrade_weights or DEFAULT_UPGRADE_WEIGHTS)
    roll = roll_turn_budget(player.dice_pool, weights, rng=rng)
    available = player.progress.available_sessions()
    tentable = player.progress.tentable_sessions()
    chosen, trace = choose_sessions_weighted(
        tentable, roll["energy_budget"], roll["rpe_max"], roll["tn"],
        quality_limit=roll["quality_sessions_from_roll"],
        weights=session_weights or DEFAULT_SESSION_WEIGHTS,
        best_die_size=max(player.dice_pool.sizes),
    )
    if bust_index is None:
        bust_index = first_bust_index(
            chosen, roll["rpe_max"], player.dice_pool.sizes,
            roll_face=risk_roll_face, rng=rng,
        )
    replacements = ()
    if bust_index is not None:
        options = post_bust_redistribution_options(
            chosen, available, roll["rpe_max"], bust_index,
        )
        replacements = choose_replacement_ef_greedy(options)
    resolution = resolve_session_plan(chosen, available, roll["rpe_max"], bust_index, replacements)
    ctl = resolution.energy_effective
    _, fatigue = energy_and_fatigue(ctl, roll["tn"])
    player.cumulative_ctl += ctl

    session_rows = []
    occurrences = _session_occurrence_traces(
        resolution.completed_sessions, resolution.replacement_sessions, trace,
    )
    for occurrence_index, occurrence in enumerate(occurrences, start=1):
        name, step = occurrence["session"], occurrence["trace"]
        category, rpe = SESSION_CATALOG[name]
        session_rows.append({
            "turn": turn_id, "session": name, "occurrence_index": occurrence_index,
            "origin": occurrence["origin"], "trace_index": occurrence["trace_index"],
            "category": category, "rpe": rpe, "energy_cost": rpe,
            "marginal_utility": step.get("marginal_utility"),
            "alternatives_considered": step.get("alternatives_considered"),
            "note": ("redistribution_EF" if occurrence["origin"] == "redistribution"
                     else step.get("note", "")),
        })
        player.progress.record_session(name)

    turn_row = {
        "turn": turn_id, "tn": roll["tn"], "pool_size": roll["pool_size"],
        "dice_pool_sizes": "-".join(str(s) for s in player.dice_pool.sizes),
        "upgrades_used": player.dice_pool.upgrades_used,
        "dice_added": player.dice_pool.dice_added,
        "dice_final_roll": "-".join(str(v) for v in roll["final_values"]),
        "pattern_detected": roll["pattern"], "dice_action": roll["action_chosen"],
        "energy_budget": roll["energy_budget"], "rpe_max": roll["rpe_max"],
        "quality_sessions_from_roll": roll["quality_sessions_from_roll"],
        "sessions_chosen": "-".join(chosen) if chosen else "",
        "nb_sessions": len(resolution.counted_sessions),
        "sessions_completed": "-".join(resolution.completed_sessions),
        "sessions_cancelled": "-".join(resolution.cancelled_sessions),
        "energy_lost": resolution.energy_lost, "ctl": ctl,
        "cumulative_ctl": player.cumulative_ctl, "fatigue_turn": fatigue,
        "ef_total": player.progress.ef_total, "quality_total": player.progress.quality_total,
        "max_unlocked_rpe": max((SESSION_CATALOG[n][1] for n in available), default=0),
    }
    return turn_row, session_rows


def run_player_simulation(n_turns=12, weights=DEFAULT_WEIGHTS,
                          session_weights=None, upgrade_weights=None, seed=42, rng=None):
    """Run a player simulation with an isolated, seedable random stream.

    ``rng`` overrides ``seed`` and may be any object exposing ``randint``.
    The default path does not mutate Python's module-global random state.
    """
    if rng is not None and seed != 42:
        raise ValueError("provide either rng or a non-default seed, not both")
    rng = rng if rng is not None else random.Random(seed)
    player = Player()
    turns, sessions = [], []
    cumulative_fatigue = 0
    for turn_id in range(1, n_turns + 1):
        turn_row, session_rows = play_player_turn(
            turn_id, player, weights, session_weights, upgrade_weights, rng=rng,
        )
        cumulative_fatigue += turn_row["fatigue_turn"]
        turn_row["cumulative_fatigue"] = cumulative_fatigue
        turns.append(turn_row)
        sessions.extend(session_rows)
    return turns, sessions, player


def print_summary(turns, player):
    print(f"{len(turns)} tours simulés pour 1 joueur.\n")
    print(f"{'Tour':>4} {'TN':>6} {'Pool':>10} {'Énergie':>8} {'RPE max':>8} "
          f"{'Qual.dés':>8} {'Séances':30} {'CTL':>5} {'CTL cum.':>9} "
          f"{'Fatigue':>8} {'Fatigue cum.':>13}")
    for t in turns:
        print(f"{t['turn']:>4} {t['tn']:>6} {t['dice_pool_sizes']:>10} "
              f"{t['energy_budget']:>8} {t['rpe_max']:>8} {t['quality_sessions_from_roll']:>8} "
              f"{t['sessions_chosen']:30} {t['ctl']:>5} {t['cumulative_ctl']:>9} "
              f"{t['fatigue_turn']:>8} {t['cumulative_fatigue']:>13}")
    print(f"\nSéances EF cumulées : {player.progress.ef_total}")
    print(f"Séances de qualité cumulées : {player.progress.quality_total}")
    print(f"Pool de dés final : {player.dice_pool.sizes} "
          f"(améliorations utilisées : {player.dice_pool.upgrades_used}/4, "
          f"dés ajoutés : {player.dice_pool.dice_added}/2)")
    print(f"Historique des réalisations : {dict(player.progress.completions)}")


if __name__ == "__main__":
    turns, sessions, player = run_player_simulation(n_turns=12)
    write_csv("player_turns.csv", turns)
    write_csv("player_sessions.csv", sessions)
    print_summary(turns, player)
    print("\nDétails -> player_turns.csv (1 ligne/tour), "
          "player_sessions.csv (1 ligne/séance réalisée)")
