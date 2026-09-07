from collections import Counter


def pattern_signature(dice):
    """
    dice : liste de faces BRUTES (sans bonus). Le motif est identifié sur
    les faces brutes (D99 du GDD) — le bonus d'un dé amélioré ne doit pas
    fausser la détection de paires/brelans/etc.
    """
    counts = Counter(dice)
    return tuple(sorted(counts.values(), reverse=True))


def pattern_name(dice):
    sig = pattern_signature(dice)
    n = len(dice)

    if n == 6:
        if sig == (6,):
            return "six of a kind"
        if sig == (5, 1):
            return "five of a kind"
        if sig == (4, 2):
            return "four and a pair"
        if sig == (4, 1, 1):
            return "four of a kind"
        if sig == (3, 3):
            return "two triples"
        if sig == (3, 2, 1):
            return "triple and pair"
        if sig == (3, 1, 1, 1):
            return "three of a kind"
        if sig == (2, 2, 2):
            return "three pairs"
        if sig == (2, 2, 1, 1):
            return "two pairs"
        if sig == (2, 1, 1, 1, 1):
            return "one pair"
        if sig == (1, 1, 1, 1, 1, 1):
            return "all different"
    if n == 5:
        if sig == (5,):
            return "five of a kind"
        if sig == (4, 1):
            return "four of a kind"
        if sig == (3, 2):
            return "full house (3+2)"
        if sig == (3, 1, 1):
            return "three of a kind"
        if sig == (2, 2, 1):
            return "two pairs"
        if sig == (2, 1, 1, 1):
            return "one pair"
        if sig == (1, 1, 1, 1, 1):
            return "all different"
    if n == 4:
        if sig == (4,):
            return "four of a kind"
        if sig == (3, 1):
            return "three of a kind"
        if sig == (2, 2):
            return "two pairs"
        if sig == (2, 1, 1):
            return "one pair"
        if sig == (1, 1, 1, 1):
            return "all different"
    if n == 3:
        if sig == (3,):
            return "three of a kind"
        if sig == (2, 1):
            return "one pair"
        if sig == (1, 1, 1):
            return "all different"

    return "unknown pattern"
