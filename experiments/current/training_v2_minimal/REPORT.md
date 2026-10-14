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
  Chaque politique choisit au plus une qualité (Seuil ou VMA) par tour,
  avec tie-breaks déterministes. EF peut aussi progresser passivement lors du
  franchissement de ses paliers : la limite ne porte pas sur tous les marqueurs.
  Toute l'énergie des compartiments alimente les compteurs; Q n'est créditée que si la qualité choisie réussit. Le test de bust
  local reprend la forme du test CURRENT : `k = coût - max(lancer final)`,
  lancer du meilleur dé du pool, bust sur face brute `<= k`. Le coût de qualité
  et la frontière sûre restent ceux du harnais, pas le catalogue/RPE Max CURRENT.
  Les gains s'appliquent en fin de tour. Aux paliers EF sans dé, `EF +1` est provisoire et seulement
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

Ces taux décrivent le lancer et les partitions du harnais, sans relance ni
décision de joueur, avec D99 bonus-only et sans son plafond de qualités.
Ils ne mesurent pas les possibilités ni les décisions du Training CURRENT.

| Mesure | Résultat |
|---|---:|
| Lancers avec ≥1 partition non triviale | 100,000 % |
| Partitions physiques légales, moyenne | 3,946 |
| Plusieurs partitions pertinentes | 100,000 % |
| Plusieurs programmes énergie/accès distincts | 100,000 % |
| Accès au premier palier EF (10) | 55,633 % |
| Accès Seuil | 99,614 % |
| Accès VMA | 77,623 % |
| Co-accessibilité alternative Seuil/VMA (ancien « accès simultané ») | 77,623 % |
| Au moins une qualité sûre | 98,765 % |
| Au moins une qualité risquée | 4,398 % |

**Critère opérationnel : `CHOIX REEL`.** Ce label désigne plusieurs programmes
énergie/accès dans ≥50 % des lancers, sans mesurer leur intérêt stratégique,
leur non-dominance ou les décisions d’un joueur. Dans les exemples, `Seuil/VMA`
désigne deux options alternatives, jamais leur financement conjoint.
Exemples compacts (lancer final → couples EF/Q) :

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

Sous ces politiques et paramètres locaux, les 200 runs de chaque politique
finissent à six dés; médiane d'obtention au
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
l'AS fixe de contexte; à offset identique, le gain dû à ses quatre points Vitesse
reste +4. À AS42, le plancher écrase la différence de coût entre BALANCED et
FULL_ECO : BALANCED fournit deux Production de plus pour le même coût nul,
aux trois offsets, donc domine localement FULL_ECO sur ces deux métriques.
Les 20/8/16 unités « économisées par ECO » comparent chaque profil à lui-même
sans son bonus ECO, à Production inchangée; ce ne sont pas les économies par
rapport à FULL_SPEED. À AS10, les trois profils à AS restent distincts : davantage
de Production contre davantage de coût répété. Ces fixtures ne représentent
ni la courbe physiologique native ni une mécanique SPEC intégrée à Race V2.

## OBSERVATIONS

- La partition n'est pas structurellement unique dans ce modèle : tous les
  tirages ont plusieurs programmes distincts, même si une part des différences
  ne change pas l'ensemble de qualités accessible.
- Seuil est presque toujours finançable dès la baseline expérimentale; VMA
  l'est dans plus de trois quarts des tirages, comme option alternative.
  4,398 % des lancers exposent au moins une option risquée dans A : il ne
  s'agit ni d'un taux de tentative ni d'un taux de bust sous politique.
- Les trois sondes font progresser tous les marqueurs et obtiennent les deux dés
  en 16 tours. P_BALANCED et P_QUALITY obtiennent presque toujours les quatre
  upgrades; P_QUALITY sépare nettement VMA mais tente et subit plus de risque.
- C mesure des bénéfices de nature différente (Production instantanée contre
  coût répété), mais le plancher zéro masque l'économie marginale au contexte
  bas et les paliers Curve B amplifient les écarts à AS10. Le coût terminal
  reste toutefois constant à partir de Production 27; la convexité globale
  ne peut être supposée.

## INTERPRETATIONS

- La multiplicité combinatoire est établie. L'accès Seuil quasi universel
  suggère une question d'allocation et de cible plutôt que d'ouverture de Seuil.
  L'intérêt stratégique, les options dominées et la lisibilité pour un joueur
  restent non démontrés : **OPEN — REQUIRES NEW EXPERIMENT** après définition
  des critères C1/C2, sans expérience supplémentaire dans cet audit.
- B établit l'absence de blocage dans ses 600 campagnes et un rythme soutenu
  sous ses paliers et politiques techniques. « Accélération forte » reste une
  interprétation sans cadence cible ni comparaison au Training CURRENT.
  EF reçoit toute l'énergie de son compartiment; les dés arrivent aux paliers
  EF 35/100, les upgrades aux paliers Q 15/35/65/100. Ces conventions, la priorité
  de chaque politique et le crédit Q intégral contribuent aux résultats, sans
  isoler leurs effets. La différenciation des marqueurs et risques mesurée en B
  ne démontre ni des builds humains ni une profondeur ludique.
- À AS10/offset zéro, les profils ne se dominent pas sur Production/coût;
  à AS42, BALANCED domine localement FULL_ECO (voir C). La valeur stratégique
  d'une Production supplémentaire face à une économie de Réserve dépend d'une
  course et d'un objectif absents de C. Même la non-dominance à AS10 ne démontre
  pas un compromis équilibré. Le contexte et les répétitions sont des fixtures,
  sans preuve d'équilibrage physiologique dans Race V2 intégré.

## LIMITS

- Le lancer local n'évalue ni relance ni choix du joueur; il lance chaque dé du
  pool une fois et utilise D99 seulement pour la réserve. `D99_OFF` est testé en
  boundary test mais aucune seconde campagne n'est exécutée.
- Les partitions physiques dupliquent parfois le même programme énergétique
  quand des faces sont égales; le rapport donne aussi les programmes distincts.
- B limite le choix à une qualité par tour, avec gains EF passifs, crédite
  toute l'énergie de compartiment, ne reporte pas un gain EF bloqué, et ne modélise ni fatigue,
  ni catalogue, ni joueur humain. Les politiques ne sont pas optimales.
- Les valeurs AS42/AS10, répétitions et effet linéaire ECO de C sont des fixtures
  abstraites locales. Curve B est réutilisée, mais son domaine terminal agrège
  toute Production ≥27 et le plancher de coût zéro est une convention du harnais.
- Les trajectoires B incluent les effets de leurs choix; elles ne sont donc pas
  des contre-factuels appariés tour par tour après divergence des pools/RNG.

A2/B2 teste la composition de deux qualités et une variante de crédit Q;
ces résultats précisent les questions initiales sans décider de leur adoption.
La traçabilité finale conserve les cinq questions de chaque passe dans un seul
registre; elle distingue réponse expérimentale locale et arbitrage de design.

---

# Deuxième passe ciblée — A2 / B2

## FACT

- **A2** réutilise exactement les 1 296 tirages et partitions physiques de A,
  mais compose réellement les programmes `aucun`, `Seuil`, `VMA` et
  `Seuil+VMA`. Le double programme exige `E_Q >= coût Seuil + coût VMA`, soit
  8 à la baseline (3 + 5). La mesure A « accès simultané » à 77,623 % était une
  **co-accessibilité alternative**, pas la finançabilité des deux séances; A2 la
  remplace pour toute conclusion sur la multi-qualité. Les reliquats moyens A2
  pondèrent chaque occurrence lancer × partition physique × programme finançable,
  séparément pour Seuil, VMA et Seuil+VMA. Ce sont des moyennes conditionnelles,
  pas des reliquats moyens par lancer ni sous une politique de choix; la moyenne
  de 1,830 compte uniquement les programmes qualitatifs, sans « aucun ».
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

Notation : `moyenne [P10 ; médiane ; P90]` sur 100 campagnes par cellule.
Les médianes de dates d'événements ci-dessous portent uniquement sur les
campagnes ayant atteint l'événement; les taux à T16 portent sur les 100 campagnes.
`q_consumed` mesure seulement le coût des qualités réussies, pas l'énergie
busted. La part SPEC est la moyenne des ratios individuels `q_to_spec/q_available`,
pas le ratio des moyennes. SPEC est un compteur sans effet de course, avec
résolution de bust non-CURRENT; les doubles réussites et flux restent locaux.

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
3. **Part dirigée vers SPEC par la convention locale :** 5,539 % de Q en
   moyenne pour P_BALANCED et 3,056 % pour P_QUALITY sous Q_SPENT_SPEC.
4. **Doubles qualités :** elles sont occasionnelles : 3,04 tours sur 16
   (19,0 %) pour P_BALANCED et 1,81 sur 16 (11,3 %) pour P_QUALITY dans la
   variante test. Il s'agit de doubles réussites : aucune des deux qualités
   ne bust sur ces tours. Les autres tours peuvent contenir des busts, dont la
   résolution non-CURRENT affecte aussi les trajectoires ultérieures.
5. **Différenciation :** elle subsiste sous Q_SPENT_SPEC. P_BALANCED finit à
   Seuil 15,83 / VMA 18,99 avec 4,90 risques; P_QUALITY à Seuil 14,65 / VMA
   19,37 avec 7,10 risques. L'écart VMA est modeste, mais les répartitions Seuil,
   risque et reliquat SPEC restent différentes.

## OBSERVATIONS

- La vraie double qualité initiale (5,787 % des lancers) est bien plus rare que
  la co-accessibilité alternative annoncée dans A (77,623 %).
- Sous Q_SPENT_SPEC, l'accès au quatrième upgrade à T16 baisse de 12 et 9
  points selon la politique. Les médianes des dates des cinquième/sixième dés
  (5/11) et leurs taux à T16 (100 %) restent identiques. Cela n'établit pas
  l'identité des dates individuelles ou des distributions. Les dés dépendent
  directement de la piste EF, mais les gains Q peuvent modifier pool, choix et RNG.
- Le reliquat SPEC mesuré reste petit devant Q totale et est plus élevé chez
  P_BALANCED, tandis que P_QUALITY consomme davantage de Q et perd davantage au
  bust.
- Les doubles réussites restent minoritaires sous les deux politiques, sans être
  exceptionnelles.

## INTERPRETATIONS

- Dans B2, passer de Q_FULL à Q_SPENT_SPEC réduit les upgrades moyens et
  l'accès au quatrième upgrade, sous les deux politiques. Il ne s'agit pas d'un
  effet causal pur à trajectoire identique : les seeds sont partagées, mais les
  états, choix et consommations RNG peuvent ensuite diverger. B et B2 diffèrent
  aussi par composition, sélection et échantillon (200/100 seeds); la baisse
  entre B et B2 ne peut donc être attribuée au seul crédit Q. Les premiers
  upgrades et les dés restent fréquents dans B2, sans validation de cadence cible.
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
  simulée. CURRENT annule les qualités risquées ultérieures et conserve les
  séances sûres : une question de poursuite ne doit pas rouvrir implicitement
  cette règle. Les fréquences B2 ne permettent pas d'en évaluer un remplacement.
- Les fréquences longitudinales reflètent ces deux politiques déterministes et
  les trajectoires peuvent diverger après leurs gains/RNG; elles ne décrivent
  pas un joueur optimal ou humain. Aucun effet intrinsèque du crédit Q, isolé
  du retour pool/choix/RNG, n'est mesuré. Le nom P_QUALITY couvre une priorité
  VMA dans B, puis nombre de qualités/VMA dans B2; les noms identiques ne
  rendent pas les deux passes expérimentalement équivalentes.
- Les moyennes de reliquat A2 pondèrent les partitions physiques et peuvent donc
  compter plusieurs fois un même couple énergétique produit par des dés égaux.

## TRAÇABILITÉ DES QUESTIONS DE DESIGN

Les deux anciennes listes finales avaient chacune cinq questions : celles de
la première passe A/B/C avaient été placées après celles d'A2/B2. Le registre
ci-dessous conserve leur origine et leur contenu, sans en faire deux listes
finales équivalentes. « Précisée expérimentalement » ne signifie pas « décidée ».
Toutes les questions d'adoption concernent une éventuelle cible Training V2,
sous réserve de C/D; aucune règle CURRENT n'est changée.

| ID / origine | Question conservée | Statut après audit |
|---|---|---|
| Q1 — A/B/C 1 | Créditer toute Q après une réussite, ou seulement son coût ? | **Précisée par B2** : comparaison Q_FULL/Q_SPENT_SPEC mesurée sous politiques; choix de crédit encore OPEN si V2 retenu. |
| Q2 — A/B/C 2 | Plusieurs marqueurs peuvent-ils progresser dans un tour ? | **Précisée/remplacée** : B permet déjà qualité + EF passive; A2/B2 démontre localement le financement/la réussite de deux qualités. L'autorisation de design reste OPEN si V2 retenu. |
| Q3 — A/B/C 3 | Gain EF +1 bloqué : perdu, différé ou converti ? | **OPEN si V2 retenu** : perte immédiate imposée par le harnais; aucune alternative comparée. |
| Q4 — A/B/C 4 | Quel lien entre ECO −1 et coût Race, et coût nul admissible ? | **OPEN** : convention Curve B/plancher zéro testée seulement dans C; SPEC absent du chemin intégré. |
| Q5 — A/B/C 5 | Remplacer les fixtures AS42/AS10 par des valeurs canoniques avant comparaison d'équilibrage ? | **OPEN** : fixtures non canoniques, insuffisantes pour un équilibrage. Définir d'abord effet et contexte de course. |
| Q6 — A2/B2 1 | Poursuivre un programme après bust de sa première qualité, ou s'arrêter ? | **Précisée, OPEN pour V2 uniquement** : B2 poursuit; CURRENT conserve les sûres et annule les risques ultérieurs. Aucun résultat B2 ne tranche une modification de CURRENT. |
| Q7 — A2/B2 2 | Reliquat SPEC automatique, optionnel ou alloué explicitement ? | **OPEN si V2 retenu** : automatisme imposé, non comparé. |
| Q8 — A2/B2 3 | Flux moyen de 3–6 % de Q comme cadence SPEC cible, ou définir d'abord son effet ? | **Précisée par B2, OPEN** : moyenne de ratios sous deux politiques, pas cadence cible démontrée; aucun effet SPEC simulé. |
| Q9 — A2/B2 4 | Quatrième upgrade normalement accessible à T16 ou minoritaire ? | **OPEN** : taux de 3/15/23/32 % dans B2, sans horizon/cadence cible validés. |
| Q10 — A2/B2 5 | Renoncer à une qualité finançable pour préserver SPEC ? | **OPEN si V2 retenu** : programme vide disponible, mais aucune politique orientée SPEC ni valeur de course testée. |

Réponses expérimentales acquises : financement double à la baseline (A2),
répartition Q réussie/reliquat/bust et fréquence des upgrades sous politiques
(B2), arithmétique des fixtures SPEC (C). Elles précisent Q1/Q2/Q8 sans résoudre
leur choix de design. L'intérêt des décisions humaines, un effet de crédit Q
isolé des trajectoires, et la valeur d'une boucle Training → Race restent
**OPEN — REQUIRES NEW EXPERIMENT**, après arbitrage de périmètre; aucune de ces
expériences n'est réalisée ici.

## MATRICE D'AUDIT — ACTION A2 DE LA ROADMAP

Audit documentaire du 2026-10-14, sur la baseline A1 intégrée par la PR #21
(`5ea9254360619b5b188c813ae789bf3ea585cc86`). Ne pas confondre cette action A2
avec le bloc combinatoire A2. Le JSON est valide, A/A2/B/B2/C sont présents et
le README porte cinq statuts `REPRODUCIBLE`; la reproductibilité A1 est reprise,
sans relancer ses campagnes. Les statuts ci-dessous évaluent les formulations
avant les corrections ciblées de cet audit; les lignes marquées « Extension »
classent des généralisations non démontrées, sans les attribuer au texte initial.
Les chemins JSON sont relatifs à
`results.json`; les fonctions citées sont dans `harness.py`.

| ID | Affirmation | Source | Évaluation | Action |
|---|---|---|---|---|
| A-01 | Tous les lancers offrent plusieurs programmes énergie/accès; moyenne 3,946 partitions physiques | `A.multiple_distinct_programs_pct`, `mean_legal_partitions`; `legal_partitions`, `experiment_a` | VALID | Conserver; les partitions physiques avec faces égales peuvent dupliquer un programme. |
| A-02 | `CHOIX REEL` établit un choix intéressant | `A.criterion`; seuil basé seulement sur la multiplicité | QUALIFY | Limiter au label combinatoire; intérêt stratégique UNSUPPORTED par A. |
| A-03 | Seuil 99,614 %, VMA 77,623 %, options risquées 4,398 % | `A.*_access_pct`; baseline 6/8/10, coûts 3/5 | VALID | Conserver avec condition baseline, accès alternatif et absence de taux de tentative/bust. |
| A-04 | Extension : généraliser A au Training CURRENT | `resolve_roll`, `has_reserve_bonus`; GDD §§2–4 | UNSUPPORTED | Rendre visible l'absence du plafond D99, des relances et des choix humains; ne pas généraliser. |
| A2-01 | « Accès simultané » à 77,623 % | `A.simultaneous_access_pct` vs `A2.seuil_plus_vma_same_partition_pct` 5,787 | CORRECT | Renommer la ligne A en co-accessibilité alternative et expliciter les exemples; A2 seul établit le financement conjoint. |
| A2-02 | Reliquats 1,935/1,007/1,125 | `A2.mean_remainder_after_program`; `experiment_a2` | QUALIFY | Conserver les valeurs; préciser moyenne conditionnelle pondérée par occurrences physiques, sans politique. |
| B-01 | Une seule progression physiologique par tour | `simulate`, `_apply_milestones` | CORRECT | Une seule qualité choisie, plus gains EF passifs possibles; corriger FACT et LIMITS. |
| B-02 | Le test local reprend exactement CURRENT | `simulate`; GDD §4, `session_risk.py` | QUALIFY | Distinguer forme seuil/face brute du coût et de la frontière sûre locaux. |
| B-03 | Six dés et trois marqueurs progressés dans tous les runs; upgrades 13/94/81,5 % | `B.policies.*.timing_diagnostics`, `final_pool_composition` | VALID | Conserver les 600 campagnes et les observations, sans généralisation au joueur. |
| B-04 | Accélération forte du futur Training | Paliers EF 35/100, Q 15/35/65/100; `B.policies` | QUALIFY | Rythme sous conventions et politiques; aucune cadence cible/comparaison CURRENT. |
| B-05 | P_QUALITY se différencie en VMA et risque | `B.policies.*.VMA`, `risky_attempts`, `busts`; `_choose_partition` | VALID | Conserver la différence observée; ne pas l'assimiler à des builds équilibrés. |
| B2-01 | Quatrième upgrade : 15→3 % et 32→23 % | `B2.cells.*.upgrade_timing.4` | VALID | Conserver −12/−9 points; effet observé sous politique, pas causalité à trajectoire identique. |
| B2-02 | Les dés ne sont jamais retardés | `B2.cells.*.fifth_die_timing`, `sixth_die_timing`; `_apply_milestones` | CORRECT | Seulement médianes 5/11 et taux à T16 identiques; distributions/dates individuelles non établies. |
| B2-03 | Part « naturelle » SPEC 5,539/3,056 % | `spec_share_pct`, `q_to_spec`, `experiment_b2` | QUALIFY | Allocation automatique expérimentale; moyenne de ratios, pas cible ni effet SPEC. |
| B2-04 | Doubles réussites 19,0/11,3 % « après bust éventuel » | `quality_turns_2`; `simulate_b2` | CORRECT | Deux réussites impliquent zéro bust sur ce tour; préciser les effets longitudinaux du traitement non-CURRENT. |
| B2-05 | B2 corrige l'accélération de B grâce au seul crédit Q | `simulate` vs `simulate_b2`, `_choose_partition` vs `_choose_b2_program`; échantillons 200/100 | UNSUPPORTED | Comparer Q_FULL/Q_SPENT_SPEC au sein de B2; B→B2 modifie aussi composition et politiques. |
| B2-06 | Différenciation BAL/QUALITY : Seuil, risque, SPEC | `B2.cells.*__Q_SPENT_SPEC` | VALID | Conserver les écarts descriptifs; feedback/RNG, bust et absence d'effet de course limitent l'inférence. |
| C-01 | Production/coûts/économies répétées du tableau | `C.rows.*`, `experiment_c`, Curve B | VALID | Conserver; économie versus même profil sans ECO, pas versus FULL_SPEED. |
| C-02 | Aucune dominance Vitesse/Économie dans les fixtures | `C.rows` : AS42 BALANCED 20/0 vs FULL_ECO 18/0 | CORRECT | Reconnaître la dominance locale de BALANCED à AS42; non-dominance à AS10 ≠ équilibre stratégique. |
| C-03 | Extension : fixtures SPEC prouvent l'équilibre physiologique Race V2 | `C.curve`; GDD §§7.1–7.3; `CURRENT_STATE.md` | UNSUPPORTED | SPEC OPEN, Curve B legacy et plancher local zéro; aucune preuve sur la courbe native. |
| T-01 | Deux listes finales de cinq questions équivalentes | Anciennes sections finales, première et seconde passes | CORRECT | Registre Q1–Q10 avec origine et statut; conserver les questions, sans arbitrage. |

Vérification factuelle : **481 valeurs numériques des tableaux** comparées aux
champs JSON (arrondis publiés), diagnostics B et arithmétique B2 examinés;
fixtures C vérifiées analytiquement. Aucun chiffre de tableau ne nécessite de
remplacement. Code, paramètres, JSON, tests, GDD et roadmap sont inchangés.
Les inférences corrigées ne retirent pas la reproductibilité des résultats.

## SYNTHÈSE DE VALIDITÉ — UTILISATION FUTURE

**Ce que Training V2 démontre.** Dans le harnais : multiplicité de programmes
énergie/accès sur les 1 296 lancers, accès alternatif ≠ financement conjoint
(77,623 % contre 5,787 %), progression sous les politiques et paliers spécifiés,
baisse observée de l'accès au quatrième upgrade sous Q_SPENT_SPEC, et calcul
local des fixtures SPEC avec saturation du plancher. Les deux passes restent
distinctes; ces résultats ne sont pas des propriétés générales de Training.

**Ce que Training V2 suggère.** L'allocation plutôt que l'ouverture de Seuil
pourrait porter les choix; le crédit Q et les paliers pourraient contribuer au
rythme; la saturation ECO et les signatures des politiques donnent des sujets
à examiner après définition de critères. Leurs effets isolés, leur intérêt
humain et leur utilité en course restent à valider.

**Ce que Training V2 ne démontre pas.** Sa supériorité sur Training CURRENT,
sa profondeur stratégique pour un joueur humain, son équilibre final, la
pertinence définitive de SPEC ou la qualité d'une boucle Training → Race
complète. Les seeds partagées n'impliquent pas un contrefactuel à trajectoire
identique; les deux métriques de C ne suffisent pas à prouver un compromis
équilibré, et ses résultats ne valident pas Race V2 intégré.

**Ce qui reste utile pour C/D.**

1. **C1/C2 :** définir l'intérêt, la lisibilité et les conséquences recherchées
   d'une décision d'allocation; distinguer ces critères du nombre d'options.
2. **C2/D1 :** définir horizon et cadence de progression avant de comparer les
   rythmes; les écarts de crédit Q sont des observations conditionnelles, pas
   une preuve de supériorité ni une recommandation A/B/C.
3. **C1/C2/D1 :** préciser le rôle du risque et l'effet de SPEC en course avant
   toute valeur cible; conserver la distinction entre bust CURRENT, compteurs
   expérimentaux et coûts physiologiques intégrés.
