"""
Conséquences d'un motif combinatoire : nombre de séances de qualité
débloquées, et accès (ou non) au "dé de pool" (P1/P2 du GDD).

Rappel des règles :
- P1 : par défaut, le joueur ne retient que (max_dice - 1) dés pour le
  calcul final, quel que soit le nombre de dés effectivement lancés.
- P2 : si le motif obtenu donne le bonus "dé de pool", le joueur retient
  la totalité des dés lancés au lieu de (max_dice - 1).

Les tables pour n=4, 5, 6 sont transcrites telles quelles depuis le GDD.
n=3 est une extrapolation (voir note dans SESSION_EFFECTS) : le GDD ne
couvre explicitement que 4d6/5d6/6d6.
"""
from patterns import pattern_signature

SESSION_EFFECTS = {
    3: {
        # Extrapolation : non fournie explicitement par le GDD. Le bonus
        # "dé de pool" est volontairement désactivé à ce niveau : il
        # correspondrait à la règle D99 (obtenir le dé de réserve gratuitement
        # sur un bon motif au lancer initial), non implémentée pour l'instant.
        (1, 1, 1): (1, False),
        (2, 1): (2, False),
        (3,): (2, False),
    },
    4: {
        (1, 1, 1, 1): (1, False),
        (2, 1, 1): (2, False),
        (3, 1): (2, True),
        (2, 2): (2, True),
        (4,): (3, True),
    },
    5: {
        (1, 1, 1, 1, 1): (1, False),
        (2, 1, 1, 1): (2, False),
        (2, 2, 1): (2, True),
        (3, 1, 1): (2, True),
        (3, 2): (3, True),
        (4, 1): (3, True),
        (5,): (3, True),
    },
    6: {
        (1, 1, 1, 1, 1, 1): (1, False),
        (2, 1, 1, 1, 1): (2, False),
        (2, 2, 1, 1): (2, True),
        (3, 1, 1, 1): (2, True),
        (3, 2, 1): (3, True),
        (2, 2, 2): (3, True),
        (4, 1, 1): (3, True),
        (4, 2): (3, True),
        (3, 3): (3, True),
        (5, 1): (3, True),
        (6,): (3, True),
    },
}


def session_outcome(faces, values, max_dice):
    """
    faces    : faces brutes du lancer FINAL du tour (après toutes les actions).
    values   : valeurs correspondantes (face + bonus, alignées avec faces).
    max_dice : taille du pool débloqué ce palier (4, 5 ou 6).

    Retourne un dict :
        sessions      : nombre de séances de qualité débloquées.
        bonus_pool    : True si le motif donne accès au dé de pool (P2).
        signature     : motif combinatoire détecté.
        dice_used     : valeurs retenues pour le calcul final (énergie/score).
        dice_dropped  : valeur écartée, ou None si aucun dé n'a été écarté.
        total         : somme de dice_used.
    """
    n = len(faces)
    if n not in SESSION_EFFECTS:
        raise ValueError(f"Unsupported number of dice: {n}")

    table = SESSION_EFFECTS[n]
    sig = pattern_signature(faces)
    sessions, bonus_pool = table.get(sig, (1, False))

    default_action_dice = max_dice - 1
    paired = list(zip(faces, values))  # garde la correspondance face/valeur

    if n <= default_action_dice or bonus_pool:
        # Pas de dé "en trop" (pas de add), ou motif bonus : on garde tout.
        dice_used = [v for _, v in paired]
        dropped = None
    else:
        # Pas de bonus : on ne retient que (max_dice - 1) dés, les plus
        # hauts en valeur (cf. exemple du GDD : on écarte le plus faible).
        ordered = sorted(paired, key=lambda fv: fv[1], reverse=True)
        kept = ordered[:default_action_dice]
        rest = ordered[default_action_dice:]
        dice_used = [v for _, v in kept]
        dropped = rest[0][1] if rest else None

    return {
        "sessions": sessions,
        "bonus_pool": bonus_pool,
        "signature": sig,
        "dice_used": dice_used,
        "dice_dropped": dropped,
        "total": sum(dice_used),
        "rpe_max": max(dice_used) if dice_used else 0,
    }
