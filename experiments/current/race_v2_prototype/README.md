# Race V2 — prototype multi-secteur

**PROTOTYPE / EXPERIMENTAL.** Cette couche orchestre une course complète à
plusieurs joueurs en réutilisant le résolveur déterministe de `sector.py`.

## Inclus

- courses 5 km / 10 km / semi / marathon et calendriers de révélation ;
- tirage 3d6 de forme du jour et recette de catégories ;
- paquets de cartes par catégorie, tirage sans remise et ordre mélangé ;
- forme cumulée et soutenabilité suivies par joueur ;
- scores entiers et classement cumulatif ;
- groupes fondés sur les écarts successifs, lièvre local et aspiration +1 ;
- révélation finale des cartes restantes après le dernier secteur uniquement.

## Déroulement des dés

Le composant `dice.py` reprend les tailles de dés du Training (`6`, `8`,
`10`, `12`). Le composant `dice_session.py` le raccorde maintenant à
`RaceState` en deux phases :

1. `prepare_sector()` révèle d'abord les cartes prévues au début du secteur,
   puis lance l'intégralité du pool de chaque joueur ;
2. `resolve_sector(choices)` applique les relances individuelles, puis la
   sélection libre du sous-ensemble dépensé, et transmet les sommes au
   résolveur du secteur.

Chaque joueur dispose d'un capital global de relance, non renouvelé entre les
secteurs. Chaque relance consomme une unité et remplace le résultat précédent.
Le même dé peut être relancé plusieurs fois si le capital le permet. Les dés
non sélectionnés ne sont pas conservés : tout le pool sera relancé au secteur
suivant. La sélection vide est autorisée et ne produit ni vitesse ni
consommation de soutenabilité.

Le capital suit la formule du GDD :
`ceil(Rmax_5km × (N / 7) × P_affûtage)`.
`RacePlayerConfig.affutage_level` fournit le palier déjà déterminé par le
Training (0 à 4), associé aux coefficients 0, 0,25, 0,50, 0,75 et 1.
La détermination de ce palier à partir de la fatigue résiduelle reste à
raccorder au profil Training ; aucune conversion de fatigue n'est inventée
ici.

## Déterminisme et validation

Les RNG sont injectés et conservés par joueur. Une décision invalide ne
consomme ni capital de relance ni état aléatoire de résolution ; le secteur
reste en attente de décisions valides. Les cartes révélées et les dés lancés
restent visibles pendant cette attente.

## Tests

    python -m unittest experiments.current.race_v2_prototype.test_race -v
    python -m unittest experiments.current.race_v2_prototype.test_dice -v
    python -m unittest experiments.current.race_v2_prototype.test_dice_session -v
