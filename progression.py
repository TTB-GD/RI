"""
Suivi de la progression d'un joueur au fil des tours : historique des
séances réalisées (pour le déblocage) et compteurs cumulés EF vs qualité
(pour l'historique de progression et l'amélioration des dés).

La contrainte "au minimum autant de EF que de qualité" n'est PAS calculée
avec ces compteurs cumulés : elle est appliquée strictement à l'intérieur
de chaque tour par `session_selector.choose_sessions_weighted`. Les EF
réalisées lors des tours précédents ne créent donc aucun quota de qualité
supplémentaire pour le tour courant.
"""
from collections import defaultdict
from sessions_catalog import (
    SESSION_CATALOG,
    QUALITY_CATEGORIES,
    available_sessions,
    tentable_sessions,
)


class PlayerProgress:
    def __init__(self):
        self.completions = defaultdict(int)  # nom séance -> nb de réalisations cumulées
        self.ef_total = 0
        self.quality_total = 0

    def available_sessions(self):
        return available_sessions(self.completions)

    def tentable_sessions(self):
        """Expose l'accès CURRENT : débloquées + prochaine étape qualité."""
        return tentable_sessions(self.completions)

    def record_session(self, session_name):
        """Enregistre qu'une séance vient d'être réalisée (met à jour les compteurs)."""
        self.completions[session_name] += 1
        category, _ = SESSION_CATALOG[session_name]
        if category in QUALITY_CATEGORIES:
            self.quality_total += 1
        else:
            self.ef_total += 1
