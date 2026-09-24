"""
Catalogue des séances d'entraînement et arbre de déblocage progressif.

Règles de déblocage : chaque séance a un ou plusieurs prérequis de la forme
"avoir réalisé N fois la séance X" (cumulé, pas nécessairement consécutif).
Quand plusieurs prérequis sont listés pour une même séance, N'IMPORTE LEQUEL
suffit.

Progression actuelle :
- EF : EF1/EF2 sont initiales, puis EF3 -> EF4 -> EF5, chaque niveau
  demandant 2 réalisations du niveau précédent.
- Seuil, VMA et Force : le niveau 3 est accessible après 2 EF2, puis chaque
  branche progresse linéairement par 2 réalisations du niveau précédent.
- Spec : Spec4 est accessible après 2 Force3 OU 2 VMA3 OU 2 Seuil3. À partir
  de Spec4, la branche devient linéaire : Spec5 -> Spec6 -> Spec7 -> Spec8
  -> Spec9, avec 2 réalisations du niveau précédent à chaque étape.
- SL : SL5 est accessible après 2 EF4. À partir de SL5, la branche devient
  linéaire : SL6 -> SL7 -> SL8 -> SL9, avec 2 réalisations du niveau
  précédent à chaque étape.

Ainsi, Spec6 n'a pas de prérequis direct en Force5/VMA5/Seuil5 : il dépend de
Spec5. De même, SL6 dépend de SL5. Les branches Spec et SL deviennent donc
autonomes après leur point d'entrée respectif (Spec4 et SL5).

Une séance nouvellement débloquée à la fin du tour N n'est disponible qu'à
partir du tour N+1 : c'est automatique ici, car available_sessions() est
appelée en tout DÉBUT de tour, avant que les séances de ce tour ne soient
choisies/enregistrées.
"""


# ============================================================
# CATALOGUE DES SÉANCES
# ============================================================
# name -> (category, rpe)
# Le RPE sert aussi de coût en énergie.
SESSION_CATALOG = {
    "EF1": ("EF", 1),
    "EF2": ("EF", 2),
    "EF3": ("EF", 3),
    "EF4": ("EF", 4),
    "EF5": ("EF", 5),

    "Seuil3": ("Seuil", 3),
    "Seuil4": ("Seuil", 4),
    "Seuil5": ("Seuil", 5),
    "Seuil6": ("Seuil", 6),
    "Seuil7": ("Seuil", 7),

    "VMA3": ("VMA", 3),
    "VMA4": ("VMA", 4),
    "VMA5": ("VMA", 5),
    "VMA6": ("VMA", 6),
    "VMA7": ("VMA", 7),

    "Force3": ("Force", 3),
    "Force4": ("Force", 4),
    "Force5": ("Force", 5),

    "Spec4": ("Spec", 4),
    "Spec5": ("Spec", 5),
    "Spec6": ("Spec", 6),
    "Spec7": ("Spec", 7),
    "Spec8": ("Spec", 8),
    "Spec9": ("Spec", 9),

    "SL5": ("SL", 5),
    "SL6": ("SL", 6),
    "SL7": ("SL", 7),
    "SL8": ("SL", 8),
    "SL9": ("SL", 9),
}

# Catégories dites "de qualité" : SL, Spec, VMA, Seuil, Force (l'EF n'en
# fait pas partie). Utilisé pour la contrainte "au minimum autant de
# séances EF que de séances de qualité".
QUALITY_CATEGORIES = {"Seuil", "VMA", "Force", "Spec", "SL"}


# ============================================================
# ARBRE DE DÉBLOCAGE
# ============================================================
# name -> None (débloqué dès le début) ou liste de (nom_prérequis, seuil).
# Débloqué dès qu'AU MOINS UN des prérequis listés est satisfait.
SESSION_PREREQ = {
    "EF1": None,
    "EF2": None,

    "EF3": [("EF2", 2)],
    "Seuil3": [("EF2", 2)],
    "VMA3": [("EF2", 2)],
    "Force3": [("EF2", 2)],

    "EF4": [("EF3", 2)],
    "Seuil4": [("Seuil3", 2)],
    "VMA4": [("VMA3", 2)],
    "Force4": [("Force3", 2)],
    "Spec4": [("Force3", 2), ("VMA3", 2), ("Seuil3", 2)],

    "EF5": [("EF4", 2)],
    "Seuil5": [("Seuil4", 2)],
    "VMA5": [("VMA4", 2)],
    "Force5": [("Force4", 2)],
    "SL5": [("EF4", 2)],
    "Spec5": [("Spec4", 2)],

    "VMA6": [("VMA5", 2)],
    "Seuil6": [("Seuil5", 2)],
    "SL6": [("SL5", 2)],
    "Spec6": [("Spec5", 2)],

    "VMA7": [("VMA6", 2)],
    "Seuil7": [("Seuil6", 2)],
    "SL7": [("SL6", 2)],
    "Spec7": [("Spec6", 2)],

    "SL8": [("SL7", 2)],
    "SL9": [("SL8", 2)],
    "Spec8": [("Spec7", 2)],
    "Spec9": [("Spec8", 2)],
}


def is_unlocked(session_name, completions):
    prereq = SESSION_PREREQ[session_name]
    if prereq is None:
        return True
    return any(completions.get(name, 0) >= threshold for name, threshold in prereq)


def available_sessions(completions):
    """Liste des noms de séances actuellement accessibles au joueur."""
    return [name for name in SESSION_CATALOG if is_unlocked(name, completions)]


def tentable_sessions(completions):
    """Séances débloquées, plus l'étape qualité immédiatement suivante.

    ``SESSION_PREREQ`` est l'arbre explicite du catalogue : une séance
    verrouillée est donc l'étape suivante lorsque l'un de ses prédécesseurs
    explicites est déjà débloqué. Les EF conservent leur accès CURRENT et ne
    bénéficient pas de cette anticipation réservée aux qualités.
    """
    unlocked = available_sessions(completions)
    unlocked_set = set(unlocked)
    next_quality = [
        name for name, prerequisites in SESSION_PREREQ.items()
        if name not in unlocked_set
        and SESSION_CATALOG[name][0] in QUALITY_CATEGORIES
        and prerequisites
        and any(prerequisite in unlocked_set for prerequisite, _ in prerequisites)
    ]
    return unlocked + next_quality
