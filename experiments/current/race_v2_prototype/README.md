# Race V2 — prototype de résolution d'un secteur

**PROTOTYPE / EXPERIMENTAL.** Ce module implémente les règles de résolution
d'un secteur consolidées dans docs/game-design/RACE_V2_DESIGN.md. Il ne
remplace pas encore le runner historique ni ne fournit l'orchestration complète.

## Entrées

- table physiologique entière énergie → vitesse, fournie explicitement ;
- énergie issue du sous-ensemble de dés choisi ;
- bonus de groupe (0 ou +1) ;
- difficulté signée du terrain ;
- AS du scénario ;
- crédit initial S0, forme cumulée F et consommation antérieure C.

La table est injectée : aucune interpolation, extrapolation ou valeur
physiologique arbitraire n'est construite par ce prototype.

## Ordre implémenté

1. Plafonner la dépense réelle à VMA.
2. Calculer le bilan de soutenabilité entrant à partir de S0 + F - C.
3. Si la dépense est nulle, produire zéro vitesse.
4. Sinon, calculer E_conversion = E_dépensée + B_groupe - D_terrain, plafonnée à VMA.
5. Appliquer le décalage horizontal expérimental de la courbe par lecture de la
   table à E_conversion - D, avec plancher EF.
6. Lire directement la vitesse entière dans la table.
7. Calculer la consommation de soutenabilité à partir de la dépense réelle et
   de l'AS ; cette consommation ne modifie que le secteur suivant.

Le ratio de dégradation d'une graduation par point est un paramètre expérimental
conservé comme valeur de départ, pas une calibration validée.

## Tests

    python -m unittest experiments.current.race_v2_prototype.test_sector -v

## Non couvert dans cet incrément

- génération des cartes et calendrier de révélation ;
- résolution multi-joueurs et constitution des groupes ;
- lancer/relance/sélection des dés ;
- orchestration des 7 / 10 / 13 / 16 secteurs ;
- construction de la table physiologique depuis le Training ;
- mapping Training → S0.
