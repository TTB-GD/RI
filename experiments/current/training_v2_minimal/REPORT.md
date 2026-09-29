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

La question de première passe sur le crédit de toute l'énergie Q et celle sur la
progression de plusieurs marqueurs sont traitées expérimentalement par A2/B2
ci-dessous. Les autres arbitrages ouverts sont consolidés dans la liste finale,
limitée à cinq questions.

---

# Deuxième passe ciblée — A2 / B2

## FACT

- **A2** réutilise exactement les 1 296 tirages et partitions physiques de A,
  mais compose réellement les programmes `aucun`, `Seuil`, `VMA` et
  `Seuil+VMA`. Le double programme exige `E_Q >= coût Seuil + coût VMA`, soit
  8 à la baseline (3 + 5). La mesure A « accès simultané » à 77,623 % était une
  **co-accessibilité alternative**, pas la finançabilité des deux séances; A2 la
  remplace pour toute conclusion sur la multi-qualité. Les reliquats moyens A2
  pondèrent chaque occurrence lancer × partition physique × programme.
- **B2** exécute 100 seeds partagées (`0..99`) × 2 politiques × 2 variantes ×
  16 tours = **400 campagnes / 6 400 tours**. `Q_FULL` conserve le contrôle de
  la PR #10 : dès qu'au moins une qualité réussit, tout E_Q non perdu par bust
  est crédité à progression Q. `Q_SPENT_SPEC` crédite seulement les coûts des
  qualités réussies; le reliquat jamais affecté va à SPEC. Une énergie affectée
  à une qualité busted est perdue, sans crédit Q ni SPEC. Les qualités sont
  résolues dans l'ordre déterministe Seuil puis VMA; un bust n'annule pas la
  seconde, car B2 ne reproduit pas la résolution post-bust CURRENT.
- Les seuils EF/Q, D99 bonus-only et conventions de pool de la première passe
  sont inchangés. SPEC reste un compteur sans effet Vitesse/Économie.

## RESULTS

### A2 — vraie composition multi-qualités

| Mesure par lancer | Résultat |
|---|---:|
| Au moins une qualité | 99,614 % |
| Seuil | 99,614 % |
| VMA | 77,623 % |
| Seuil + VMA réellement financés dans une partition | **5,787 %** |
| Choix entre ≥2 programmes qualitatifs distincts | 77,623 % |
| Programmes qualitatifs distincts, moyenne | 1,830 |
| Reliquat moyen après Seuil | 1,935 |
| Reliquat moyen après VMA | 1,007 |
| Reliquat moyen après Seuil + VMA | 1,125 |

Exemples représentatifs (`EF/Q : programme, consommé, reliquat`) :

- `1,1,1,1` : aucun programme qualitatif;
- `4,3,2` : `6/3 : Seuil, 3, 0` et `5/4 : Seuil, 3, 1`;
- `5,5,2,2` : jusqu'à `7/7 : Seuil, 3, 4` ou `VMA, 5, 2`, sans double;
- `6,3,3,3` : `9/6 : Seuil, 3, 3` ou `VMA, 5, 1`;
- `6,5,4` : programmes simples seulement, reliquat maximal 3;
- `6,6,5,5` : `12/10 : Seuil+VMA, 8, 2` ou `11/11 : ..., 8, 3`;
- `6,6,6,6` : `12/12 : Seuil+VMA, 8, 4`.

### B2 — Q_FULL vs Q_SPENT_SPEC

Notation : `moyenne [P10 ; médiane ; P90]` sur 100 campagnes.

| Mesure | BAL Q_FULL | BAL Q_SPENT_SPEC | QUALITY Q_FULL | QUALITY Q_SPENT_SPEC |
|---|---:|---:|---:|---:|
| EF final | 11,99 [12;12;12] | 11,99 [12;12;12] | 11,78 [11;12;12] | 11,76 [11;12;12] |
| Seuil final | 15,80 [15;16;16,1] | 15,83 [15;16;17] | 14,63 [13,9;14;16] | 14,65 [13,9;15;16] |
| VMA final | 18,96 [18;19;20] | 18,99 [18;19;20] | 19,42 [18;19;21] | 19,37 [18;19;20] |
| progression EF | 188,84 [175;187;208] | 187,90 [174;187;206,1] | 175,98 [159;176;191,1] | 175,44 [159;175;190,2] |
| progression Q | 88,43 [75,9;89;101] | 86,13 [74,9;86,5;96,1] | 93,38 [77,9;94,5;107,1] | 89,99 [74,9;90;104,1] |
| progression SPEC | 0 [0;0;0] | 5,55 [3;5;8,1] | 0 [0;0;0] | 3,42 [1;3;6] |
| dés finaux | 6 [6;6;6] | 6 [6;6;6] | 6 [6;6;6] | 6 [6;6;6] |
| upgrades | 3,15 [3;3;4] | 3,02 [3;3;3] | 3,32 [3;3;4] | 3,23 [3;3;4] |
| tours à 0 qualité réussie | 2,23 [1;2;4] | 2,22 [1;2;4] | 1,79 [0;2;3] | 1,79 [0;2;3,1] |
| tours à 1 qualité réussie | 10,78 [8;11;13] | 10,74 [8;11;13] | 12,37 [10;13;15] | 12,40 [10;13;15] |
| tours à 2 qualités réussies | 2,99 [1;3;5] | 3,04 [1,9;3;5] | 1,84 [1;2;3] | 1,81 [0,9;2;3] |
| tentatives risquées | 4,89 [3;5;7] | 4,90 [3;5;7] | 6,99 [5;7;9] | 7,10 [5;7;9] |
| busts | 1,12 [0;1;3] | 1,02 [0;1;2] | 1,96 [0,9;2;4] | 1,99 [0;2;4] |
| énergie Q disponible | 99,95 [87;100,5;112] | 99,83 [88,9;100;109,2] | 111,33 [97,9;111;126,1] | 111,21 [98,9;110;125,1] |
| énergie Q consommée | 85,56 [73;86;98] | 86,13 [74,9;86,5;96,1] | 90,30 [76;90,5;104] | 89,99 [74,9;90;104,1] |
| énergie Q → SPEC | 0 [0;0;0] | 5,55 [3;5;8,1] | 0 [0;0;0] | 3,42 [1;3;6] |
| énergie Q perdue par bust | 8,94 [0;8;21,1] | 8,15 [0;8;19,1] | 17,63 [5,4;16;33,1] | 17,80 [0;17,5;33] |
| part SPEC de Q | 0 % | 5,539 % [2,752;5,465;8,421] | 0 % | 3,056 % [0,999;2,885;5,273] |

| Événement | BAL Q_FULL | BAL Q_SPENT_SPEC | QUALITY Q_FULL | QUALITY Q_SPENT_SPEC |
|---|---:|---:|---:|---:|
| 5e dé, tour médian (% à T16) | 5 (100 %) | 5 (100 %) | 5 (100 %) | 5 (100 %) |
| 6e dé, tour médian (% à T16) | 11 (100 %) | 11 (100 %) | 11 (100 %) | 11 (100 %) |
| Upgrade 1 | 5 (100 %) | 5 (100 %) | 4 (100 %) | 4 (100 %) |
| Upgrade 2 | 8 (100 %) | 8 (100 %) | 7 (100 %) | 8 (100 %) |
| Upgrade 3 | 13 (100 %) | 13 (99 %) | 12 (100 %) | 13 (100 %) |
| Upgrade 4 | 16 (15 %) | 16 (3 %) | 16 (32 %) | 16 (23 %) |

Réponses prioritaires :

1. **Ralentissement des upgrades :** Q_SPENT réduit la moyenne de 3,15 à 3,02
   pour P_BALANCED et de 3,32 à 3,23 pour P_QUALITY. L'accès au quatrième
   upgrade à T16 baisse respectivement de 15 % à 3 % (−12 points) et de 32 % à
   23 % (−9 points); les deuxième/troisième upgrades de P_QUALITY reculent
   chacun d'un tour médian.
2. **Deuxième d6 :** oui, il reste universel dans cet échantillon : 100 % à T16
   dans les quatre cellules, tour médian 11.
3. **Part naturelle vers SPEC :** 5,539 % de Q en moyenne pour P_BALANCED et
   3,056 % pour P_QUALITY sous Q_SPENT_SPEC.
4. **Doubles qualités :** elles sont occasionnelles : 3,04 tours sur 16
   (19,0 %) pour P_BALANCED et 1,81 sur 16 (11,3 %) pour P_QUALITY dans la
   variante test. Il s'agit de doubles réussites, après bust éventuel.
5. **Différenciation :** elle subsiste sous Q_SPENT_SPEC. P_BALANCED finit à
   Seuil 15,83 / VMA 18,99 avec 4,90 risques; P_QUALITY à Seuil 14,65 / VMA
   19,37 avec 7,10 risques. L'écart VMA est modeste, mais les répartitions Seuil,
   risque et reliquat SPEC restent différentes.

## OBSERVATIONS

- La vraie double qualité initiale (5,787 % des lancers) est bien plus rare que
  la co-accessibilité alternative annoncée dans A (77,623 %).
- Q_SPENT ralentit surtout le quatrième upgrade; il ne retarde ni le cinquième
  ni le sixième dé dans ces trajectoires, car ceux-ci dépendent de la piste EF.
- Le reliquat SPEC mesuré reste petit devant Q totale et est plus élevé chez
  P_BALANCED, tandis que P_QUALITY consomme davantage de Q et perd davantage au
  bust.
- Les doubles réussites restent minoritaires sous les deux politiques, sans être
  exceptionnelles.

## INTERPRETATIONS

- Supprimer le crédit Q gratuit corrige une partie de l'accélération observée en
  B, mais ne suffit pas, sur 16 tours, à rendre les premiers upgrades ou les dés
  supplémentaires rares.
- Le compteur SPEC reçoit un flux mesurable sans détourner de coûts réellement
  affectés aux qualités. Son volume dépend de la politique et ne constitue pas
  encore une cadence de piste validée.
- Les deux sondes conservent des signatures distinctes après la correction,
  surtout sur la répartition Seuil/VMA et l'exposition au risque; cela ne prouve
  pas qu'elles représentent des stratégies humaines ou équilibrées.

## LIMITS

- Les conventions de lancer, pool, gain EF bloqué et upgrades restent celles du
  harnais initial; B2 ne les revalide pas.
- `Q_FULL` est un contrôle technique : après au moins une réussite il crédite le
  compartiment moins les coûts busted. Il n'est ni une nouvelle règle CURRENT,
  ni une proposition de design.
- Un bust n'arrête pas la qualité suivante. Le reliquat jamais affecté reste
  SPEC; le coût affecté au bust est perdu. Aucune redistribution post-bust n'est
  simulée.
- Les fréquences longitudinales reflètent ces deux politiques déterministes et
  les trajectoires divergent après leurs gains/RNG; elles ne décrivent pas un
  joueur optimal ou humain.
- Les moyennes de reliquat A2 pondèrent les partitions physiques et peuvent donc
  compter plusieurs fois un même couple énergétique produit par des dés égaux.

## DESIGN QUESTIONS

1. Un programme multi-qualités doit-il continuer après le bust de sa première
   qualité, ou s'arrêter ?
2. Le reliquat SPEC doit-il être automatique, optionnel, ou exiger une allocation
   Q explicite distincte ?
3. Les futurs paliers SPEC doivent-ils interpréter un flux moyen de 3–6 % de Q
   comme cadence cible, ou faut-il d'abord définir leur effet ?
4. Le quatrième upgrade doit-il être normalement accessible à T16, ou rester un
   résultat minoritaire ?
5. Les politiques doivent-elles pouvoir renoncer à une qualité finançable pour
   préserver davantage de SPEC ?
## DESIGN QUESTIONS

1. Une énergie Q doit-elle être entièrement créditée lorsqu'une seule qualité
   progresse, ou seulement son coût effectif ?
2. Plusieurs marqueurs physiologiques peuvent-ils progresser dans un même tour ?
3. Un gain `EF +1` bloqué par `EF < Seuil` est-il perdu, différé, ou converti ?
4. Quel effet de règle relie exactement `ECO -1` au coût Race Engine V2, et un
   coût nul est-il admissible ?
5. Les fixtures d'intensité/durée AS42 et AS10 doivent-elles être remplacées par
   des valeurs canoniques avant toute comparaison d'équilibrage ?
