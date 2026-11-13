"""
course_marathon.py : simulation d'une course par tours consécutifs.

À lancer dans le même dossier que pools_optimise_sans_numpy.py :
    python course_marathon.py

RAPPEL DU MODÈLE
----------------
* À chaque tour, le coureur lance son pool de dés. Le résultat est un MENU :
  toutes les sommes de sous-ensembles possibles. Il choisit une énergie E dans ce menu.
* L'énergie E est convertie en vitesse (km/h) par une courbe. Le TN est l'énergie de
  l'allure AS42 ; la zone TN-1..TN+1 donne la vitesse AS42 (elle « tolère » ±1).
* Chaque choix coûte de la JAUGE de soutenabilité :
      E <= TN-3        : 0            (zone EF, rien ne se vide)
      TN-3 < E < TN-1  : coût faible, croissant
      TN-1 <= E <= TN+1: 1            (zone TN)
      E > TN+1         : E - TN       (de plus en plus vite)
* MUR : quand la jauge est vide (<= 0) au début d'un tour, toute la courbe de vitesse
  est translatée vers le bas (pénalité en km/h). Si on continue à dépenser alors que la
  jauge est vide, on creuse une « dette » et la pénalité augmente.
* RELANCES : un stock limité pour toute la course. Types : 0 = aucune, 1 = tous les dés,
  2 = sous-ensemble choisi (on garde certains dés, on relance les autres).
* Dernier tour : la jauge ne sert plus à rien après l'arrivée, donc on peut tout dépenser
  (sprint final). Le mur est évalué au DÉBUT du tour, donc le dernier tour est « gratuit ».

LA STRATÉGIE (ce n'est PAS un optimum exact, c'est une règle de pilotage)
------------------------------------------------------------------------
Un calcul d'optimum exact (programmation dynamique) serait trop lourd en Python pur avec
les relances de sous-ensemble. On utilise donc une règle simple, inspirée de l'optimisation
sous contrainte (multiplicateur de Lagrange) :
  1. On calcule « l'enveloppe concave » des couples (coût, vitesse) : ce sont les allures
     efficaces. Entre deux sommets de l'enveloppe, on peut alterner (ex. EF / zone TN).
  2. On vise un coût moyen par tour = jauge restante / tours restants (hors dernier tour).
  3. Pour alterner, on suit une jauge « de référence » qui décroît linéairement : si on est
     au-dessus de cette référence, on vise le niveau haut (zone TN), sinon le niveau bas (EF).
  4. On relance quand on vise le niveau haut et que le menu ne le contient pas, tant qu'il
     reste assez de relances (paramètre rho = réserve de relances par tour restant).
  5. On teste plusieurs valeurs de rho et on garde la meilleure.
Si le comportement obtenu ressemble à un vrai marathon, c'est bon signe pour le modèle ;
si une règle de pilotage trouve une stratégie « absurde » très rentable, c'est un signal
que la courbe de coût ou de vitesse est à corriger.
"""

import itertools
import math
import random
import statistics

import dicererolloptimized as P   # pools, masques de sommes, mémoïsation

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES D'ÉQUILIBRAGE (tous modifiables)
# ---------------------------------------------------------------------------

# Profils : numéro -> (vitesse AS42, vitesse VMA) en km/h, d'après ta table.
PROFILS = {
    8:  (9, 11),
    9:  (10, 12),
    10: (12, 14),
    11: (13, 15),
    12: (14, 16),
    13: (15, 17),
    14: (16, 19),
    15: (17, 20),
}

ENERGIE_PAR_KMH = 1.4   # points d'énergie nécessaires pour gagner 1 km/h
VITESSE_MIN = 3.0       # la vitesse ne descend jamais sous cette valeur (km/h)

COUT_ZONE = 1.0         # coût d'un tour dans la zone TN-1..TN+1
DIST_EF = 3             # à TN-3 et en dessous : coût nul (zone EF)
PENTE_SOUS_TN = 0.5     # coût ajouté par point d'énergie entre TN-3 et TN-1

MUR_BASE = 2.0          # km/h perdus dès que la jauge est vide (translation de la courbe)
MUR_PENTE = 0.5         # km/h perdus en plus par point de dette de jauge
MUR_MAX = 6.0           # pénalité maximale

PLAFOND_PAR_TOUR = 3    # relances maximum utilisées dans un même tour
MARGE = 0.05            # petite marge qui départage deux choix de même valeur
RHOS = (0.0, 0.15, 0.3, 0.5, 0.8)   # réserves de relances testées (par tour restant)


# ---------------------------------------------------------------------------
# 2. LA COURSE : courbes énergie -> vitesse et énergie -> coût
# ---------------------------------------------------------------------------

class Course:
    def __init__(self, faces, tn, v_as42, v_vma, tours, jauge):
        self.faces = tuple(sorted(faces))   # dés du pool, triés (mêmes conventions que P)
        self.n = len(self.faces)
        self.total = math.prod(self.faces)
        self.maxi = sum(self.faces)         # énergie maximale possible
        self.tn, self.v0, self.vmax = tn, v_as42, v_vma
        self.tours, self.jauge = tours, jauge
        self._cache_ss = {}                 # mémoire des sous-ensembles choisis

        # Tables indexées par l'énergie E (E = 1 .. maxi)
        self.vitesse = [0.0] * (self.maxi + 2)
        self.cout = [0.0] * (self.maxi + 2)
        for E in range(1, self.maxi + 1):
            self.vitesse[E] = self._vitesse(E)
            self.cout[E] = self._cout(E)
        self.enveloppe = self._enveloppe_concave()

    def _vitesse(self, E):
        """Courbe de conversion : plate dans la zone TN (= AS42), linéaire de part et d'autre."""
        d = E - self.tn
        if abs(d) <= 1:
            v = self.v0
        elif d > 1:
            v = self.v0 + (d - 1) / ENERGIE_PAR_KMH
        else:
            v = self.v0 - (-d - 1) / ENERGIE_PAR_KMH
        return max(VITESSE_MIN, min(v, self.vmax))   # plafonnée à la VMA

    def _cout(self, E):
        """Coût en jauge d'un tour couru à l'énergie E."""
        d = E - self.tn
        if abs(d) <= 1:
            return COUT_ZONE
        if d > 1:
            return float(d)                           # valeur du subset - TN
        return max(0.0, PENTE_SOUS_TN * (d + DIST_EF))  # sous TN : coût faible, puis nul

    def _enveloppe_concave(self):
        """
        Allures « efficaces » : sommets de l'enveloppe concave des points (coût, vitesse).
        Renvoie une liste de (coût, vitesse, E) triée par coût croissant.
        Entre deux sommets on peut alterner pour atteindre n'importe quel coût moyen.
        """
        # Pour chaque couple (coût, vitesse) on retient l'énergie médiane
        groupes = {}
        for E in range(1, self.maxi + 1):
            groupes.setdefault((round(self.cout[E], 6), round(self.vitesse[E], 6)), []).append(E)
        pts = [(c, v, sorted(Es)[len(Es) // 2]) for (c, v), Es in groupes.items()]
        # Pour un même coût, seule la vitesse maximale est intéressante
        meilleur = {}
        for c, v, E in pts:
            if c not in meilleur or v > meilleur[c][1]:
                meilleur[c] = (c, v, E)
        pts = sorted(meilleur.values())
        # On s'arrête dès que la vitesse maximale est atteinte (aller plus haut est inutile)
        vmax_atteinte = max(p[1] for p in pts)
        tronque = []
        for p in pts:
            tronque.append(p)
            if p[1] >= vmax_atteinte - 1e-9:
                break
        # Enveloppe supérieure (chaîne monotone, on retire aussi les points alignés)
        h = []
        for p in tronque:
            while len(h) >= 2:
                a, b = h[-2], h[-1]
                croix = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
                if croix >= 0:
                    h.pop()
                else:
                    break
            h.append(p)
        return h

    def niveaux(self, beta):
        """
        Pour un coût moyen visé beta, renvoie (prix de la jauge, niveau bas, niveau haut).
        Le « prix de la jauge » est la pente de l'enveloppe : km/h gagnés par point de jauge.
        """
        h = self.enveloppe
        if len(h) == 1 or beta >= h[-1][0]:
            return 0.0, h[-1], h[-1]          # jauge très riche : on dépense au maximum
        beta = max(beta, 0.0)
        for a, b in zip(h, h[1:]):
            if a[0] <= beta <= b[0]:
                return (b[1] - a[1]) / (b[0] - a[0]), a, b
        return 0.0, h[-1], h[-1]

    @staticmethod
    def penalite_mur(g):
        """Pénalité de vitesse (km/h) selon la jauge au début du tour."""
        if g > 1e-9:
            return 0.0
        return min(MUR_MAX, MUR_BASE + MUR_PENTE * (-g))

    # -----------------------------------------------------------------------
    # 3. OUTILS DE TOUR : menu, choix d'énergie, choix du sous-ensemble à relancer
    # -----------------------------------------------------------------------

    @staticmethod
    def menu(valeurs):
        """Masque de bits : le bit E vaut 1 si l'énergie E est dans le menu."""
        m = 1
        for v in valeurs:
            m |= m << v
        return m

    def choisir(self, masque, prix, cible_cout):
        """
        Choisit dans le menu l'énergie qui maximise  vitesse - prix * coût.
        (Le terme 1e-3 départage les égalités en préférant le coût proche de cible_cout.)
        """
        meilleur, choix = -1e18, None
        for E in range(1, self.maxi + 1):
            if (masque >> E) & 1:
                j = (self.vitesse[E] - prix * self.cout[E]
                     - 1e-3 * abs(self.cout[E] - cible_cout))
                if j > meilleur:
                    meilleur, choix = j, E
        return choix

    def niveau_present(self, masque, v_min, c_max):
        """Vrai si le menu contient une énergie assez rapide (>= v_min) et pas trop chère."""
        for E in range(1, self.maxi + 1):
            if ((masque >> E) & 1 and self.vitesse[E] >= v_min - 1e-9
                    and self.cout[E] <= c_max + 1e-9):
                return True
        return False

    def sous_ensemble(self, valeurs, cible):
        """
        Quels dés relancer pour maximiser la probabilité d'avoir une somme à cible±1 ?
        On réutilise la mémoïsation de pools_optimise_sans_numpy (_vec) : pour chaque
        sous-ensemble relancé, le nombre d'issues réussissantes est lu dans le champ « cible ».
        Renvoie les INDICES des dés à relancer.
        """
        cle = (tuple(valeurs), cible)
        if cle in self._cache_ss:
            return self._cache_ss[cle]
        meilleur, choix, vus = -1, tuple(range(self.n)), set()
        for k in range(1, self.n + 1):
            for S in itertools.combinations(range(self.n), k):
                signature = tuple(sorted((self.faces[i], valeurs[i]) for i in S))
                if signature in vus:          # relances équivalentes : un seul essai
                    continue
                vus.add(signature)
                F = tuple(sorted(self.faces[i] for i in S))
                m = 1                          # masque des dés GARDÉS
                for i in range(self.n):
                    if i not in S:
                        m |= m << valeurs[i]
                score = (((P._vec(m, F) >> (P.W * cible)) & P.CHAMP)
                         * (self.total // math.prod(F)))
                if score > meilleur:
                    meilleur, choix = score, S
        self._cache_ss[cle] = choix
        return choix

    # -----------------------------------------------------------------------
    # 4. UNE COURSE COMPLÈTE
    # -----------------------------------------------------------------------

    def courir(self, mode, relances, rho, rng):
        """
        Simule une course. mode : 0 aucune relance, 1 tous les dés, 2 sous-ensemble.
        Renvoie un dictionnaire de résultats.
        """
        T, G0 = self.tours, self.jauge
        g, r, score = G0, relances, 0.0
        classes = {"EF": 0, "bas": 0, "TN": 0, "haut": 0}
        tours_mur, utilisees = 0, 0

        for t in range(T):
            L = T - t                      # tours restants, celui-ci inclus
            valeurs = [rng.randint(1, f) for f in self.faces]
            mur = self.penalite_mur(g)
            tours_mur += mur > 0

            # --- 4.1 Que veut-on faire ce tour ? ---------------------------------
            cible_E = None                 # énergie visée si on relance (None = pas de relance)
            v_min = c_max = None           # niveau « satisfaisant » pour arrêter de relancer
            if L == 1:                     # dernier tour : sprint, la jauge ne compte plus
                prix, cible_c = 0.0, 0.0
                cible_E, v_min, c_max = self.enveloppe[-1][2], self.vmax, 1e9
            elif g <= 1e-9:                # mur : chaque point de coût aggrave les tours restants
                prix, cible_c = MUR_PENTE * (L - 1), 0.0
            else:
                beta = g / (L - 1)         # coût moyen affordable (le dernier tour est gratuit)
                prix, bas, haut = self.niveaux(beta)
                # Jauge de référence visée APRÈS ce tour (décroissance linéaire jusqu'à 0)
                ref_apres = G0 * (L - 2) / (T - 1)
                veut_haut = (bas is haut) or (g - haut[0] >= ref_apres - 1e-9)
                if veut_haut:
                    prix *= (1 - MARGE)
                    cible_c = haut[0]
                    cible_E, v_min, c_max = haut[2], haut[1], haut[0]
                else:
                    prix *= (1 + MARGE)
                    cible_c = bas[0]

            # --- 4.2 Relances éventuelles ------------------------------------------
            essais = 0
            while True:
                masque = self.menu(valeurs)
                if (cible_E is None or mode == 0 or r <= 0 or essais >= PLAFOND_PAR_TOUR
                        or self.niveau_present(masque, v_min, c_max)
                        or (L > 1 and r <= rho * (L - 1))):
                    break
                if mode == 1:
                    idx = range(self.n)
                else:
                    idx = self.sous_ensemble(valeurs, cible_E)
                for i in idx:
                    valeurs[i] = rng.randint(1, self.faces[i])
                r -= 1
                essais += 1
                utilisees += 1

            # --- 4.3 Choix de l'énergie et mise à jour ------------------------------
            E = self.choisir(self.menu(valeurs), prix, cible_c)
            score += self.vitesse[E] - mur
            g = max(g - self.cout[E], -20.0)
            c = self.cout[E]
            if c <= 1e-9:
                classes["EF"] += 1
            elif abs(E - self.tn) <= 1:
                classes["TN"] += 1
            elif E > self.tn + 1:
                classes["haut"] += 1
            else:
                classes["bas"] += 1

        return {"score": score, "jauge_fin": g, "relances_restantes": r,
                "classes": classes, "tours_mur": tours_mur, "utilisees": utilisees}


# ---------------------------------------------------------------------------
# 5. ÉVALUATION STATISTIQUE
# ---------------------------------------------------------------------------

def evaluer(course, mode, R, rho, n_courses, graine):
    """Simule n_courses courses (même graine = mêmes dés pour comparer équitablement)."""
    rng = random.Random(graine)
    res = [course.courir(mode, R, rho, rng) for _ in range(n_courses)]
    scores = [x["score"] for x in res]
    ref = course.tours * course.v0          # score d'une course « parfaite » à l'AS42
    return {
        "score": statistics.mean(scores),
        "ecart": statistics.pstdev(scores),
        "pct_ref": statistics.mean(scores) / ref * 100,
        "jauge_fin": statistics.mean(x["jauge_fin"] for x in res),
        "relances_restantes": statistics.mean(x["relances_restantes"] for x in res),
        "pct_mur": statistics.mean(x["tours_mur"] for x in res) / course.tours * 100,
        **{f"pct_{k}": statistics.mean(x["classes"][k] for x in res) / course.tours * 100
           for k in ("EF", "bas", "TN", "haut")},
    }


def meilleure_strategie(course, mode, R, n_recherche, n_final, graine, rhos=RHOS):
    """
    Cherche la meilleure réserve de relances rho sur un premier échantillon, puis
    mesure le résultat sur un second échantillon indépendant (évite un biais optimiste).
    """
    if mode == 0 or R == 0:
        return 0.0, evaluer(course, mode, R, 0.0, n_final, graine + 1)
    meilleur_rho = max(rhos, key=lambda x: evaluer(course, mode, R, x, n_recherche, graine)["score"])
    return meilleur_rho, evaluer(course, mode, R, meilleur_rho, n_final, graine + 1)


# ---------------------------------------------------------------------------
# 6. DIALOGUE
# ---------------------------------------------------------------------------

def f1(x):
    return P.fmt(x, 1)


def main():
    resultats = P.calculer_tout()
    print("\nSIMULATION DE COURSE (voir l'en-tête du fichier pour le modèle)\n")
    num = P.saisir_entier("Numéro du pool (1 à 33)", 13, 1, 33)
    pool = resultats[num - 1]
    t50 = P.tn_50(P.probas(pool, 0), pool["maxi"])
    tn_defaut = max(1, min(int(round(t50)), pool["maxi"])) if t50 else pool["maxi"] // 2
    tn = P.saisir_entier("TN (énergie de l'AS42)", tn_defaut, 1, pool["maxi"])
    profil = P.saisir_entier("Profil (8 à 15)", 12, 8, 15)
    tours = P.saisir_entier("Nombre de tours", 14, 3, 40)
    jauge = P.saisir_entier("Jauge de soutenabilité", 11, 1, 40)
    R = P.saisir_entier("Relances disponibles", 6, 0, 30)

    v0, vmax = PROFILS[profil]
    course = Course(pool["faces"], tn, v0, vmax, tours, jauge)
    print(f"\nPool {pool['nom']} | TN {tn} | profil P{profil} (AS42 {v0} km/h, VMA {vmax}) | "
          f"{tours} tours | jauge {jauge} | {R} relances")
    print("Enveloppe des allures efficaces (coût -> vitesse, énergie) :",
          ", ".join(f"({f1(c)} -> {f1(v)} km/h, E={E})" for c, v, E in course.enveloppe))
    print(f"Taux de jauge : {f1(jauge / (tours - 1))} point par tour (hors dernier tour). "
          f"Part de tours en zone TN attendue : environ "
          f"{f1(min(100, jauge / (tours - 1) * 100))} %.")

    print("\nCalcul en cours (quelques secondes)...")
    noms = {0: "sans relance", 1: "relance de tous les dés", 2: "relance d'un sous-ensemble"}
    print("\nRÉSULTATS (moyenne sur 3000 courses)\n")
    print("Mode\trho\tScore\tÉcart-type\t% de la référence AS42\tJauge à l'arrivée\t"
          "Relances restantes\t% tours EF\t% tours sous TN\t% tours zone TN\t"
          "% tours au-dessus\t% tours avec mur")
    for mode in (0, 1, 2):
        rho, e = meilleure_strategie(course, mode, R, 800, 3000, 1)
        print(f"{noms[mode]}\t{P.fmt(rho)}\t{f1(e['score'])}\t{f1(e['ecart'])}\t"
              f"{f1(e['pct_ref'])}\t{f1(e['jauge_fin'])}\t{f1(e['relances_restantes'])}\t"
              f"{f1(e['pct_EF'])}\t{f1(e['pct_bas'])}\t{f1(e['pct_TN'])}\t"
              f"{f1(e['pct_haut'])}\t{f1(e['pct_mur'])}")

    print("\nSCORE (% de la référence AS42) SELON LE NOMBRE DE RELANCES\n")
    print("Relances\tsans relance\ttous les dés\tsous-ensemble")
    base = evaluer(course, 0, 0, 0.0, 1500, 1)["pct_ref"]
    for nb in (0, 2, 4, 6, 8, 10):
        ligne = [f1(base)]
        for mode in (1, 2):
            _, e = meilleure_strategie(course, mode, nb, 300, 1500, 1, rhos=(0.0, 0.3, 0.8))
            ligne.append(f1(e["pct_ref"]))
        print(f"{nb}\t" + "\t".join(ligne))
    print("\n(Modifie les paramètres en tête de fichier pour tester d'autres équilibrages.)")


if __name__ == "__main__":
    main()
    