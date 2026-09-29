# Course V2 — Position & Efficacité

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

## FACT

- Protocole analytique déterministe : **2 courbes × 11 positions**, **18
  builds** (3 départs × 3 allocations × 2 courbes), puis **52 états locaux de
  course** à AS−1/AS/AS+1 lorsque légaux. Zéro seed, partie, tour ou
  Monte-Carlo. Baseline inspectée : `4f7fb9d`.
- Domaine fermé : `EF=0`, `VMA=10`. `LINEAR: C0=5+x`.
  `CONVEX: C0=5+0,8x+0,05x²`; ces petits coefficients non calibrés donnent une
  convexité modérée. Une unité d'Efficacité retire une unité de coût.
- L'unique enveloppe testée est
  `min(C0(AS)-C0(EF), C0(VMA)-C0(AS))`. Aucun coefficient n'a été modifié après
  lecture des résultats.
- Les départs LOW/MID/HIGH valent 2/5/8. Chaque build dépense quatre paliers :
  FULL_POSITION 4/0, BALANCED 2/2, FULL_EFFICIENCY 0/4. POSITION est bornée à
  VMA; aucune conversion automatique d'un palier POSITION saturé n'est faite.
- E4 répète seulement un coût pendant 4/8/12 segments. ECO s'applique à l'AS
  active; les allures adjacentes sont des contre-factuels locaux au coût natif.
  Aucun score, pacing, réserve, difficulté ou moteur de course n'est ajouté.

## RESULTS E1

Les deux C0 sont strictement croissantes. LINEAR progresse toujours de 1;
CONVEX progresse de 0,85 à 1,75 par position. Le coût EF vaut 5 dans les deux
cas; le coût VMA vaut respectivement 15 et 18.

## RESULTS E2

`min` est le coût minimum atteignable par une ECO arbitrairement grande.

| Courbe | x | C0 | ECO_MAX | min |
|---|---:|---:|---:|---:|
| LINEAR | 0 | 5 | 0 | 5 |
| LINEAR | 1 | 6 | 1 | 5 |
| LINEAR | 2 | 7 | 2 | 5 |
| LINEAR | 3 | 8 | 3 | 5 |
| LINEAR | 4 | 9 | 4 | 5 |
| LINEAR | 5 | 10 | 5 | 5 |
| LINEAR | 6 | 11 | 4 | 7 |
| LINEAR | 7 | 12 | 3 | 9 |
| LINEAR | 8 | 13 | 2 | 11 |
| LINEAR | 9 | 14 | 1 | 13 |
| LINEAR | 10 | 15 | 0 | 15 |
| CONVEX | 0 | 5 | 0 | 5 |
| CONVEX | 1 | 5,85 | 0,85 | 5 |
| CONVEX | 2 | 6,8 | 1,8 | 5 |
| CONVEX | 3 | 7,85 | 2,85 | 5 |
| CONVEX | 4 | 9 | 4 | 5 |
| CONVEX | 5 | 10,25 | 5,25 | 5 |
| CONVEX | 6 | 11,6 | 6,4 | 5,2 |
| CONVEX | 7 | 13,05 | 4,95 | 8,1 |
| CONVEX | 8 | 14,6 | 3,4 | 11,2 |
| CONVEX | 9 | 16,25 | 1,75 | 14,5 |
| CONVEX | 10 | 18 | 0 | 18 |

Les distances à EF et VMA, présentes exhaustivement dans `results.json`, sont
les deux opérandes dont `ECO_MAX` prend le minimum.

## RESULTS E3

| Courbe | Départ | Build | AS | ECO brute | effective | perdue | coût final |
|---|---|---|---:|---:|---:|---:|---:|
| LINEAR | LOW | FULL_POSITION | 6 | 0 | 0 | 0 | 11 |
| LINEAR | LOW | BALANCED | 4 | 2 | 2 | 0 | 7 |
| LINEAR | LOW | FULL_EFFICIENCY | 2 | 4 | 2 | 2 | 5 |
| LINEAR | MID | FULL_POSITION | 9 | 0 | 0 | 0 | 14 |
| LINEAR | MID | BALANCED | 7 | 2 | 2 | 0 | 10 |
| LINEAR | MID | FULL_EFFICIENCY | 5 | 4 | 4 | 0 | 6 |
| LINEAR | HIGH | FULL_POSITION | 10 | 0 | 0 | 0 | 15 |
| LINEAR | HIGH | BALANCED | 10 | 2 | 0 | 2 | 15 |
| LINEAR | HIGH | FULL_EFFICIENCY | 8 | 4 | 2 | 2 | 11 |
| CONVEX | LOW | FULL_POSITION | 6 | 0 | 0 | 0 | 11,6 |
| CONVEX | LOW | BALANCED | 4 | 2 | 2 | 0 | 7 |
| CONVEX | LOW | FULL_EFFICIENCY | 2 | 4 | 1,8 | 2,2 | 5 |
| CONVEX | MID | FULL_POSITION | 9 | 0 | 0 | 0 | 16,25 |
| CONVEX | MID | BALANCED | 7 | 2 | 2 | 0 | 11,05 |
| CONVEX | MID | FULL_EFFICIENCY | 5 | 4 | 4 | 0 | 6,25 |
| CONVEX | HIGH | FULL_POSITION | 10 | 0 | 0 | 0 | 18 |
| CONVEX | HIGH | BALANCED | 10 | 2 | 0 | 2 | 18 |
| CONVEX | HIGH | FULL_EFFICIENCY | 8 | 4 | 3,4 | 0,6 | 11,2 |

**Rendement marginal.** Le prochain palier EFFICACITÉ réduit le coût de 1 dans
10/18 états et de 0 dans les 8 états déjà saturés ou à VMA. Le prochain
POSITION change aussi l'enveloppe : elle augmente en montant vers son sommet,
puis diminue. Exemple LINEAR/LOW/FULL_EFFICIENCY : passer de 2 à 3 augmente
ECO_MAX de 1, rend une ECO déjà achetée effective et laisse le coût ajusté
inchangé. À l'inverse LINEAR/HIGH/FULL_EFFICIENCY, 8→9 retire 1 de latitude;
le coût ajusté augmente de 2 (C0 +1 et ECO effective −1). Sous CONVEX le même
cas 8→9 augmente le coût de 3,3. Tous les détails sont dans `marginals`.

## RESULTS E4

Chaque cellule est `allure: coût×4/coût×8/coût×12`.

| Courbe | Départ | Build | répétitions locales |
|---|---|---|---|
| LINEAR | LOW | FULL_POSITION | 5: 40/80/120; **6: 44/88/132**; 7: 48/96/144 |
| LINEAR | LOW | BALANCED | 3: 32/64/96; **4: 28/56/84**; 5: 40/80/120 |
| LINEAR | LOW | FULL_EFFICIENCY | 1: 24/48/72; **2: 20/40/60**; 3: 32/64/96 |
| LINEAR | MID | FULL_POSITION | 8: 52/104/156; **9: 56/112/168**; 10: 60/120/180 |
| LINEAR | MID | BALANCED | 6: 44/88/132; **7: 40/80/120**; 8: 52/104/156 |
| LINEAR | MID | FULL_EFFICIENCY | 4: 36/72/108; **5: 24/48/72**; 6: 44/88/132 |
| LINEAR | HIGH | FULL_POSITION | 9: 56/112/168; **10: 60/120/180** |
| LINEAR | HIGH | BALANCED | 9: 56/112/168; **10: 60/120/180** |
| LINEAR | HIGH | FULL_EFFICIENCY | 7: 48/96/144; **8: 44/88/132**; 9: 56/112/168 |
| CONVEX | LOW | FULL_POSITION | 5: 41/82/123; **6: 46,4/92,8/139,2**; 7: 52,2/104,4/156,6 |
| CONVEX | LOW | BALANCED | 3: 31,4/62,8/94,2; **4: 28/56/84**; 5: 41/82/123 |
| CONVEX | LOW | FULL_EFFICIENCY | 1: 23,4/46,8/70,2; **2: 20/40/60**; 3: 31,4/62,8/94,2 |
| CONVEX | MID | FULL_POSITION | 8: 58,4/116,8/175,2; **9: 65/130/195**; 10: 72/144/216 |
| CONVEX | MID | BALANCED | 6: 46,4/92,8/139,2; **7: 44,2/88,4/132,6**; 8: 58,4/116,8/175,2 |
| CONVEX | MID | FULL_EFFICIENCY | 4: 36/72/108; **5: 25/50/75**; 6: 46,4/92,8/139,2 |
| CONVEX | HIGH | FULL_POSITION | 9: 65/130/195; **10: 72/144/216** |
| CONVEX | HIGH | BALANCED | 9: 65/130/195; **10: 72/144/216** |
| CONVEX | HIGH | FULL_EFFICIENCY | 7: 52,2/104,4/156,6; **8: 44,8/89,6/134,4**; 9: 65/130/195 |

## OBSERVATIONS

1. **Q1 — Oui.** Les 22 positions passent le contrôle : aucun coût minimum
   atteignable n'est inférieur à 5, le coût EF.
2. **Q2 — Oui.** À x=9, la latitude n'est plus que 1 (linéaire) ou 1,75
   (convexe), puis 0 à VMA. Dans les builds HIGH, 0,6 à 2 points d'ECO sont
   déjà perdus avant VMA, et toute ECO est perdue à VMA.
3. **Q3 — Oui.** Le maximum apparaît au milieu : 5 à x=5 en linéaire; 6,4 à
   x=6 en convexe. Les deux extrémités valent 0.
4. **Q4 — Oui, mécaniquement.** À départ MID linéaire, les trois builds
   terminent respectivement à AS 9/7/5 et coûtent 14/10/6 à leur AS. E4 rend
   ces différences proportionnelles à 4/8/12 segments. Cela ne démontre pas
   leur équilibre stratégique faute d'objectif commun ou de score final.
5. **Q5 — Oui.** POSITION peut augmenter la latitude avant le sommet, puis la
   réduire après celui-ci; il peut donc réactiver ou saturer EFFICACITÉ.
6. **Q6 — L'amplitude et le sommet changent, pas la conclusion structurelle.**
   La convexité déplace le maximum de x=5 à x=6 et l'élève de 5 à 6,4. Les
   bornes nulles, la zone intermédiaire et l'interaction marginale subsistent.

## INTERPRETATIONS

- La règle unique satisfait le critère d'arrêt demandé et constitue une base
  assez robuste pour **revenir au Game Design** : les cinq formes attendues
  (zéro/faible/fort/faible/zéro) existent sous les deux seules courbes testées.
- Aucun choix n'est toujours dominant dans les conséquences mesurées :
  POSITION obtient une AS supérieure mais accroît le coût natif; EFFICACITÉ
  réduit le coût répété mais sature aux bords. Cette distinction ne dit pas
  lequel gagne une course.
- Le déplacement de l'AS après le sommet produit un effet renforcé : coût natif
  croissant et latitude ECO décroissante. C'est une conséquence de la formule,
  particulièrement visible avec la convexité, à soumettre au design plutôt
  qu'à corriger dans cette sonde.

## LIMITS

- Les coefficients, l'échelle 0..10, les trois départs, quatre paliers et une
  unité de coût par ECO sont des paramètres de sonde non calibrés.
- E4 n'est pas Race Engine V2. Son application ECO uniquement à l'AS est une
  convention isolante; aucune largeur de zone d'efficacité n'est testée.
- POSITION saturée à VMA n'est ni remboursée ni convertie. FULL_POSITION et
  BALANCED HIGH convergent donc à AS 10, et le tableau ne mesure pas leurs
  paliers POSITION inutilisables.
- « Stratégique » signifie ici conséquences distinctes et rendement dépendant
  de l'état, pas qualité du choix humain, équilibre ou performance finale.
- Signal à surveiller : après le sommet, POSITION augmente parfois le coût
  ajusté de plus que la seule hausse C0 (jusqu'à +3,3 observé), car elle réduit
  simultanément ECO effective. Aucun des autres signaux d'échec demandés
  (dominance universelle, zone absente/universelle, instabilité) n'apparaît.

## DESIGN QUESTIONS

1. L'amplification après le sommet (hausse C0 + perte de latitude ECO) est-elle
   une interaction voulue de POSITION, ou une pénalité trop forte ?
2. Une EFFICACITÉ future doit-elle rester strictement attachée à l'AS active ou
   couvrir une zone d'allures ?
3. Un palier POSITION impossible à VMA doit-il être interdit, perdu ou dirigé
   vers un autre choix ?
4. Le sommet d'ECO_MAX doit-il pouvoir se déplacer avec la forme de C0, comme
   x=6 sous la courbe convexe, ou doit-il être centré en position ?

