import sys
import os

# Garde-fou : garantit que le dossier du script est dans sys.path, quel que
# soit le répertoire de travail ou la façon dont le script est lancé.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import random
from dice_types import example_pool, pool_tn
from patterns import pattern_name
from dice_result import create_dice_result
from decision_engine import choose_weighted_action, energy_and_fatigue, rank_to_records
from session_effects import session_outcome
from game_logger import write_csv
# Poids par défaut du moteur pondéré. Un w_rpe positif augmente l'utilité des
# options à RPE max attendu plus élevé ; ce n'est donc pas un terme de pénalité.
DEFAULT_WEIGHTS = {
    "w_energy": 1.0,
    "w_sessions": 1.0,
    "w_fatigue": 1.0,
    "w_rpe": 1.0,
}
def get_max_dice():
    return random.choice([4, 5, 6])
def initial_active_size(max_dice):
    return max_dice - 1
def roll_dice(dice_objects):
    faces, values = [], []
    for d in dice_objects:
        face, value = d.roll()
        faces.append(face)
        values.append(value)
    return faces, values
def _apply_action(choice, index, active, reserve_die, faces, values):
    """
    Exécute l'action retenue et retourne (active, faces, values) mis à jour.
    Isolé de play_turn() pour rester testable indépendamment du reste.
    """
    if choice == "add":
        face, value = reserve_die.roll()
        active = active + [reserve_die]
        faces = faces + [face]
        values = values + [value]
    elif choice == "reroll":
        face, value = active[index].roll()
        faces = faces.copy()
        values = values.copy()
        faces[index] = face
        values[index] = value
    elif choice == "add+reroll":
        face, value = reserve_die.roll()
        active = active + [reserve_die]
        faces = faces + [face]
        values = values + [value]
        face2, value2 = active[index].roll()
        faces[index] = face2
        values[index] = value2
    # "keep" : rien à faire, on retourne l'état inchangé.
    return active, faces, values
def play_turn(turn_id, weights=DEFAULT_WEIGHTS):
    """
    Joue un tour complet et retourne (turn_row, decision_rows) :
    - turn_row      : dict résumant le tour (une ligne pour turns.csv).
    - decision_rows : liste de dicts, une par option évaluée par le moteur
                       pondéré ce tour-ci (des lignes pour decisions.csv).
    """
    max_dice = get_max_dice()
    active_size = initial_active_size(max_dice)
    pool = example_pool(max_dice)
    tn = pool_tn(pool)
    active = pool[:active_size]
    reserve_die = pool[active_size]
    faces, values = roll_dice(active)
    initial_faces = faces.copy()
    initial_pattern = pattern_name(faces)
    initial_sum = sum(values)
    choice, index, ranked = choose_weighted_action(
        active, reserve_die, faces, max_dice, tn, **weights
    )
    decision_records = rank_to_records(ranked, weights)
    for record in decision_records:
        record["turn"] = turn_id
        record["is_chosen"] = (record["action"] == choice and record["index"] == index)
    best_utility = decision_records[0]["utility"]
    runner_up_utility = decision_records[1]["utility"] if len(decision_records) > 1 else best_utility
    utility_gap = round(best_utility - runner_up_utility, 3)
    active, faces, values = _apply_action(choice, index, active, reserve_die, faces, values)
    result = create_dice_result(active, faces, values)
    outcome = session_outcome(faces, values, max_dice)
    energy, fatigue = energy_and_fatigue(outcome["total"], tn)
    turn_row = {
        "turn": turn_id,
        "max_dice": max_dice,
        "pool_sizes": "-".join(str(d.size) for d in pool),
        "tn": tn,
        "initial_faces": "-".join(map(str, initial_faces)),
        "initial_pattern": initial_pattern,
        "initial_sum": initial_sum,
        "chosen_action": choice,
        "chosen_index": index,
        "utility_gap": utility_gap,
        "final_faces": "-".join(map(str, result.faces)),
        "final_pattern": result.pattern,
        "final_sum": result.total,
        "sessions": outcome["sessions"],
        "bonus_pool": outcome["bonus_pool"],
        "dice_used": "-".join(map(str, outcome["dice_used"])),
        "dice_dropped": outcome["dice_dropped"],
        "rpe_max": outcome["rpe_max"],
        "energy": energy,
        "fatigue": fatigue,
    }
    return turn_row, decision_records
def run_simulation(n_turns=50, weights=DEFAULT_WEIGHTS, seed=42):
    random.seed(seed)
    turns, decisions = [], []
    for turn_id in range(1, n_turns + 1):
        turn_row, decision_rows = play_turn(turn_id, weights)
        turns.append(turn_row)
        decisions.extend(decision_rows)
    return turns, decisions
def print_summary(turns):
    """
    Résumé console minimal (contrôle rapide, pas un journal détaillé).
    L'analyse fine se fait dans turns.csv / decisions.csv.
    """
    n = len(turns)
    avg_energy = sum(t["energy"] for t in turns) / n
    avg_fatigue = sum(t["fatigue"] for t in turns) / n
    avg_sessions = sum(t["sessions"] for t in turns) / n
    avg_gap = sum(t["utility_gap"] for t in turns) / n
    action_counts = {}
    for t in turns:
        action_counts[t["chosen_action"]] = action_counts.get(t["chosen_action"], 0) + 1
    print(f"{n} tours simulés.")
    print(f"Énergie moyenne : {avg_energy:.2f}")
    print(f"Fatigue moyenne : {avg_fatigue:.2f}")
    print(f"Séances moyennes : {avg_sessions:.2f}")
    print(f"Écart d'utilité moyen (1er vs 2e choix) : {avg_gap:.2f}")
    print(f"Répartition des actions choisies : {action_counts}")
if __name__ == "__main__":
    turns, decisions = run_simulation(n_turns=50)
    write_csv("turns.csv", turns)
    write_csv("decisions.csv", decisions)
    print_summary(turns)
    print("\nDétails -> turns.csv (1 ligne/tour), decisions.csv (1 ligne/option évaluée par tour)")