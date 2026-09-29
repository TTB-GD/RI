# Training V2 minimale — rapport

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**  Baseline de code observée
avant l'expérience : `231d49e729431c48ce24ebcdd55871b9f9f76302`.

## FACT

- **A** énumère les 1 296 tirages ordonnés équiprobables de 4d6. Le modèle
  local lance tout le pool puis écarte le plus petit dé, sauf lorsqu'un motif
  D99 CURRENT à quatre dés autorise la réserve (`D99_BONUS_ONLY`). Le plafond
  de qualités D99 est ignoré. Toutes les bipartitions physiques non vides sont
  énumérées, avec `EF >= Q`; des dés égaux restent des objets physiques
  distincts. Une « partition pertinente » diffère par énergie EF, énergie Q,
  accès et statut sûr/risqué. Le seuil opérationnel, fixé avant lecture du
  résultat, classe moins de 10 % de lancers multi-programmes comme
  `CHOIX QUASI AUTOMATIQUE`, 10–49,999 % comme `CHOIX FAIBLE`, sinon
  `CHOIX REEL`.
- **B** exécute, puisque A n'a pas déclenché l'arrêt, 200 seeds partagées
  (`0..199`) × 3 politiques × 16 tours = **600 campagnes / 9 600 tours**.
  Chaque politique choisit au plus une progression physiologique par tour,
  avec tie-breaks déterministes. Toute l'énergie des compartiments alimente
  les compteurs; Q n'est créditée que si la qualité choisie réussit. Le bust
  local reprend exactement le principe CURRENT : `k = coût - meilleur dé`,
  meilleur dé du pool, bust sur face brute `<= k`. Les gains s'appliquent en
  fin de tour. Aux paliers EF sans dé, `EF +1` est provisoire et seulement
  appliqué si `EF + 1 < Seuil`; un gain bloqué n'est pas mis en attente. Aux
  paliers Q sans upgrade, rien n'est attribué (simples marqueurs). Les upgrades
  suivent une politique locale répartie et déterministe.
- **C** est une grille analytique, sans Monte-Carlo ni course complète. Quatre
  points SPEC sont répartis entre vitesse et économie pour `FULL_SPEED (4/0)`,
  `BALANCED (2/2)` et `FULL_ECO (0/4)`. Fixtures abstraites explicites : AS42
  basse = Production 18 répétée 10 fois; AS10 haute = Production 23 répétée
  4 fois. Vitesse ajoute à la Production; chaque point d'économie soustrait 1
  au coût Curve B, avec plancher local à zéro. Les coûts sont lus à AS−1, AS et
  AS+1.

## RESULTS

### A — cartographie d'un tour

| Mesure | Résultat |
|---|---:|
| Lancers avec ≥1 partition non triviale | 100,000 % |
| Partitions physiques légales, moyenne | 3,946 |
| Plusieurs partitions pertinentes | 100,000 % |
| Plusieurs programmes énergie/accès distincts | 100,000 % |
| Accès au premier palier EF (10) | 55,633 % |
| Accès Seuil | 99,614 % |
| Accès VMA | 77,623 % |
| Accès simultané Seuil/VMA | 77,623 % |
| Au moins une qualité sûre | 98,765 % |
| Au moins une qualité risquée | 4,398 % |

**Critère : `CHOIX REEL`.** Exemples compacts (lancer final → couples EF/Q) :

- `1,1,1,1 → 3/1, 2/2` (aucune qualité);
- `4,3,2 → 7/2, 6/3, 5/4` (aucune puis Seuil);
- `5,5,2,2 → 12/2, 10/4, 9/5, 7/7` (aucune, Seuil, puis Seuil/VMA);
- `5,4,3 → 9/3, 8/4, 7/5` (Seuil puis Seuil/VMA);
- `6,3,3,3 → 12/3, 9/6` (Seuil puis Seuil/VMA);
- `6,5,4 → 11/4, 10/5, 9/6`;
- `6,6,5,5 → 17/5, 16/6, 12/10, 11/11`;
- `6,6,6,6 → 18/6, 12/12`.

### B — progression sur 16 tours

Chaque cellule est `moyenne [P10 ; médiane ; P90]`.

| Mesure finale | P_EF | P_BALANCED | P_QUALITY |
|---|---:|---:|---:|
| EF | 11,705 [11;12;12] | 11,790 [11;12;12] | 10,910 [10;11;12] |
| Seuil | 13,435 [13;13;14] | 14,550 [14;15;15] | 13,105 [12;13;14] |
| VMA | 14,685 [14;15;15] | 17,830 [17;18;18] | 18,880 [18;19;20] |
| progression EF | 188,270 [171,9;185;209,3] | 157,650 [144;157;172] | 153,300 [139,9;152;169] |
| progression Q | 84,520 [68;83;101] | 123,890 [103,9;124;143] | 112,665 [90;113;132,1] |
| dés | 6 [6;6;6] | 6 [6;6;6] | 6 [6;6;6] |
| upgrades | 3,070 [3;3;4] | 3,940 [4;4;4] | 3,815 [3;4;4] |
| qualités risquées tentées | 0,065 [0;0;0] | 2,355 [1;2;4] | 6,580 [5;7;8] |
| busts | 0,010 [0;0;0] | 0,460 [0;0;1] | 1,905 [0;2;3] |

Les 200 runs de chaque politique finissent à six dés; médiane d'obtention au
tour 11 pour P_EF et 12 pour les deux autres. Les quatre upgrades sont atteints
à T16 dans 13 %, 94 % et 81,5 % des runs respectivement. Tous les marqueurs ont
progressé dans 100 % des runs des trois politiques. Les pools finaux détaillés
et trois trajectoires (`0`, `73`, `199`) par politique sont dans `results.json`.

### C — Spécifique vitesse / économie

| Contexte | Profil | Production à AS | Coût à AS | Coût répété | Réserve économisée par ECO |
|---|---|---:|---:|---:|---:|
| AS42 basse (10×) | FULL_SPEED | 22 | 3 | 30 | 0 |
|  | BALANCED | 20 | 0 | 0 | 20 |
|  | FULL_ECO | 18 | 0 | 0 | 20 |
| AS10 haute (4×) | FULL_SPEED | 27 | 16 | 64 | 0 |
|  | BALANCED | 25 | 8 | 32 | 8 |
|  | FULL_ECO | 23 | 1 | 4 | 16 |

Autour d'AS, FULL_SPEED gagne toujours +3/+4/+5 Production par rapport à
l'AS de contexte. À AS42, le plancher écrase la différence de coût entre
BALANCED et FULL_ECO. À AS10, les trois profils restent distincts : davantage
de Production contre des économies répétées croissantes.

## OBSERVATIONS

- La partition n'est pas structurellement unique dans ce modèle : tous les
  tirages ont plusieurs programmes distincts, même si une part des différences
  ne change pas l'ensemble de qualités accessible.
- Seuil est presque toujours finançable dès la baseline; VMA l'est dans plus de
  trois quarts des tirages. Le risque est rare dans la cartographie initiale.
- Les trois sondes font progresser tous les marqueurs et obtiennent les deux dés
  en 16 tours. P_BALANCED et P_QUALITY obtiennent presque toujours les quatre
  upgrades; P_QUALITY sépare nettement VMA mais tente et subit plus de risque.
- C mesure des bénéfices de nature différente (Production instantanée contre
  coût répété), mais le plancher zéro masque l'économie marginale au contexte
  bas et la courbe convexe amplifie fortement les écarts au contexte haut.

## INTERPRETATIONS

- La partition paraît produire un choix combinatoire réel, mais l'accès Seuil
  quasi universel suggère que le choix porte davantage sur l'allocation et la
  cible que sur l'ouverture de Seuil.
- B présente un signal d'accélération forte plutôt qu'un blocage : les gains de
  pool sont universels et tous les marqueurs progressent. Cela ne suffit pas à
  qualifier l'équilibre, car les politiques maximisent explicitement un
  compartiment et les conventions de dépense sont locales.
- Vitesse et économie ne se dominent pas analytiquement sur les deux axes : la
  première achète de la Production, la seconde de la Reserve. Leur valeur
  relative change avec intensité et répétitions, mais la fixture ECO est trop
  simplifiée pour conclure à un équilibre.

## LIMITS

- Le lancer local n'évalue ni relance ni choix du joueur; il lance chaque dé du
  pool une fois et utilise D99 seulement pour la réserve. `D99_OFF` est testé en
  boundary test mais aucune seconde campagne n'est exécutée.
- Les partitions physiques dupliquent parfois le même programme énergétique
  quand des faces sont égales; le rapport donne aussi les programmes distincts.
- B impose une seule progression physiologique par tour, crédite toute l'énergie
  de compartiment, ne reporte pas un gain EF bloqué, et ne modélise ni fatigue,
  ni catalogue, ni joueur humain. Les politiques ne sont pas optimales.
- Les valeurs AS42/AS10, répétitions et effet linéaire ECO de C sont des fixtures
  abstraites locales. Curve B est réutilisée, mais son domaine terminal agrège
  toute Production ≥27 et le plancher de coût zéro est une convention du harnais.
- Les trajectoires B incluent les effets de leurs choix; elles ne sont donc pas
  des contre-factuels appariés tour par tour après divergence des pools/RNG.

## DESIGN QUESTIONS

1. Une énergie Q doit-elle être entièrement créditée lorsqu'une seule qualité
   progresse, ou seulement son coût effectif ?
2. Plusieurs marqueurs physiologiques peuvent-ils progresser dans un même tour ?
3. Un gain `EF +1` bloqué par `EF < Seuil` est-il perdu, différé, ou converti ?
4. Quel effet de règle relie exactement `ECO -1` au coût Race Engine V2, et un
   coût nul est-il admissible ?
5. Les fixtures d'intensité/durée AS42 et AS10 doivent-elles être remplacées par
   des valeurs canoniques avant toute comparaison d'équilibrage ?
