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

## Frontière d'entrée

Pour chaque secteur, `play_sector` reçoit une dépense d'énergie non négative
par joueur. Il s'agit de la somme des dés choisis après relances et sélection
du sous-ensemble. Les lancers, relances et interactions utilisateur restent
hors de cette couche.

Le terrain est un entier signé par secteur : positif en montée, négatif en
descente.

## Déterminisme

`RaceState.create` accepte une graine. Les tirages 3d6, l'ordre des catégories
et les valeurs des cartes sont reproductibles pour le même ordre de joueurs
et la même graine.

## Tests

    python -m unittest experiments.current.race_v2_prototype.test_race -v
