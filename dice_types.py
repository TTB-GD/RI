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


def example_pool(max_dice):
    """
    Génère un pool d'exemple pour les tests/démo : (max_dice - 1) dés actifs
    (le lancer initial), plus un dé de réserve (utilisé par l'action 'add').

    Hypothèse de jeu actée : la plupart des joueurs intègrent systématiquement
    leur(s) dé(s) amélioré(s) au lancer initial plutôt que de le(s) garder en
    réserve. On ne modélise donc PAS (pour l'instant) le cas où le dé de
    réserve serait le dé amélioré : le dé de réserve est toujours un d6, et
    un éventuel dé amélioré est toujours placé parmi les dés actifs.
    """
    active_size = max_dice - 1
    sizes = [6] * active_size

    if random.random() < 0.5:  # 50% de chance d'avoir un dé amélioré ce tour
        idx = random.randrange(active_size)
        sizes[idx] = random.choice([8, 10, 12])

    sizes.append(6)  # dé de réserve : toujours un d6 pour l'instant
    return make_pool(sizes)
