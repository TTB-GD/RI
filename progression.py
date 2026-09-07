"""
Suivi de la progression d'un joueur au fil des tours : historique des
séances réalisées (pour le déblocage) et compteurs EF vs qualité (pour la
contrainte "au minimum autant de EF que de qualité").
"""
from collections import defaultdict
from sessions_catalog import SESSION_CATALOG, QUALITY_CATEGORIES, available_sessions


class PlayerProgress:
    def __init__(self):
        self.completions = defaultdict(int)  # nom séance -> nb de réalisations cumulées
        self.ef_total = 0
        self.quality_total = 0

    def available_sessions(self):
        return available_sessions(self.completions)

    def record_session(self, session_name):
        """Enregistre qu'une séance vient d'être réalisée (met à jour les compteurs)."""
        self.completions[session_name] += 1
        category, _ = SESSION_CATALOG[session_name]
        if category in QUALITY_CATEGORIES:
            self.quality_total += 1
        else:
            self.ef_total += 1
