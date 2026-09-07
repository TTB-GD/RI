"""
Simulation multi-tours pour UN joueur : à chaque tour, le moteur de dés
existant (dice_types/decision_engine/session_effects) détermine l'énergie et
le RPE max disponibles ce tour-ci, à partir du pool de dés PERSISTANT du
joueur (`player_state.Player.dice_pool`, plus un simple tirage aléatoire
comme avant) ; le joueur choisit ensuite ses séances d'entraînement sous
les contraintes de progression/déblocage (`session_selector`).
Pool de dés : contrairement à la version précédente (taille de pool
re-tirée au hasard à CHAQUE tour via `get_max_dice`), le pool est
maintenant un état qui persiste et évolue pour un même joueur — cf.
`dice_progression.PlayerDicePool` (paliers CTL 50/100, améliorations tous
les 8 séances de qualité). Les évolutions dues sont appliquées en DÉBUT de
tour, à partir de l'état accumulé à la fin du tour précédent (même
principe que le déblocage de séances : rien de nouveau n'est disponible le
tour même où le seuil est franchi).
CTL (forme) du tour = somme des coûts en énergie des séances CHOISIES (pas
l'énergie totale disponible : le joueur peut ne pas tout dépenser s'il n'a
pas de séance débloquée/compatible pour l'utiliser). CTL CUMULÉ = somme du
CTL de chaque tour joué, piste les paliers 50/100 du pool de dés.
Fatigue : calculée via la même fonction que pour le moteur de dés seul
(energy_and_fatigue, suite quasi-Fibonacci selon l'écart au TN), appliquée
au CTL du tour. Cumulée d'un tour à l'autre par simple somme (hypothèse : pas
de récupération/décroissance modélisée pour l'instant).
"""
import sys
import os

# Garde-fou : garantit que le dossier du script est dans sys.path, quel que
# soit le répertoire de travail ou la façon dont le script est lancé (IDE,
# double-clic, terminal depuis un autre dossier...). Évite la classe de bug
# rencontrée ici (un import résolu par erreur vers un chemin absolu du type
# `RI_clean4.RI.module` au lieu de l'import plat `module` utilisé partout
# ailleurs dans ce projet, qui n'est PAS un package installé).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import random
from dice_types import pool_tn
from decision_engine import choose_weighted_action, energy_and_fatigue
from session_effects import session_outcome
from patterns import pattern_name
from sessions_catalog import SESSION_CATALOG
from session_selector import choose_sessions_weighted, DEFAULT_SESSION_WEIGHTS
from dice_progression import DEFAULT_UPGRADE_WEIGHTS
from player_state import Player
from game_logger import write_csv
DEFAULT_WEIGHTS = {"w_energy": 1.0, "w_sessions": 1.0, "w_fatigue": 1.0, "w_rpe": 1.0}
def _split_active_reserve(dice_objects):
    """
    Sépare le pool en (dés actifs, dé de réserve) : le dé de réserve est
    celui de plus petite taille (à égalité, le dernier ajouté, donc l'index
    le plus élevé, reste réserve — les dés améliorés sont donc préférés en
    actif, cohérent avec l'hypothèse déjà actée dans `example_pool`).
    """
    reserve_idx = min(range(len(dice_objects)), key=lambda i: (dice_objects[i].size, -i))
    reserve_die = dice_objects[reserve_idx]
    active = [d for i, d in enumerate(dice_objects) if i != reserve_idx]
    return active, reserve_die
def roll_turn_budget(dice_pool, weights=DEFAULT_WEIGHTS):
    """
    Réutilise le moteur de dés existant sur le pool PERSISTANT du joueur
    (plus de taille de pool aléatoire par tour). Retourne un dict avec tout
    ce qui doit être journalisé (énergie, RPE max, TN, tirage final,
    motif détecté, action retenue par le moteur pondéré côté dés).
    """
    dice_objects = dice_pool.as_dice_objects()
    max_dice = len(dice_objects)
    active, reserve_die = _split_active_reserve(dice_objects)
    tn = pool_tn(dice_objects)
    faces, values = [], []
    for d in active:
        face, value = d.roll()
        faces.append(face)
        values.append(value)
    choice, index, ranked = choose_weighted_action(active, reserve_die, faces, max_dice, tn, **weights)
    if choice == "add":
        face, value = reserve_die.roll()
        faces.append(face)
        values.append(value)
    elif choice == "reroll":
        face, value = active[index].roll()
        faces[index] = face
        values[index] = value
    elif choice == "add+reroll":
        face, value = reserve_die.roll()
        faces.append(face)
        values.append(value)
        face2, value2 = active[index].roll()
        faces[index] = face2
        values[index] = value2
    outcome = session_outcome(faces, values, max_dice)
    return {
        "energy_budget": outcome["total"],
        "rpe_max": outcome["rpe_max"],
        "quality_sessions_from_roll": outcome["sessions"],
        "tn": tn,
        "pool_size": max_dice,
        "final_faces": faces,
        "final_values": values,
        "pattern": pattern_name(faces),
        "action_chosen": choice,
    }
def play_player_turn(turn_id, player, weights=DEFAULT_WEIGHTS,
                      session_weights=None, upgrade_weights=None):
    """
    Joue un tour pour un joueur et retourne (turn_row, session_rows) :
    - turn_row     : dict résumant le tour (tirage, CTL, fatigue, état de
                       progression du pool et des séances) pour player_turns.csv.
    - session_rows : une ligne par séance réalisée ce tour, pour
                       player_sessions.csv (inclut la trace du moteur
                       pondéré : utilité marginale ayant motivé le choix).
    Trois jeux de poids indépendants, réglables séparément :
        weights          -> moteur de dés (choose_weighted_action)
        session_weights   -> moteur de séances (choose_sessions_weighted)
        upgrade_weights    -> moteur d'amélioration du pool (choose_die_to_upgrade)
    """
    # Évolutions du pool dues à la fin du tour précédent, appliquées AVANT
    # le tirage de ce tour (même principe que le déblocage de séances).
    player.dice_pool.maybe_add_dice(player.cumulative_ctl)
    player.dice_pool.maybe_upgrade(player.progress.quality_total, upgrade_weights or DEFAULT_UPGRADE_WEIGHTS)
    roll = roll_turn_budget(player.dice_pool, weights)
    available = player.progress.available_sessions()
    chosen, trace = choose_sessions_weighted(
        available, roll["energy_budget"], roll["rpe_max"], roll["tn"],
        weights=session_weights or DEFAULT_SESSION_WEIGHTS,
    )
    ctl = sum(SESSION_CATALOG[name][1] for name in chosen)
    _, fatigue = energy_and_fatigue(ctl, roll["tn"])
    player.cumulative_ctl += ctl
    session_rows = []
    for name, step in zip(chosen, trace):
        category, rpe = SESSION_CATALOG[name]
        session_rows.append({
            "turn": turn_id,
            "session": name,
            "category": category,
            "rpe": rpe,
            "energy_cost": rpe,
            "marginal_utility": step["marginal_utility"],
            "alternatives_considered": step["alternatives_considered"],
            "note": step["note"],
        })
        player.progress.record_session(name)
    turn_row = {
        "turn": turn_id,
        "tn": roll["tn"],
        "pool_size": roll["pool_size"],
        "dice_pool_sizes": "-".join(str(s) for s in player.dice_pool.sizes),
        "upgrades_used": player.dice_pool.upgrades_used,
        "dice_added": player.dice_pool.dice_added,
        "dice_final_roll": "-".join(str(v) for v in roll["final_values"]),
        "pattern_detected": roll["pattern"],
        "dice_action": roll["action_chosen"],
        "energy_budget": roll["energy_budget"],
        "rpe_max": roll["rpe_max"],
        "quality_sessions_from_roll": roll["quality_sessions_from_roll"],
        "sessions_chosen": "-".join(chosen) if chosen else "",
        "nb_sessions": len(chosen),
        "ctl": ctl,
        "cumulative_ctl": player.cumulative_ctl,
        "fatigue_turn": fatigue,
        "ef_total": player.progress.ef_total,
        "quality_total": player.progress.quality_total,
        "max_unlocked_rpe": max((SESSION_CATALOG[n][1] for n in available), default=0),
    }
    return turn_row, session_rows
def run_player_simulation(n_turns=12, weights=DEFAULT_WEIGHTS,
                           session_weights=None, upgrade_weights=None, seed=42):
    random.seed(seed)
    player = Player()
    turns, sessions = [], []
    cumulative_fatigue = 0
    for turn_id in range(1, n_turns + 1):
        turn_row, session_rows = play_player_turn(
            turn_id, player, weights, session_weights, upgrade_weights,
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