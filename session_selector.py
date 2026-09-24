"""
Moteur de décision PONDÉRÉ pour le choix des séances d'un tour.

Remplace l'heuristique gloutonne de `turn_planner.choose_sessions_for_turn`
(qui ne maximisait que le RPE de chaque séance choisie, une à une, tant que
c'était affordable) par un choix qui arbitre explicitement entre plusieurs
objectifs — même esprit que `decision_engine.choose_weighted_action` côté dés :

    utilité(combo) = + w_sessions * séances_de_qualité(combo)
                      + w_rpe      * rpe_moyen(combo) / rpe_max
                      + w_energy   * énergie_utilisée(combo) / energy_budget
                      - w_fatigue  * fatigue(énergie_utilisée, tn)

La fatigue réutilise `decision_engine.energy_and_fatigue` : même courbe
(quasi-Fibonacci autour du TN) que pour le résultat des dés, pour que
"dépenser de l'énergie" ait un coût cohérent, qu'elle vienne d'un total de
dés gardé tel quel ou d'une somme de séances choisies.

RÈGLES DU JEU appliquées comme contraintes DURES (jamais arbitrées par les
poids, seulement filtrées) :
    - énergie  : somme des coûts (RPE) des séances choisies <= energy_budget.
    - risque   : RPE Max délimite la zone sûre ; une qualité au-dessus reste
                 possible sauf si son seuil atteint la taille du meilleur dé.
    - qualité  : contrainte STRICTE PAR TOUR (pas cumulative) — le nombre de
                 séances de qualité choisies CE TOUR ne peut jamais dépasser
                 le nombre de séances EF choisies CE TOUR. Un stock d'EF
                 réalisées les tours précédents ne finance rien : chaque
                 tour doit se suffire à lui-même sur ce ratio.
    - D99      : le nombre de qualités planifiées, SL comprise, ne dépasse
                 jamais le plafond obtenu aux dés.
    - répétition: une entrée qualité ne peut apparaître qu'une fois ; les EF
                 restent répétables. Une seule SL au total reste autorisée.
    - quantité : au plus MAX_SESSIONS_PER_TURN séances par tour.
Les poids (w_energy, w_sessions, w_fatigue, w_rpe) n'interviennent QUE pour
départager les combinaisons qui respectent déjà toutes ces contraintes.

PRIORITÉ SORTIE LONGUE : une SL doit être casée dès que possible (dans la
limite d'1/tour). Comme la contrainte qualité<=EF est maintenant stricte
par tour, une SL (catégorie qualité) exige qu'au moins une EF soit choisie
le MÊME tour pour ouvrir le quota. `_prioritize_long_run` traite donc
ce cas en préambule : si une SL est accessible et qu'une EF est affordable,
les deux sont ajoutées avant de laisser le moteur pondéré arbitrer le reste
du budget — plutôt que de laisser la SL être noyée dans la comparaison
d'utilité marginale et potentiellement jamais choisie.

STRATÉGIE DE RECHERCHE : énumérer tous les bundles possibles est
combinatoire (EF répétables, jusqu'à 7 séances) et inutile ici.
On construit la sélection pas à pas : à CHAQUE étape, on ajoute la séance
qui maximise l'UTILITÉ MARGINALE (pas juste le RPE brut comme l'ancien
_best_affordable), et on s'arrête dès que même la meilleure option
disponible dégraderait l'utilité — au lieu de remplir jusqu'à épuisement
du budget comme le faisait l'ancien code. Optimum local, pas global, mais
cohérent avec le choix déjà fait côté dés ("moteur pondéré, pas recherche
exhaustive").
"""
from dataclasses import dataclass, field

from decision_engine import energy_and_fatigue
from sessions_catalog import SESSION_CATALOG, QUALITY_CATEGORIES
from session_risk import is_risk_tentable

MAX_SESSIONS_PER_TURN = 7
SINGLE_PER_TURN_CATEGORIES = {"SL"}  # catégories limitées à 1 occurrence / tour

# Poids par défaut : équirépartis, à ajuster/tester comme DEFAULT_WEIGHTS
# du moteur de dés. w_fatigue soustrait ; w_rpe positif favorise les séances
# à intensité (RPE) plus élevée. Les autres termes s'additionnent.
DEFAULT_SESSION_WEIGHTS = {
    "w_energy": 3.0,
    "w_sessions": 1.5,
    "w_fatigue": 0.25,
    "w_rpe": 0.25,
}


@dataclass
class _SelectionState:
    """État mutable d'une construction gloutonne en cours (lisibilité)."""
    chosen: list = field(default_factory=list)   # noms des séances retenues ce tour
    energy_used: int = 0
    ef_this_turn: int = 0                         # règle stricte : compteurs remis à 0 chaque tour
    quality_this_turn: int = 0
    used_quality_names: set = field(default_factory=set)
    used_single_categories: set = field(default_factory=set)


def _is_affordable(name, state, energy_budget, rpe_max, quality_limit,
                   best_die_size=None):
    """Contraintes DURES : la séance `name` peut-elle rejoindre `state` ?"""
    category, rpe = SESSION_CATALOG[name]
    if len(state.chosen) >= MAX_SESSIONS_PER_TURN:
        return False
    if rpe > rpe_max:
        if category not in QUALITY_CATEGORIES:
            return False
        if best_die_size is None or not is_risk_tentable(
            name, rpe_max, best_die_size
        ):
            return False
    if state.energy_used + rpe > energy_budget:
        return False
    if category in SINGLE_PER_TURN_CATEGORIES and category in state.used_single_categories:
        return False
    if category in QUALITY_CATEGORIES:
        if name in state.used_quality_names:
            return False
        if state.quality_this_turn >= quality_limit:
            return False
        if state.quality_this_turn + 1 > state.ef_this_turn:
            return False
    return True


def _commit(name, state):
    """Ajoute définitivement `name` à l'état de sélection (met à jour tous les compteurs)."""
    category, rpe = SESSION_CATALOG[name]
    state.chosen.append(name)
    state.energy_used += rpe
    if category in QUALITY_CATEGORIES:
        state.quality_this_turn += 1
        state.used_quality_names.add(name)
    else:
        state.ef_this_turn += 1
    if category in SINGLE_PER_TURN_CATEGORIES:
        state.used_single_categories.add(category)


def _prioritize_long_run(available_session_names, state, energy_budget, rpe_max,
                         quality_limit, trace, best_die_size=None):
    """
    Case une Sortie Longue dès que possible (au plus 1/tour). Sous la règle
    stricte qualité<=EF PAR TOUR, une SL exige une EF dans le même tour pour
    ouvrir le quota : on ajoute donc la meilleure EF affordable, PUIS la
    meilleure SL affordable, avant que le moteur pondéré ne traite le reste.
    Ne force rien si aucune SL n'est débloquée, ou si aucune EF n'est
    affordable pour lui ouvrir le quota.
    """
    if quality_limit <= 0:
        return

    sl_candidates = [n for n in available_session_names if SESSION_CATALOG[n][0] == "SL"]
    if not sl_candidates:
        return

    ef_candidates = [n for n in available_session_names if SESSION_CATALOG[n][0] == "EF"]
    affordable_ef = [
        n for n in ef_candidates
        if _is_affordable(n, state, energy_budget, rpe_max, quality_limit, best_die_size)
    ]
    if not affordable_ef:
        return  # pas d'EF possible ce tour -> pas de quota qualité -> pas de SL non plus
    best_ef = max(affordable_ef, key=lambda n: SESSION_CATALOG[n][1])
    _commit(best_ef, state)
    trace.append({
        "session": best_ef, "category": "EF", "rpe": SESSION_CATALOG[best_ef][1],
        "marginal_utility": None, "energy_used_running": state.energy_used,
        "alternatives_considered": len(affordable_ef), "note": "priorite_SL:EF_prealable",
    })

    affordable_sl = [
        n for n in sl_candidates
        if _is_affordable(n, state, energy_budget, rpe_max, quality_limit, best_die_size)
    ]
    if not affordable_sl:
        return
    best_sl = max(affordable_sl, key=lambda n: SESSION_CATALOG[n][1])
    _commit(best_sl, state)
    trace.append({
        "session": best_sl, "category": "SL", "rpe": SESSION_CATALOG[best_sl][1],
        "marginal_utility": None, "energy_used_running": state.energy_used,
        "alternatives_considered": len(affordable_sl), "note": "priorite_SL",
    })


def _utility(energy_used, n_quality, avg_rpe, energy_budget, rpe_max, tn, weights):
    _, fatigue = energy_and_fatigue(energy_used, tn)
    energy_rate = energy_used / energy_budget if energy_budget else 0.0
    rpe_rate = avg_rpe / rpe_max if rpe_max else 0.0
    return (
        weights["w_energy"] * energy_rate
        + weights["w_sessions"] * n_quality
        + weights["w_rpe"] * rpe_rate
        - weights["w_fatigue"] * fatigue
    )


def _marginal_utility(name, state, energy_budget, rpe_max, tn, weights):
    """
    Utilité marginale d'ajouter `name` à `state` : différence d'utilité
    avant/après, plutôt qu'un classement des séances sur un seul critère
    (RPE) comme le faisait l'ancien `_best_affordable`.
    """
    category, rpe = SESSION_CATALOG[name]

    n_before = len(state.chosen)
    quality_before = sum(1 for s in state.chosen if SESSION_CATALOG[s][0] in QUALITY_CATEGORIES)
    rpe_sum_before = sum(SESSION_CATALOG[s][1] for s in state.chosen)
    avg_rpe_before = (rpe_sum_before / n_before) if n_before else 0.0
    u_before = _utility(state.energy_used, quality_before, avg_rpe_before,
                         energy_budget, rpe_max, tn, weights)

    n_after = n_before + 1
    quality_after = quality_before + (1 if category in QUALITY_CATEGORIES else 0)
    avg_rpe_after = (rpe_sum_before + rpe) / n_after
    u_after = _utility(state.energy_used + rpe, quality_after, avg_rpe_after,
                        energy_budget, rpe_max, tn, weights)

    return u_after - u_before


def choose_sessions_weighted(available_session_names, energy_budget, rpe_max, tn,
                             quality_limit, weights=None, best_die_size=None):
    """
    Sélectionne les séances du tour par construction gloutonne sur l'utilité
    marginale pondérée, sous les contraintes dures du jeu.

    Paramètres
    ----------
    available_session_names : séances tentables (progress.tentable_sessions()).
    energy_budget            : énergie disponible ce tour (dés).
    rpe_max                  : RPE maximum atteignable ce tour (dés).
    tn                       : Target Number du tour, pour que la fatigue des
                                séances choisies suive la même courbe que
                                celle des dés (energy_and_fatigue).
    quality_limit            : plafond D99 de qualités planifiables. Une SL
                                consomme un slot comme toute autre qualité.
    weights                  : dict w_energy/w_sessions/w_fatigue/w_rpe
                                (DEFAULT_SESSION_WEIGHTS si omis).
    best_die_size            : meilleur dé du pool persistant. Sans valeur,
                                les qualités au-dessus de RPE Max sont filtrées.

    Note : la contrainte qualité<=EF est désormais STRICTEMENT PAR TOUR
    (pas de compteurs cumulés en entrée) — ce tour doit se suffire à
    lui-même, cf. docstring du module.

    Retourne
    --------
    (chosen, trace) :
        chosen : liste des noms de séances retenues.
        trace  : liste de dicts, une ligne par séance ajoutée (utilité
                 marginale ou note "priorite_SL" pour la SL/EF forcées).
    """
    weights = weights or DEFAULT_SESSION_WEIGHTS
    state = _SelectionState()
    trace = []

    if quality_limit < 0:
        raise ValueError("quality_limit must be non-negative")

    _prioritize_long_run(
        available_session_names, state, energy_budget, rpe_max, quality_limit, trace,
        best_die_size,
    )

    while True:
        candidates = [
            name for name in available_session_names
            if _is_affordable(
                name, state, energy_budget, rpe_max, quality_limit, best_die_size
            )
        ]
        if not candidates:
            break

        scored = [
            (name, _marginal_utility(name, state, energy_budget, rpe_max, tn, weights))
            for name in candidates
        ]
        scored.sort(key=lambda c: c[1], reverse=True)
        best_name, best_utility = scored[0]

        # Arrêt qualitatif : si même la meilleure option marginale dégrade
        # l'utilité, on s'arrête plutôt que d'ajouter des séances "pour
        # remplir le budget".
        if best_utility < 0:
            break

        _commit(best_name, state)
        category, rpe = SESSION_CATALOG[best_name]
        trace.append({
            "session": best_name, "category": category, "rpe": rpe,
            "marginal_utility": round(best_utility, 4),
            "energy_used_running": state.energy_used,
            "alternatives_considered": len(candidates), "note": "",
        })

    return state.chosen, trace
