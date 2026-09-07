from dataclasses import dataclass
from patterns import pattern_name, pattern_signature


@dataclass
class DiceResult:
    faces: list      # faces brutes (sans bonus) -> utilisées pour le motif
    values: list     # valeurs finales (face + bonus) -> utilisées pour le score
    sizes: list      # taille de chaque dé utilisé (traçabilité / debug)
    total: int       # somme des valeurs (énergie / score du tour)
    max_value: int   # valeur max -> détermine le palier de difficulté accessible
    pattern: str
    signature: tuple


def create_dice_result(dice_objects, faces, values):
    """
    dice_objects : liste de Die (voir dice_types.py), dans le même ordre que
    faces/values, pour retrouver la taille de chaque dé utilisé.
    """
    return DiceResult(
        faces=faces,
        values=values,
        sizes=[d.size for d in dice_objects],
        total=sum(values),
        max_value=max(values),
        pattern=pattern_name(faces),
        signature=pattern_signature(faces),
    )
