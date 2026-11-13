import itertools
import math
import os
from collections import Counter, defaultdict

# Niveau 0 = d6, 1 = d8, 2 = d10, 3 = d12
TAILLES = [6, 8, 10, 12]
MAX_AMELIORATIONS = 4
FICHIER_CSV = "tables_completes.csv"
FICHIER_RECAP = "recapitulatif.csv"
FICHIER_SERIES = "series.csv"
FICHIER_COMPARAISON = "comparaison_relance.csv"
FICHIER_SERIES_COMPAREES = "series_comparees.csv"
FICHIER_SERIES_BUDGET = "series_relances_limitees.csv"
N_MIN, N_MAX = 6, 16   # nombre de tours étudiés
K_DEFAUT = 3           # série de k réussites consécutives par défaut

MODES = {
    0: "sans relance",
    1: "relance de tous les dés",
    2: "relance d'un sous-ensemble choisi",
}

SERIES_CALCULEES = []   # séries calculées pendant la session
COMPARAISONS = {}       # comparaisons des modes, clé (num de pool, TN)
SERIES_COMPAREES = []   # séries comparant les 3 modes, calculées pendant la session
SERIES_BUDGET = []      # séries avec relances limitées, calculées pendant la session
CACHE_PROBAS = {}       # probabilités avec relance, par (pool, mode)


# ---------------------------------------------------------------------------
# 1. Pools et statistiques
# ---------------------------------------------------------------------------

def generer_pools():
    """Génère les 33 pools : 4 à 6 dés, au plus 4 améliorations."""
    pools = []
    for n in (4, 5, 6):
        for combo in itertools.combinations_with_replacement(range(4), n):
            if sum(combo) <= MAX_AMELIORATIONS:
                pools.append(sorted(TAILLES[niv] for niv in combo))
    return pools


def nom(faces):
    c = Counter(faces)
    return " + ".join(f"{c[f]}d{f}" for f in sorted(c))


def statistiques(faces):
    esperance = sum((f + 1) / 2 for f in faces)
    ecart_type = math.sqrt(sum((f * f - 1) / 12 for f in faces))
    return esperance, ecart_type


def nombre_ameliorations(faces):
    return sum((f - 6) // 2 for f in faces)  # d6→0, d8→1, d10→2, d12→3


# ---------------------------------------------------------------------------
# 2. Outils de sommes de sous-ensembles (entiers Python, sans numpy)
# ---------------------------------------------------------------------------
# Un « masque » est un entier dont le bit s vaut 1 si la somme s est atteignable
# par un sous-ensemble de dés (le bit 0 représente le sous-ensemble vide).
#
# Un « vecteur empaqueté » range, dans un seul grand entier, un compteur de W bits
# par TN : le champ tn contient le nombre d'issues qui réussissent au TN tn.
# Additionner deux vecteurs = additionner les compteurs de tous les TN d'un coup.

W = 20                    # bits par compteur
CHAMP = (1 << W) - 1
NB_CHAMPS = 64            # nombre maximal de TN gérés (somme max des dés + 2)
GARDE = sum(1 << (W * i + W - 1) for i in range(NB_CHAMPS))  # bits de garde

_FEUILLES = {}            # masque -> vecteur de réussite (0 ou 1 par TN)
_VEC = {}                 # (masque, dés restants) -> vecteur empaqueté


def _verifier(faces):
    assert sum(faces) + 2 <= NB_CHAMPS, "Somme des dés trop grande pour NB_CHAMPS"
    assert math.prod(faces) < (1 << (W - 1)), "Trop de lancers : augmenter W"


def _feuille(m):
    """Vecteur empaqueté d'un masque final : 1 pour chaque TN valide (somme à ±1)."""
    v = _FEUILLES.get(m)
    if v is None:
        m &= ~1                       # on retire la somme vide
        val = m | (m << 1) | (m >> 1)  # TN valide si une somme est à ±1
        v = 0
        x, tn = val >> 1, 1
        while x:
            if x & 1:
                v |= 1 << (W * tn)
            x >>= 1
            tn += 1
        _FEUILLES[m] = v
    return v


def _vec(m, F):
    """
    Vecteur empaqueté (nb d'issues réussissantes par TN) quand on lance les dés
    de faces F (tuple trié) en partant des sommes déjà atteintes m.
    Mémoïsé : les mêmes états sont partagés entre lancers, sous-ensembles et pools.
    """
    cle = (m, F)
    v = _VEC.get(cle)
    if v is None:
        if not F:
            v = _feuille(m)
        else:
            reste = F[1:]
            v = 0
            for val in range(1, F[0] + 1):
                v += _vec(m | (m << val), reste)
        _VEC[cle] = v
    return v


def _max_champs(a, b):
    """Maximum champ par champ de deux vecteurs empaquetés (astuce SWAR)."""
    g = (((a | GARDE) - b) & GARDE) >> (W - 1)   # 1 dans chaque champ où a >= b
    m = g * CHAMP                                # champ rempli de 1 là où a >= b
    return b ^ ((a ^ b) & m)


# ---------------------------------------------------------------------------
# 3. Probabilités d'un tour sans relance
# ---------------------------------------------------------------------------

def analyser(faces):
    """Renvoie (nombre de lancers, compte des lancers valides par TN, TN max utile)."""
    faces = tuple(sorted(faces))
    _verifier(faces)
    maxi = sum(faces)
    v = _vec(1, faces)
    compte = {tn: (v >> (W * tn)) & CHAMP for tn in range(1, maxi + 2)}
    return math.prod(faces), compte, maxi


def tn_equivalent(probas_tn, cible, maxi):
    """
    TN (interpolé) auquel la probabilité sans relance atteint la valeur cible.
    Sert à convertir un gain de probabilité en points de TN.
    """
    if cible <= 0:
        return None
    a = max((tn for tn in range(1, maxi + 2) if probas_tn[tn] >= cible), default=None)
    if a is None:
        return None
    pa = probas_tn[a]
    pb = probas_tn.get(a + 1, 0.0)
    if pa == pb:
        return float(a)
    return a + (pa - cible) / (pa - pb)


def tn_50(probas_tn, maxi):
    """Plus grand TN avec une réussite ≥ 50 %, interpolé linéairement."""
    return tn_equivalent(probas_tn, 0.5, maxi)


# ---------------------------------------------------------------------------
# 4. Relance d'un sous-ensemble
# ---------------------------------------------------------------------------

def _lancers_groupes(faces):
    """
    Génère (dés, poids) : dés = liste triée de (face, valeur), poids = nombre de
    lancers équivalents par permutation de dés identiques.
    """
    options = []
    for f, c in sorted(Counter(faces).items()):
        opts = []
        for vals in itertools.combinations_with_replacement(range(1, f + 1), c):
            poids = math.factorial(c)
            for mult in Counter(vals).values():
                poids //= math.factorial(mult)
            opts.append((tuple((f, v) for v in vals), poids))
        options.append(opts)
    for choix in itertools.product(*options):
        yield ([d for ds, _ in choix for d in ds],
               math.prod(p for _, p in choix))


def probas_relance_sous_ensemble(faces):
    """
    Probabilité de réussite par TN avec relance optimale d'un sous-ensemble.
    Pour chaque lancer initial, on retient le meilleur sous-ensemble à relancer,
    ce choix étant fait séparément pour chaque TN (maximum champ par champ).
    """
    faces = tuple(sorted(faces))
    _verifier(faces)
    n = len(faces)
    nt = sum(faces) + 2
    total = math.prod(faces)

    # Pour chaque sous-ensemble relancé : dés gardés, faces relancées, échelle
    # (ramène toutes les probabilités au même dénominateur « total »).
    plan = []
    for k in range(n + 1):
        for S in itertools.combinations(range(n), k):
            gardes = [i for i in range(n) if i not in S]
            F = tuple(faces[i] for i in S)
            plan.append((S, gardes, F, total // math.prod(F)))

    acc = Counter()   # meilleur vecteur empaqueté -> poids cumulé
    for des, poids in _lancers_groupes(faces):
        vus = set()
        meilleur = None
        for S, gardes, F, echelle in plan:
            signature = tuple(des[i] for i in S)   # relances équivalentes : un seul essai
            if signature in vus:
                continue
            vus.add(signature)
            m = 1
            for i in gardes:
                m |= m << des[i][1]
            v = _vec(m, F) * echelle
            meilleur = v if meilleur is None else _max_champs(meilleur, v)
        acc[meilleur] += poids

    gain = [0] * nt
    for vecteur, poids in acc.items():
        for tn in range(1, nt):
            gain[tn] += poids * ((vecteur >> (W * tn)) & CHAMP)
    return {tn: gain[tn] / (total * total) for tn in range(1, nt)}


def precalculer_relances(resultats):
    """Calcule la relance de sous-ensemble des pools manquants (avec progression)."""
    a_faire = [r for r in resultats if (r["num"], 2) not in CACHE_PROBAS]
    for i, r in enumerate(a_faire, 1):
        print(f"  {i}/{len(a_faire)} : {r['nom']}", flush=True)
        CACHE_PROBAS[(r["num"], 2)] = probas_relance_sous_ensemble(r["faces"])


def probas(r, mode):
    """
    Probabilité p de réussir un tour, par TN, selon le mode :
    0 = sans relance, 1 = relance de tous les dés, 2 = relance d'un sous-ensemble.
    Les résultats avec relance sont mis en cache.
    """
    if mode == 0:
        return {tn: r["compte"][tn] / r["total"] for tn in range(1, r["maxi"] + 2)}

    cle = (r["num"], mode)
    if cle not in CACHE_PROBAS:
        if mode == 1:
            # Formule exacte : p1 = 1 − (1 − p0)²
            base = probas(r, 0)
            CACHE_PROBAS[cle] = {tn: 1 - (1 - base[tn]) ** 2 for tn in base}
        else:
            CACHE_PROBAS[cle] = probas_relance_sous_ensemble(r["faces"])
    return CACHE_PROBAS[cle]


# ---------------------------------------------------------------------------
# 5. Probabilités sur plusieurs tours consécutifs
# ---------------------------------------------------------------------------

def proba_toujours(p, n):
    """Probabilité de réussir les n tours consécutifs : p^n."""
    return p ** n


def proba_au_moins_une(p, n):
    """Probabilité de réussir au moins une fois sur n tours : 1 − (1 − p)^n."""
    return 1 - (1 - p) ** n


def proba_serie_k(p, n, k):
    """
    Probabilité d'obtenir au moins k réussites consécutives sur n tours.
    Récurrence sur la longueur de la série en cours, avec état absorbant à k.
    """
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    etats = [0.0] * k      # etats[j] : P(série en cours de longueur j, k non atteint)
    etats[0] = 1.0
    absorbe = 0.0          # P(série de k réussites déjà atteinte)
    for _ in range(n):
        nouveau = [0.0] * k
        nouveau[0] = sum(etats) * (1 - p)     # échec : la série repart de zéro
        for j in range(k - 1):
            nouveau[j + 1] = etats[j] * p      # réussite : la série s'allonge
        absorbe += etats[k - 1] * p            # réussite qui complète la série
        etats = nouveau
    return absorbe


def calculer_series(r, tn_min, tn_max, k, mode):
    """Renvoie la liste des lignes de séries pour le mode de relance choisi."""
    p_par_tn = probas(r, mode)
    lignes = []
    for tn in range(tn_min, tn_max + 1):
        p = p_par_tn[tn]
        for n in range(N_MIN, N_MAX + 1):
            lignes.append({
                "pool_num": r["num"], "pool": r["nom"],
                "mode": MODES[mode], "k": k,
                "tn": tn, "p": p, "n": n,
                "toujours": proba_toujours(p, n),
                "une_fois": proba_au_moins_une(p, n),
                "serie_k": proba_serie_k(p, n, k),
            })
    return lignes


def calculer_series_comparees(r, tn_min, tn_max, k):
    """
    Pour un pool, calcule sur n tours consécutifs (N_MIN..N_MAX) les probabilités
    des trois modes (0 = sans relance, 1 = relance de tous, 2 = relance d'un
    sous-ensemble) : tous les tours réussis, au moins une réussite, au moins k
    réussites consécutives. Chaque liste est ordonnée selon les modes 0, 1, 2.
    """
    p_modes = [probas(r, m) for m in (0, 1, 2)]
    lignes = []
    for tn in range(tn_min, tn_max + 1):
        ps = [pm[tn] for pm in p_modes]
        for n in range(N_MIN, N_MAX + 1):
            lignes.append({
                "pool_num": r["num"], "pool": r["nom"], "k": k, "tn": tn, "n": n,
                "p": ps,
                "toujours": [proba_toujours(p, n) for p in ps],
                "une_fois": [proba_au_moins_une(p, n) for p in ps],
                "serie_k": [proba_serie_k(p, n, k) for p in ps],
            })
    return lignes


def dialoguer_series_comparees(resultats):
    """Compare sans relance / relance totale / relance d'un sous-ensemble sur n tours."""
    num = saisir_entier(f"Numéro du pool (1 à {len(resultats)})", 1, 1, len(resultats))
    r = resultats[num - 1]

    print(f"Calcul des relances pour {r['nom']}...")
    t50 = tn_50(probas(r, 0), r["maxi"])
    centre = int(round(t50)) if t50 is not None else r["maxi"] // 2
    tn_min = max(1, centre - 2)
    tn_max = min(r["maxi"] + 1, centre + 2)
    tn_min = saisir_entier("TN minimum", tn_min, 1, r["maxi"] + 1)
    tn_max = saisir_entier("TN maximum", tn_max, tn_min, r["maxi"] + 1)
    k = saisir_entier(f"Nombre k de réussites consécutives (1 à {N_MAX})",
                      K_DEFAUT, 1, N_MAX)

    lignes = calculer_series_comparees(r, tn_min, tn_max, k)
    SERIES_COMPAREES.extend(lignes)

    print(f"\nSÉRIES COMPARÉES : {r['nom']} (k = {k})\n")
    print("TN\tn tours\t"
          "p sans (%)\tp relance tous (%)\tp relance sous-ens. (%)\t"
          "Tous les tours : sans (%)\ttous (%)\tsous-ens. (%)\t"
          "Au moins 1 : sans (%)\ttous (%)\tsous-ens. (%)\t"
          f"Au moins {k} consécutives : sans (%)\ttous (%)\tsous-ens. (%)")
    for l in lignes:
        cols = [str(l["tn"]), str(l["n"])]
        for cle in ("p", "toujours", "une_fois", "serie_k"):
            if cle == "p" and l["n"] != N_MIN:
                cols += [""] * 3          # p ne dépend pas de n : affiché une fois par TN
            else:
                cols += [fmt(x * 100) for x in l[cle]]
        print("\t".join(cols))


# ---------------------------------------------------------------------------
# 5 bis. Relances limitées : budget total et plafond par tour
# ---------------------------------------------------------------------------
# Modèle : à chaque tour, le joueur lance ; s'il échoue (aucune somme à TN, TN-1
# ou TN+1), il relance (tous les dés, ou le meilleur sous-ensemble) tant qu'il lui
# reste du budget et qu'il n'a pas atteint le plafond de relances par tour.
# R = nombre de relances nécessaires pour réussir un tour (0 = réussi du 1er coup).
# Pour la relance d'un sous-ensemble, à chaque relance on choisit le sous-ensemble
# qui maximise la probabilité de réussir à cette relance (politique gloutonne).

JMAX = 10                 # plafond maximal de relances par tour
CACHE_CUMULS = {}         # (num de pool, TN) -> [P(réussir avec <= j relances)]
_ISSUES = {}              # faces relancées -> [(dés, poids)] regroupés par symétrie


def _issues(F):
    v = _ISSUES.get(F)
    if v is None:
        v = _ISSUES[F] = list(_lancers_groupes(F))
    return v


def _reussit(des, tn):
    """Vrai si une somme de sous-ensemble de dés vaut tn-1, tn ou tn+1."""
    m = 1
    for _, v in des:
        m |= m << v
    m &= ~1
    return bool(((m | (m << 1) | (m >> 1)) >> tn) & 1)


def cumuls_sous_ensemble(faces, tn, jmax):
    """
    Renvoie [c_0, ..., c_jmax] où c_j = probabilité de réussir un tour avec au plus
    j relances de sous-ensemble (c_0 = sans relance).
    """
    faces = tuple(sorted(faces))
    _verifier(faces)
    n = len(faces)
    total = math.prod(faces)

    plan = []
    for k in range(n + 1):
        for S in itertools.combinations(range(n), k):
            gardes = [i for i in range(n) if i not in S]
            F = tuple(faces[i] for i in S)
            plan.append((S, gardes, F, total // math.prod(F)))

    c0 = 0.0
    echecs = {}
    for des, poids in _lancers_groupes(faces):
        if _reussit(des, tn):
            c0 += poids / total
        else:
            echecs[tuple(des)] = poids / total
    cumuls = [c0]
    if jmax == 0:
        return cumuls

    # Meilleur sous-ensemble à relancer pour chaque lancer en échec
    choix = {}
    for cle in echecs:
        vus, meilleur, best = set(), -1, None
        for S, gardes, F, echelle in plan:
            signature = tuple(cle[i] for i in S)
            if signature in vus:
                continue
            vus.add(signature)
            m = 1
            for i in gardes:
                m |= m << cle[i][1]
            score = ((_vec(m, F) >> (W * tn)) & CHAMP) * echelle
            if score > meilleur:
                meilleur, best = score, (gardes, F)
        choix[cle] = (meilleur / total, best)  # (proba de réussir à la relance, sous-ensemble)
    suivant = {}
    if jmax >= 2:
        for cle, (_, (gardes, F)) in choix.items():
            gardees = [cle[i] for i in gardes]
            den = math.prod(F)
            nxt = defaultdict(float)
            for nouv, w in _issues(F):
                des = sorted(gardees + nouv)
                if not _reussit(des, tn):
                    nxt[tuple(des)] += w / den
            suivant[cle] = nxt

    masse = dict(echecs)
    for j in range(1, jmax + 1):
        gain = sum(x * choix[cle][0] for cle, x in masse.items())
        cumuls.append(cumuls[-1] + gain)
        if j < jmax:
            nouvelle = defaultdict(float)
            for cle, x in masse.items():
                for cle2, q in suivant[cle].items():
                    nouvelle[cle2] += x * q
            masse = nouvelle
    return cumuls


def lois_par_tour(pool, tn, m):
    """
    Pour les modes 0, 1, 2 : liste r telle que r[j] = P(réussir avec exactement j relances),
    j = 0..plafond (le mode 0 n'a que r[0]), et c = P(réussir avec au plus 'plafond' relances).
    """
    p0 = probas(pool, 0)[tn]
    cum1 = [1 - (1 - p0) ** (j + 1) for j in range(m + 1)]

    cle = (pool["num"], tn)
    if len(CACHE_CUMULS.get(cle, [])) < m + 1:
        CACHE_CUMULS[cle] = cumuls_sous_ensemble(pool["faces"], tn, m)
    cum2 = CACHE_CUMULS[cle][:m + 1]

    def lois(cum):
        return [cum[0]] + [cum[j] - cum[j - 1] for j in range(1, len(cum))]

    return [lois([p0]), lois(cum1), lois(cum2)]


def relances_moyennes(r, m):
    """Nombre moyen de relances consommées par tour (plafond m, arrêt dès la réussite)."""
    c = sum(r)
    return sum(j * x for j, x in enumerate(r)) + m * max(0.0, 1 - c)


def series_avec_budget(r, m, n, B, k):
    """
    r[j] : P(réussir un tour avec exactement j relances), j = 0..m.
    Sur n tours, avec un budget total de B relances et au plus m par tour, le joueur
    relance dès qu'il échoue tant que budget et plafond le permettent.
    Renvoie (tous les tours réussis, au moins une réussite, au moins k consécutives).
    """
    # Tous les tours réussis : état = budget restant
    d = {B: 1.0}
    for _ in range(n):
        nd = defaultdict(float)
        for b, x in d.items():
            for j in range(min(m, b) + 1):
                nd[b - j] += x * r[j]
        d = nd
    toujours = sum(d.values())

    # Au moins une réussite : on suit la probabilité d'échouer à tous les tours
    d = {B: 1.0}
    for _ in range(n):
        nd = defaultdict(float)
        for b, x in d.items():
            u = min(m, b)
            nd[b - u] += x * max(0.0, 1 - sum(r[:u + 1]))
        d = nd
    une_fois = 1 - sum(d.values())

    # Au moins k réussites consécutives : état = (budget restant, série en cours)
    d = {(B, 0): 1.0}
    absorbe = 0.0
    for _ in range(n):
        nd = defaultdict(float)
        for (b, serie), x in d.items():
            u = min(m, b)
            cumul = 0.0
            for j in range(u + 1):
                cumul += r[j]
                if serie + 1 >= k:
                    absorbe += x * r[j]
                else:
                    nd[(b - j, serie + 1)] += x * r[j]
            nd[(b - u, 0)] += x * max(0.0, 1 - cumul)
        d = nd
    return toujours, une_fois, absorbe


def calculer_series_budget(pool, tn_min, tn_max, k, B, m):
    """Séries sur n tours pour les 3 modes, avec budget total B et plafond m par tour."""
    lignes = []
    for tn in range(tn_min, tn_max + 1):
        lois = lois_par_tour(pool, tn, m)
        plafonds = [0, m, m]          # sans relance : aucun plafond consommé
        c = [sum(r) for r in lois]
        moyennes = [relances_moyennes(lois[i], plafonds[i]) for i in range(3)]
        for n in range(N_MIN, N_MAX + 1):
            res = [series_avec_budget(lois[i], plafonds[i], n, B, k) for i in range(3)]
            lignes.append({
                "pool_num": pool["num"], "pool": pool["nom"], "k": k, "B": B, "m": m,
                "tn": tn, "n": n, "c": c, "moy": moyennes,
                "lois": lois,
                "toujours": [x[0] for x in res],
                "une_fois": [x[1] for x in res],
                "serie_k": [x[2] for x in res],
            })
    return lignes


def dialoguer_series_budget(resultats):
    """Compare les 3 modes sur n tours avec un nombre de relances limité."""
    num = saisir_entier(f"Numéro du pool (1 à {len(resultats)})", 1, 1, len(resultats))
    pool = resultats[num - 1]

    print(f"Calcul des relances pour {pool['nom']}...")
    t50 = tn_50(probas(pool, 2), pool["maxi"])
    centre = int(round(t50)) if t50 is not None else pool["maxi"] // 2
    tn_min = max(1, centre - 1)
    tn_max = min(pool["maxi"] + 1, centre + 1)
    tn_min = saisir_entier("TN minimum", tn_min, 1, pool["maxi"] + 1)
    tn_max = saisir_entier("TN maximum", tn_max, tn_min, pool["maxi"] + 1)
    k = saisir_entier(f"Nombre k de réussites consécutives (1 à {N_MAX})",
                      K_DEFAUT, 1, N_MAX)
    B = saisir_entier("Budget total de relances sur la séquence (0 à 99)", 4, 0, 99)
    m = saisir_entier(f"Relances maximum par tour (1 à {JMAX})", 2, 1, JMAX)
    if m >= 3:
        print("(Un plafond >= 3 peut prendre quelques instants pour la relance de sous-ensemble.)")

    lignes = calculer_series_budget(pool, tn_min, tn_max, k, B, m)
    SERIES_BUDGET.extend(lignes)

    print(f"\nRELANCES NÉCESSAIRES PAR TOUR : {pool['nom']} (plafond {m} par tour)\n")
    print("TN\tMode\t" + "\t".join(f"Exactement {j} relance(s) (%)" for j in range(m + 1))
          + "\tRéussite totale (%)\tRelances moyennes consommées")
    vus = set()
    for l in lignes:
        if l["tn"] in vus:
            continue
        vus.add(l["tn"])
        for i, nom_mode in enumerate(("sans relance", "relance de tous",
                                      "relance sous-ensemble")):
            r = l["lois"][i]
            cols = [fmt(x * 100) for x in r] + [""] * (m + 1 - len(r))
            print(f"{l['tn']}\t{nom_mode}\t" + "\t".join(cols)
                  + f"\t{fmt(l['c'][i] * 100)}\t{fmt(l['moy'][i])}")

    print(f"\nSÉRIES AVEC RELANCES LIMITÉES : {pool['nom']} "
          f"(k = {k}, budget {B}, plafond {m} par tour)\n")
    print("TN\tn tours\t"
          "Tous les tours : sans (%)\ttous (%)\tsous-ens. (%)\t"
          "Au moins 1 : sans (%)\ttous (%)\tsous-ens. (%)\t"
          f"Au moins {k} consécutives : sans (%)\ttous (%)\tsous-ens. (%)")
    for l in lignes:
        cols = [str(l["tn"]), str(l["n"])]
        for cle in ("toujours", "une_fois", "serie_k"):
            cols += [fmt(x * 100) for x in l[cle]]
        print("\t".join(cols))


# ---------------------------------------------------------------------------
# 6. Comparaison des modes sur un tour
# ---------------------------------------------------------------------------

def ligne_comparaison(r, tn):
    """
    Calcule les trois probabilités pour un pool et un TN, convertit les gains
    en points de TN, et enregistre la ligne pour l'export CSV.
    """
    p0 = probas(r, 0)
    p1 = probas(r, 1)
    p2 = probas(r, 2)
    q0 = p0.get(tn, 0.0)
    q1 = p1.get(tn, 0.0)
    q2 = p2.get(tn, 0.0)

    eq1 = tn_equivalent(p0, q1, r["maxi"])
    eq2 = tn_equivalent(p0, q2, r["maxi"])

    ligne = {
        "num": r["num"], "pool": r["nom"], "tn": tn,
        "p0": q0, "p1": q1, "p2": q2,
        "g1": q1 - q0, "g2": q2 - q0, "g21": q2 - q1,
        "eq1": eq1, "eq2": eq2,
        "pts1": None if eq1 is None else tn - eq1,
        "pts2": None if eq2 is None else tn - eq2,
    }
    # Points de TN rapportés à l'espérance du pool (comparables d'un pool à l'autre)
    ligne["ne1"] = None if ligne["pts1"] is None else ligne["pts1"] / r["esp"]
    ligne["ne2"] = None if ligne["pts2"] is None else ligne["pts2"] / r["esp"]
    COMPARAISONS[(r["num"], tn)] = ligne
    return ligne


def fmt_pts(x):
    return "n/a" if x is None else fmt(x, 1)


def fmt_pct(x):
    """Rapport (0,25) affiché en pourcentage (25,0), ou n/a."""
    return "n/a" if x is None else fmt(x * 100, 1)


def texte_ligne_comparaison(l):
    return (f"{l['num']}\t{l['pool']}\t{l['tn']}\t"
            f"{fmt(l['p0'] * 100)}\t{fmt(l['p1'] * 100)}\t{fmt(l['p2'] * 100)}\t"
            f"{fmt(l['g1'] * 100)}\t{fmt(l['g2'] * 100)}\t{fmt(l['g21'] * 100)}\t"
            f"{fmt_pts(l['pts1'])}\t{fmt_pts(l['pts2'])}\t"
            f"{fmt_pct(l['ne1'])}\t{fmt_pct(l['ne2'])}")


ENTETE_COMPARAISON = ("N°\tPool\tTN\tp sans (%)\tp relance tous (%)\tp relance sous-ens. (%)\t"
                      "Gain tous (pts)\tGain sous-ens. (pts)\tSous-ens. − tous (pts)\t"
                      "Points de TN (tous)\tPoints de TN (sous-ens.)\t"
                      "Points de TN / espérance, tous (%)\t"
                      "Points de TN / espérance, sous-ens. (%)")


def afficher_comparaison(r):
    """Compare les trois modes sur tous les TN d'un pool, et enregistre les lignes."""
    print(f"\nCalcul des relances pour {r['nom']} (peut prendre quelques instants)...")
    probas(r, 2)  # calcul unique, mis en cache
    print(f"\nCOMPARAISON DES MODES : {r['nom']}\n")
    print(ENTETE_COMPARAISON)
    for tn in range(1, r["maxi"] + 2):
        print(texte_ligne_comparaison(ligne_comparaison(r, tn)))
    print("\nLignes ajoutées à l'export (commande s).")


def comparer_tous_pools(resultats):
    """Compare les trois modes sur un même TN, pour tous les pools."""
    print("Référence de TN : 1 = TN 50 % sans relance propre à chaque pool | "
          "2 = TN fixe commun")
    mode_tn = saisir_entier("Référence", 2, 1, 2)
    tn_fixe = None
    if mode_tn == 2:
        tn_fixe = saisir_entier("TN commun", 14, 1, 100)

    print(f"\nCalcul en cours pour les {len(resultats)} pools "
          f"(le mode 2 peut être long)...")
    precalculer_relances(resultats)

    lignes = []
    for r in resultats:
        if mode_tn == 1:
            t = tn_50(probas(r, 0), r["maxi"])
            tn = int(round(t)) if t is not None else r["maxi"] // 2
            tn = max(1, min(tn, r["maxi"] + 1))
        else:
            tn = tn_fixe
        lignes.append(ligne_comparaison(r, tn))

    print("\nCOMPARAISON DES RELANCES SUR UN TOUR, TOUS LES POOLS\n")
    print(ENTETE_COMPARAISON)
    for l in lignes:
        print(texte_ligne_comparaison(l))

    classement = sorted(lignes, key=lambda l: l["pts2"] if l["pts2"] is not None else 0,
                        reverse=True)
    print("\nCLASSEMENT (points de TN gagnés grâce à la relance d'un sous-ensemble)")
    for rang, l in enumerate(classement[:5], 1):
        print(f"  {rang}. {l['pool']} (TN {l['tn']}) : +{fmt_pts(l['pts2'])} pts de TN")
    print("  ...")
    for rang, l in enumerate(classement[-5:], len(classement) - 4):
        print(f"  {rang}. {l['pool']} (TN {l['tn']}) : +{fmt_pts(l['pts2'])} pts de TN")

    print("\nSYNTHÈSE : points de TN rapportés à l'espérance du pool")
    for libelle, cle in (("relance de tous les dés", "ne1"),
                         ("relance d'un sous-ensemble", "ne2")):
        v = [l[cle] for l in lignes if l[cle] is not None]
        if v:
            moy = sum(v) / len(v)
            ecart = math.sqrt(sum((x - moy) ** 2 for x in v) / len(v))
            print(f"  {libelle} : moyenne {fmt_pct(moy)} % | min {fmt_pct(min(v))} % | "
                  f"max {fmt_pct(max(v))} % | écart-type {fmt_pct(ecart)} pts")
    if mode_tn == 2:
        print("  (Attention : avec un TN commun, les pools sont dans des régimes de "
              "réussite très différents ; la référence 1 est plus comparable.)")
    print("\nLignes ajoutées à l'export (commande s).")


# ---------------------------------------------------------------------------
# 7. Formatage et affichage
# ---------------------------------------------------------------------------

def fmt(x, dec=2):
    """Nombre au format français (virgule décimale), pour Excel."""
    return f"{x:.{dec}f}".replace(".", ",")


def calculer_tout():
    pools = sorted(generer_pools(), key=lambda p: statistiques(p)[0])
    assert len(pools) == 33, f"Nombre de pools inattendu : {len(pools)}"

    resultats = []
    print("Calcul en cours, veuillez patienter...\n")
    for i, faces in enumerate(pools, 1):
        total, compte, maxi = analyser(faces)
        esp, sig = statistiques(faces)
        p0 = {tn: compte[tn] / total for tn in range(1, maxi + 2)}
        t50 = tn_50(p0, maxi)
        resultats.append({
            "num": i, "faces": faces, "nom": nom(faces),
            "esp": esp, "sig": sig, "t50": t50,
            "compte": compte, "total": total, "maxi": maxi,
            "amel4": nombre_ameliorations(faces) == 4,
        })
    return resultats


def afficher_recap(resultats):
    print("\nRÉCAPITULATIF (copier-coller dans Excel)\n")
    print("N°\tPool\tEspérance\tÉcart-type\tTN 50 %\t4 amélior.\tLancers")
    for r in resultats:
        t50 = fmt(r["t50"]) if r["t50"] is not None else "n/a"
        print(f"{r['num']}\t{r['nom']}\t{fmt(r['esp'])}\t{fmt(r['sig'])}\t"
              f"{t50}\t{'oui' if r['amel4'] else 'non'}\t{r['total']}")


def afficher_table(r):
    print(f"\nTABLE COMPLÈTE : {r['nom']} ({r['total']} lancers)\n")
    print("TN\tLancers valides\tTotal\tProbabilité (%)")
    for tn in range(1, r["maxi"] + 2):
        n = r["compte"][tn]
        print(f"{tn}\t{n}\t{r['total']}\t{fmt(n / r['total'] * 100, 1)}")


def saisir_entier(message, defaut, minimum, maximum):
    """Demande un entier borné ; Entrée renvoie la valeur par défaut."""
    while True:
        brut = input(f"{message} [{defaut}] : ").strip()
        if brut == "":
            return defaut
        if brut.isdigit() and minimum <= int(brut) <= maximum:
            return int(brut)
        print(f"Valeur invalide : entrez un entier entre {minimum} et {maximum}, "
              f"ou Entrée pour {defaut}.")


def dialoguer_series(resultats):
    """Demande le pool, le mode de relance, la plage de TN et k, puis affiche les séries."""
    num = saisir_entier(f"Numéro du pool (1 à {len(resultats)})", 1, 1, len(resultats))
    r = resultats[num - 1]

    print("Modes de relance : 0 = sans relance | 1 = relance de tous les dés | "
          "2 = relance d'un sous-ensemble choisi")
    mode = saisir_entier("Mode", 0, 0, 2)

    p_par_tn = probas(r, mode)
    t50_mode = tn_50(p_par_tn, r["maxi"])
    centre = int(round(t50_mode)) if t50_mode is not None else r["maxi"] // 2
    tn_min = max(1, centre - 3)
    tn_max = min(r["maxi"] + 1, centre + 3)
    tn_min = saisir_entier("TN minimum", tn_min, 1, r["maxi"] + 1)
    tn_max = saisir_entier("TN maximum", tn_max, tn_min, r["maxi"] + 1)
    k = saisir_entier(f"Nombre k de réussites consécutives (1 à {N_MAX})",
                      K_DEFAUT, 1, N_MAX)

    lignes = calculer_series(r, tn_min, tn_max, k, mode)
    SERIES_CALCULEES.extend(lignes)

    print(f"\nSÉRIES : {r['nom']} ({MODES[mode]}, k = {k})\n")
    print("TN\tp (%)\tn tours\tRéussir tous les tours (%)\t"
          f"Au moins 1 réussite (%)\tAu moins {k} consécutives (%)")
    for l in lignes:
        print(f"{l['tn']}\t{fmt(l['p'] * 100)}\t{l['n']}\t"
              f"{fmt(l['toujours'] * 100)}\t{fmt(l['une_fois'] * 100)}\t"
              f"{fmt(l['serie_k'] * 100)}")


def sauvegarder_csv(resultats):
    # Séparateur « ; » et encodage utf-8-sig : Excel en français ouvre le fichier directement
    with open(FICHIER_RECAP, "w", encoding="utf-8-sig", newline="") as f:
        f.write("N°;Pool;Espérance;Écart-type;TN 50 %;4 amélior.;Lancers\n")
        for r in resultats:
            t50 = fmt(r["t50"]) if r["t50"] is not None else "n/a"
            f.write(f"{r['num']};{r['nom']};{fmt(r['esp'])};{fmt(r['sig'])};"
                    f"{t50};{'oui' if r['amel4'] else 'non'};{r['total']}\n")

    with open(FICHIER_CSV, "w", encoding="utf-8-sig", newline="") as f:
        f.write("N°;Pool;TN;Lancers valides;Total;Probabilité (%)\n")
        for r in resultats:
            for tn in range(1, r["maxi"] + 2):
                n = r["compte"][tn]
                f.write(f"{r['num']};{r['nom']};{tn};{n};{r['total']};"
                        f"{fmt(n / r['total'] * 100, 1)}\n")

    fichiers = [FICHIER_RECAP, FICHIER_CSV]

    if SERIES_CALCULEES:
        with open(FICHIER_SERIES, "w", encoding="utf-8-sig", newline="") as f:
            f.write("N°;Pool;Mode;k;TN;p (%);Tours n;Tous les tours (%);"
                    "Au moins 1 réussite (%);Au moins k consécutives (%)\n")
            for l in SERIES_CALCULEES:
                f.write(f"{l['pool_num']};{l['pool']};{l['mode']};{l['k']};{l['tn']};"
                        f"{fmt(l['p'] * 100)};{l['n']};{fmt(l['toujours'] * 100)};"
                        f"{fmt(l['une_fois'] * 100)};{fmt(l['serie_k'] * 100)}\n")
        fichiers.append(FICHIER_SERIES)

    if SERIES_COMPAREES:
        with open(FICHIER_SERIES_COMPAREES, "w", encoding="utf-8-sig", newline="") as f:
            f.write("N°;Pool;k;TN;Tours n;p sans (%);p relance tous (%);p relance sous-ens. (%);"
                    "Tous les tours sans (%);Tous les tours relance tous (%);"
                    "Tous les tours relance sous-ens. (%);"
                    "Au moins 1 sans (%);Au moins 1 relance tous (%);"
                    "Au moins 1 relance sous-ens. (%);"
                    "Au moins k consécutives sans (%);Au moins k consécutives relance tous (%);"
                    "Au moins k consécutives relance sous-ens. (%)\n")
            for l in SERIES_COMPAREES:
                vals = l["p"] + l["toujours"] + l["une_fois"] + l["serie_k"]
                f.write(f"{l['pool_num']};{l['pool']};{l['k']};{l['tn']};{l['n']};"
                        + ";".join(fmt(x * 100) for x in vals) + "\n")
        fichiers.append(FICHIER_SERIES_COMPAREES)

    if SERIES_BUDGET:
        with open(FICHIER_SERIES_BUDGET, "w", encoding="utf-8-sig", newline="") as f:
            f.write("N°;Pool;k;Budget total;Plafond par tour;TN;Tours n;"
                    "Réussite par tour sans (%);Réussite par tour relance tous (%);"
                    "Réussite par tour relance sous-ens. (%);"
                    "Relances moyennes par tour tous;Relances moyennes par tour sous-ens.;"
                    "Tous les tours sans (%);Tous les tours relance tous (%);"
                    "Tous les tours relance sous-ens. (%);"
                    "Au moins 1 sans (%);Au moins 1 relance tous (%);"
                    "Au moins 1 relance sous-ens. (%);"
                    "Au moins k consécutives sans (%);Au moins k consécutives relance tous (%);"
                    "Au moins k consécutives relance sous-ens. (%)\n")
            for l in SERIES_BUDGET:
                vals = l["c"] + l["toujours"] + l["une_fois"] + l["serie_k"]
                pct = [fmt(x * 100) for x in vals]
                f.write(f"{l['pool_num']};{l['pool']};{l['k']};{l['B']};{l['m']};"
                        f"{l['tn']};{l['n']};" + ";".join(pct[:3]) + ";"
                        f"{fmt(l['moy'][1])};{fmt(l['moy'][2])};" + ";".join(pct[3:]) + "\n")
        fichiers.append(FICHIER_SERIES_BUDGET)

    if COMPARAISONS:
        with open(FICHIER_COMPARAISON, "w", encoding="utf-8-sig", newline="") as f:
            f.write("N°;Pool;TN;p sans relance (%);p relance tous (%);"
                    "p relance sous-ensemble (%);Gain relance tous (pts);"
                    "Gain relance sous-ensemble (pts);Sous-ensemble − tous (pts);"
                    "Points de TN (tous);Points de TN (sous-ensemble);"
                    "Points de TN / espérance tous (%);"
                    "Points de TN / espérance sous-ensemble (%)\n")
            for cle in sorted(COMPARAISONS):
                l = COMPARAISONS[cle]
                f.write(f"{l['num']};{l['pool']};{l['tn']};"
                        f"{fmt(l['p0'] * 100)};{fmt(l['p1'] * 100)};{fmt(l['p2'] * 100)};"
                        f"{fmt(l['g1'] * 100)};{fmt(l['g2'] * 100)};{fmt(l['g21'] * 100)};"
                        f"{fmt_pts(l['pts1'])};{fmt_pts(l['pts2'])};"
                        f"{fmt_pct(l['ne1'])};{fmt_pct(l['ne2'])}\n")
        fichiers.append(FICHIER_COMPARAISON)
    else:
        print("\nAucune comparaison à enregistrer : utilisez c ou m avant s.")

    dossier = os.getcwd()
    print(f"\nFichiers enregistrés dans {dossier} :")
    for nom_fichier in fichiers:
        print(f"  - {nom_fichier}")


# ---------------------------------------------------------------------------
# 8. Programme principal
# ---------------------------------------------------------------------------

def main():
    resultats = calculer_tout()
    afficher_recap(resultats)

    print("\n* Commandes : numéro de pool (1 à 33) pour sa table | "
          "c = comparer les relances d'un pool (tous les TN) | "
          "m = comparer les relances sur un TN, pour tous les pools | "
          "t = séries sur plusieurs tours (un mode) | k = séries comparant les 3 modes | b = séries avec relances limitées | r = revoir le récapitulatif | "
          "s = enregistrer les CSV | Entrée = quitter")

    while True:
        choix = input("\nVotre choix : ").strip().lower()
        if choix == "":
            break
        if choix == "r":
            afficher_recap(resultats)
        elif choix == "s":
            sauvegarder_csv(resultats)
        elif choix == "t":
            dialoguer_series(resultats)
        elif choix == "k":
            dialoguer_series_comparees(resultats)
        elif choix == "b":
            dialoguer_series_budget(resultats)
        elif choix == "c":
            num = saisir_entier(f"Numéro du pool (1 à {len(resultats)})", 1, 1, len(resultats))
            afficher_comparaison(resultats[num - 1])
        elif choix == "m":
            comparer_tous_pools(resultats)
        elif choix.isdigit() and 1 <= int(choix) <= len(resultats):
            afficher_table(resultats[int(choix) - 1])
        else:
            print(f"Choix invalide : entrez un numéro entre 1 et {len(resultats)}, "
                  "c, m, t, k, b, r, s ou Entrée.")

    print("Au revoir.")


if __name__ == "__main__":
    main()