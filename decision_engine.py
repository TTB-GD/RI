"""
Deux briques, liées mais distinctes :

1. energy_and_fatigue(raw_total, tn) : convertit une somme brute de dés en
   (énergie à dépenser, fatigue générée), selon la position par rapport au TN.

2. choose_weighted_action(...) : un moteur de décision qui remplace le
   simple seuil sur l'écart au TN (action_evaluator.choose_best_action) par
   une utilité pondérée entre l'énergie/fatigue attendues et les séances de
   qualité attendues. Gère naturellement le cas du dépassement (pas besoin
   de branche spéciale : "keep" avec un mauvais total aura simplement une
   utilité plus faible que d'autres options).
"""

import math

from session_effects import session_outcome


def _round_half_away_from_zero(x):
    """
    Arrondi classique (0.5 s'arrondit toujours vers l'extérieur), contrairement
    à round() de Python qui utilise l'arrondi bancaire (round(0.5)=0,
    round(1.5)=2 -> incohérent selon parité). Important ici car TN peut être
    fractionnaire (ex: 17.5 pour un pool de 5 d6) et cette incohérence serait
    difficile à justifier auprès des joueurs.
    """
    return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)


def fibonacci(k):
    """F(0)=0, F(1)=1, F(2)=1, F(3)=2, F(4)=3, F(5)=5, F(6)=8, F(7)=13, ..."""
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def recovery_curve(offset):
    """
    Récupération selon l'écart sous le TN.

    offset = spend - tn

    -2 et -3 : charge faible mais neutre
    <= -4    : récupération progressive
    """
    recovery_fib = {
        -4: 1,
        -5: 1,
        -6: 2,
        -7: 2,
        -8: 3,
        -9: 5,
        -10: 8,
    }
    return recovery_fib.get(offset, 8)


def energy_and_fatigue(spend, tn):
    """
    Nouvelle architecture (remplace l'ancienne courbe plafonnée à TN) :

    - L'énergie n'est PLUS plafonnée : énergie = spend, telle quelle, sans
      bonus ni malus.
    - La fatigue suit une suite quasi-Fibonacci selon la proximité au TN :

          offset = spend - tn
          offset <= -2  : fatigue = 0
          offset == -1  : fatigue = 1
          offset == 0   : fatigue = 2   (TN pile)
          offset == 1   : fatigue = 3
          offset == 2   : fatigue = 5
          offset == 3   : fatigue = 8
          offset == 4   : fatigue = 13  (et ainsi de suite)

      Concrètement : fatigue = fibonacci(offset + 3) pour offset >= -1.
    """
    energy = spend
    offset = _round_half_away_from_zero(spend - tn)

    if offset >= -1:
        fatigue = fibonacci(offset + 3)
    elif offset in (-2, -3):
        fatigue = 0
    else:
        fatigue = -recovery_curve(offset)

    return energy, fatigue


def _enumerate_outcomes(faces, reroll_index, reroll_die_size, add_die):
    """Génère tous les jeux de faces finales possibles pour une action donnée."""
    reroll_range = range(1, reroll_die_size + 1) if reroll_index is not None else [None]
    add_range = range(1, add_die.size + 1) if add_die is not None else [None]

    outcomes = []
    for r in reroll_range:
        for a in add_range:
            new_faces = faces.copy()
            if reroll_index is not None:
                new_faces[reroll_index] = r
            if add_die is not None:
                new_faces = new_faces + [a]
            outcomes.append(new_faces)
    return outcomes


def evaluate_action(faces, active_dice, reserve_die, max_dice, tn,
                     reroll_index=None, do_add=False):
    """
    Calcule les métriques moyennes d'une action (énumération complète et
    exacte de ses issues équiprobables, pas de simulation) :
    énergie attendue, fatigue attendue, séances attendues, proba de bonus_pool.
    """
    reroll_die_size = active_dice[reroll_index].size if reroll_index is not None else None
    add_die = reserve_die if do_add else None

    outcomes = _enumerate_outcomes(faces, reroll_index, reroll_die_size, add_die)

    energies, fatigues, sessions_list, bonus_flags, rpe_list = [], [], [], [], []
    for new_faces in outcomes:
        outcome = session_outcome(new_faces, new_faces, max_dice)
        energy, fatigue = energy_and_fatigue(outcome["total"], tn)
        energies.append(energy)
        fatigues.append(fatigue)
        sessions_list.append(outcome["sessions"])
        bonus_flags.append(1 if outcome["bonus_pool"] else 0)
        rpe_list.append(outcome["rpe_max"])

    n = len(outcomes)
    return {
        "expected_energy": sum(energies) / n,
        "expected_fatigue": sum(fatigues) / n,
        "expected_sessions": sum(sessions_list) / n,
        "bonus_pool_probability": sum(bonus_flags) / n,
        "expected_rpe_max": sum(rpe_list) / n,
    }


def choose_weighted_action(active_dice, reserve_die, faces, max_dice, tn,
                            w_energy=1.0, w_sessions=1.0, w_fatigue=1.0, w_rpe=1.0):
    """
    Évalue toutes les actions possibles (keep, reroll x chaque dé actif,
    add, add+reroll x chaque dé actif) et retourne celle qui maximise :

        utilité = w_energy   * énergie_attendue
                + w_sessions * séances_attendues
                + w_rpe      * RPE_max_attendu
                - w_fatigue  * fatigue_attendue

    Retourne (choix, index, classement) où classement est la liste complète
    des options évaluées, triée par utilité décroissante (pour audit/debug).
    """
    candidates = []

    m = evaluate_action(faces, active_dice, reserve_die, max_dice, tn)
    candidates.append(("keep", None, m))

    for i in range(len(active_dice)):
        m = evaluate_action(faces, active_dice, reserve_die, max_dice, tn, reroll_index=i)
        candidates.append(("reroll", i, m))

    m = evaluate_action(faces, active_dice, reserve_die, max_dice, tn, do_add=True)
    candidates.append(("add", None, m))

    for i in range(len(active_dice)):
        m = evaluate_action(faces, active_dice, reserve_die, max_dice, tn,
                             reroll_index=i, do_add=True)
        candidates.append(("add+reroll", i, m))

    def utility(m):
        return (w_energy * m["expected_energy"]
                + w_sessions * m["expected_sessions"]
                + w_rpe * m["expected_rpe_max"]
                - w_fatigue * m["expected_fatigue"])

    ranked = sorted(candidates, key=lambda c: utility(c[2]), reverse=True)
    best_choice, best_index, _ = ranked[0]
    return best_choice, best_index, ranked


def rank_to_records(ranked, weights):
    """
    Convertit le classement retourné par choose_weighted_action en une liste
    de dicts plats, prête à être journalisée (CSV/JSON).
    """
    def utility(m):
        return (weights["w_energy"] * m["expected_energy"]
                + weights["w_sessions"] * m["expected_sessions"]
                + weights["w_rpe"] * m["expected_rpe_max"]
                - weights["w_fatigue"] * m["expected_fatigue"])

    records = []
    for rank, (choice, index, m) in enumerate(ranked, start=1):
        records.append({
            "rank": rank,
            "action": choice,
            "index": index,
            "expected_energy": round(m["expected_energy"], 3),
            "expected_fatigue": round(m["expected_fatigue"], 3),
            "expected_sessions": round(m["expected_sessions"], 3),
            "expected_rpe_max": round(m["expected_rpe_max"], 3),
            "bonus_pool_probability": round(m["bonus_pool_probability"], 3),
            "utility": round(utility(m), 3),
        })
    return records
