import random
from dataclasses import dataclass, field

# Bonus permanent attaché à un dé amélioré (D4 du GDD).
# Mis à 0 volontairement pour l'instant : on veut d'abord observer les
# probabilités "naturelles" (liées uniquement à la taille du dé, donc à son
# nombre de faces) avant d'ajouter un calcul de bonus par-dessus.
DIE_BONUS = {6: 0, 8: 0, 10: 0, 12: 0}


@dataclass
class Die:
    size: int  # 6, 8, 10 ou 12
    bonus: int = field(init=False)

    def __post_init__(self):
        if self.size not in DIE_BONUS:
            raise ValueError(f"Taille de dé non supportée : {self.size}")
        self.bonus = DIE_BONUS[self.size]

    def roll(self):
        """Retourne (face_brute, valeur_finale = face + bonus)."""
        face = random.randint(1, self.size)
        return face, face + self.bonus


def make_pool(sizes):
    """Construit un pool de dés à partir d'une liste de tailles, ex: [6, 6, 6, 8, 10]."""
    return [Die(s) for s in sizes]


def expected_value(die):
    """Valeur moyenne d'un dé (face uniforme 1..size) : (size + 1) / 2."""
    return (die.size + 1) / 2


def pool_tn(pool):
    """
    Target Number d'un pool : somme des valeurs moyennes de TOUS les dés du
    pool (dés actifs + dé de réserve), qu'ils soient d6, d8, d10 ou d12.

    Remplace l'ancienne formule 'max_dice * 3.5', qui supposait un pool
    entièrement composé de d6 et sous-évaluait le TN dès qu'un dé amélioré
    était présent (un d12 vaut en moyenne 6.5, pas 3.5).
    """
    return sum(expected_value(d) for d in pool)
