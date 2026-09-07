"""
Progression du pool de dés d'un joueur, INDÉPENDANTE des tirages tour par
tour. `dice_types`/`decision_engine` restent des fonctions pures sur un pool
donné pour UN tour ; ce module gère l'ÉVOLUTION de ce pool d'un tour à
l'autre pour un joueur qui persiste sur toute la simulation.

Règles (fournies par l'utilisateur) :
    - Pool initial : 4 d6.
    - Jusqu'à 2 dés supplémentaires débloqués aux paliers de CTL CUMULÉ 50
      et 100 (1 dé par palier franchi, jamais plus). Toujours des d6 à
      l'ajout. Pool maximum : 4 + 2 = 6 dés (borne haute déjà couverte par
      les tables SESSION_EFFECTS existantes, pas besoin d'extrapoler
      au-delà).
    - Jusqu'à 4 améliorations de dé au total sur TOUT le pool (dés
      initiaux et dés ajoutés confondus, budget global unique) : une
      amélioration devient disponible toutes les 8 séances de qualité
      cumulées. Un dé progresse d6 -> d8 -> d10 -> d12 (plafond à d12).
    - Quel dé améliorer en premier (répartir l'effort sur plusieurs dés vs
      le concentrer sur un ou deux) est un choix de profil de joueur : géré
      par un moteur pondéré (`w_concentration` / `w_spread`) pour pouvoir
      tester plusieurs profils en simulation sans changer le code.

Comme pour le déblocage de séances (`sessions_catalog.available_sessions`,
appelé en tout début de tour), les paliers/améliorations dus sont appliqués
en DÉBUT de tour, à partir de l'état accumulé (CTL, séances de qualité) à
la fin du tour précédent : un joueur qui franchit CTL=50 ou complète sa
8e séance de qualité pendant le tour N n'en profite qu'à partir du tour N+1.
"""
from dataclasses import dataclass, field

from dice_types import make_pool

SIZE_SEQUENCE = [6, 8, 10, 12]
INITIAL_POOL_SIZE = 4
MAX_ADDED_DICE = 2
MAX_UPGRADES = 4
QUALITY_SESSIONS_PER_UPGRADE = 4
CTL_MILESTONES = (50, 100)  # un dé ajouté par palier franchi, jamais plus d'un

DEFAULT_UPGRADE_WEIGHTS = {"w_concentration": 1.0, "w_spread": 1.0}


def choose_die_to_upgrade(sizes, weights):
    """
    Choisit l'index du dé à améliorer parmi ceux non plafonnés (< d12).

    Profil piloté par les poids :
        score(i) = (w_concentration - w_spread) * rang_taille(dé_i)
    où rang_taille va de 0 (d6) à 2 (d10, le dernier rang éligible avant d12).

    - w_concentration >> w_spread : le score croît avec la taille déjà
      atteinte -> on pousse encore plus haut un dé déjà amélioré (profil
      CONCENTRÉ : un ou deux dés montent vite vers d12).
    - w_spread >> w_concentration : le score décroît avec la taille -> on
      privilégie les dés encore en d6/d8 (profil RÉPARTI : tous les dés
      progressent ensemble, aucun n'avance avant les autres).
    - Poids égaux (défaut) : score nul partout, égalité résolue par taille
      croissante puis index croissant -> réparti par défaut, déterministe
      et reproductible en simulation.

    Retourne None si tous les dés du pool sont déjà au maximum (d12).
    """
    eligible = [i for i, s in enumerate(sizes) if s < SIZE_SEQUENCE[-1]]
    if not eligible:
        return None

    def score(i):
        rank = SIZE_SEQUENCE.index(sizes[i])
        return (weights["w_concentration"] - weights["w_spread"]) * rank

    eligible.sort(key=lambda i: (-score(i), sizes[i], i))
    return eligible[0]


@dataclass
class PlayerDicePool:
    """État persistant du pool de dés d'UN joueur, à faire évoluer tour après tour."""
    sizes: list = field(default_factory=lambda: [6] * INITIAL_POOL_SIZE)
    upgrades_used: int = 0
    dice_added: int = 0
    _milestones_claimed: set = field(default_factory=set)

    def maybe_add_dice(self, cumulative_ctl):
        """Ajoute un d6 par palier de CTL cumulé franchi (une seule fois par palier)."""
        for milestone in CTL_MILESTONES:
            if (
                cumulative_ctl >= milestone
                and milestone not in self._milestones_claimed
                and self.dice_added < MAX_ADDED_DICE
            ):
                self.sizes.append(6)
                self.dice_added += 1
                self._milestones_claimed.add(milestone)

    def maybe_upgrade(self, quality_total, weights=None):
        """
        Applique toutes les améliorations dues (une par tranche de 8 séances
        de qualité cumulées, plafonné à MAX_UPGRADES), en choisissant à
        chaque fois le dé cible via `choose_die_to_upgrade`. Ne fait rien
        si aucune amélioration n'est due, si le budget global est épuisé,
        ou si tous les dés sont déjà au maximum.
        """
        weights = weights or DEFAULT_UPGRADE_WEIGHTS
        points_due = min(quality_total // QUALITY_SESSIONS_PER_UPGRADE, MAX_UPGRADES)
        while self.upgrades_used < points_due:
            idx = choose_die_to_upgrade(self.sizes, weights)
            if idx is None:
                break  # tous les dés au max : budget restant inutilisable
            current_rank = SIZE_SEQUENCE.index(self.sizes[idx])
            self.sizes[idx] = SIZE_SEQUENCE[current_rank + 1]
            self.upgrades_used += 1

    def as_dice_objects(self):
        """Instancie les objets Die (dice_types) correspondant à l'état actuel du pool."""
        return make_pool(self.sizes)