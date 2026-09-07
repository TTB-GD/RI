"""
Sélection des séances jouées par le joueur à un tour donné, sous contrainte :

- énergie   : somme des coûts des séances choisies <= énergie du tirage.
- RPE       : RPE d'une séance <= RPE max du tirage (le risque de blessure
              pour une séance dépassant ce RPE n'est PAS encore modélisé —
              on l'exclut donc pour l'instant plutôt que de l'autoriser).
- catégorie : au plus 1 séance par catégorie (EF, Seuil, VMA, Force, Spec,
              SL) et par tour.
- qualité   : le nombre cumulé de séances de qualité ne peut jamais dépasser
              le nombre cumulé de séances EF.

Politique de choix (heuristique simple, pas une recherche exhaustive) :
1. Toujours essayer de caser une séance EF au palier le plus élevé possible
   (fait progresser l'arbre de déblocage ET ouvre le quota de qualité).
2. Puis, dans un ordre de priorité fixe (Seuil, VMA, Force, Spec, SL),
   essayer une séance de qualité au palier le plus élevé possible tant que
   la contrainte qualité <= EF et le budget énergie/RPE le permettent.

C'est un point de départ délibérément simple : la priorité entre catégories
de qualité (arbitraire ici) est un levier de game design à tester/ajuster.
"""
from sessions_catalog import SESSION_CATALOG, QUALITY_CATEGORIES

QUALITY_PRIORITY = ["Seuil", "VMA", "Force", "Spec", "SL"]


def _best_affordable(candidates, energy_budget, rpe_max):
    """Parmi une liste de noms de séances, retourne celle au RPE le plus
    élevé qui respecte le budget énergie et le RPE max (ou None)."""
    affordable = [
        name for name in candidates
        if SESSION_CATALOG[name][1] <= rpe_max and SESSION_CATALOG[name][1] <= energy_budget
    ]
    if not affordable:
        return None
    return max(affordable, key=lambda name: SESSION_CATALOG[name][1])


def choose_sessions_for_turn(available_session_names, energy_budget, rpe_max, progress):
    """
    Retourne la liste des séances choisies pour ce tour.

    Contraintes :
      - énergie : somme des coûts des séances choisies <= énergie disponible ;
      - RPE : RPE individuel <= RPE max du tirage ;
      - maximum 7 séances par tour ;
      - SL : une seule sortie longue par tour ;
      - qualité : le nombre cumulé de séances qualité ne dépasse jamais
        le nombre cumulé de séances EF.

    Les séances EF, Seuil, VMA, Force et Spec peuvent être répétées.
    """

    MAX_SESSIONS_PER_TURN = 7

    remaining_energy = energy_budget
    chosen = []

    # Catégories avec limitation structurelle
    used_categories = set()

    # Compteurs temporaires du tour
    ef_this_turn = 0
    quality_this_turn = 0

    while len(chosen) < MAX_SESSIONS_PER_TURN:

        best_choice = None
        best_rpe = -1

        for name in available_session_names:

            category, rpe = SESSION_CATALOG[name]

            # Une seule sortie longue par tour
            if category == "SL" and category in used_categories:
                continue

            # Contraintes énergie / RPE
            if rpe > remaining_energy:
                continue

            if rpe > rpe_max:
                continue

            # Contrainte quantité de travail qualitatif
            if category in QUALITY_CATEGORIES:
                if (
                    progress.quality_total
                    + quality_this_turn
                    + 1
                    > progress.ef_total
                    + ef_this_turn
                ):
                    continue

            # Choix glouton : séance avec le RPE le plus élevé
            if rpe > best_rpe:
                best_choice = name
                best_rpe = rpe

        if best_choice is None:
            break

        chosen.append(best_choice)

        category, rpe = SESSION_CATALOG[best_choice]

        remaining_energy -= rpe

        # Seule catégorie limitée actuellement : SL
        if category == "SL":
            used_categories.add(category)

        if category == "EF":
            ef_this_turn += 1

        elif category in QUALITY_CATEGORIES:
            quality_this_turn += 1

    return chosen
