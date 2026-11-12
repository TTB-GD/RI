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

## Dés et relances — composant expérimental séparé

`dice.py` reprend les tailles de dés du Training (`6`, `8`, `10`, `12`)
sans modifier ni dupliquer la progression du pool.

- `roll_dice_pool` lance l'intégralité du pool à chaque appel ;
- `resolve_dice_decision` applique les relances individuelles avant la sélection ;
- une relance remplace le résultat précédent et consomme une unité de capital ;
- un même dé peut être relancé plusieurs fois si le capital le permet ;
- la sélection accepte tout sous-ensemble, y compris le sous-ensemble vide ;
- les dés non sélectionnés ne sont pas dépensés et seront relancés au prochain appel.

Le capital global est calculé par
`ceil(Rmax_5km × (N / 7) × P_affûtage)`. Le profil Training fournit
`affutage_level` (0 à 4), converti en coefficient 0, 0,25, 0,50, 0,75 ou 1.
Cette entrée explicite évite de déduire arbitrairement l'affûtage d'une valeur
de fatigue non encore raccordée au prototype.

**Frontière actuelle :** le composant de dés est testé séparément ; il n'est
pas encore appelé par `RaceState.play_sector`. L'orchestration multi-secteur
continue donc à recevoir l'énergie dépensée, en attendant le raccordement
interactif en deux temps (lancer, puis décisions du joueur).

Le terrain est un entier signé par secteur : positif en montée, négatif en
descente.

## Déterminisme

Les fonctions de dés reçoivent un générateur aléatoire explicite. Deux appels
avec les mêmes entrées et le même état RNG produisent les mêmes résultats.

## Tests

    python -m unittest experiments.current.race_v2_prototype.test_race -v
    python -m unittest experiments.current.race_v2_prototype.test_dice -v
