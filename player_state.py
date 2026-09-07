"""
Regroupe tout l'état d'UN joueur qui persiste d'un tour à l'autre :
- progress   : PlayerProgress (déblocage, compteurs EF/qualité cumulés).
- dice_pool  : PlayerDicePool (pool de dés, paliers CTL, améliorations).
- cumulative_ctl : somme du CTL de chaque tour joué (forme cumulée).
Regroupé en une seule classe pour éviter de faire circuler 3 paramètres
séparés dans toute la simulation (cf. `simulate_player.play_player_turn`).
"""
from dataclasses import dataclass, field

from progression import PlayerProgress
from dice_progression import PlayerDicePool


@dataclass
class Player:
    progress: PlayerProgress = field(default_factory=PlayerProgress)
    dice_pool: PlayerDicePool = field(default_factory=PlayerDicePool)
    cumulative_ctl: int = 0