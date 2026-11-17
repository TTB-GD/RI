# Comparaison Blackjack — réserve de relances et gestion de soutenabilité

**Statut : EXPERIMENTAL — simulation heuristique, non normative.**  
**Date :** 17 novembre 2026  
**Source des paramètres :** `FEEDBACK.md` (main, 17 novembre 2026, 16 h 53)

## 1. Question

Comparer, sur une course de 8 tours, les réserves de 0, 4 et 8 relances communes, avec deux comportements :
- opportuniste : maximiser la dépense immédiatement payable ;
- gestion à long terme : répartir la soutenabilité sur les tours restants.

Le test porte sur le pool de référence 4d6, TN 14, soutenabilité initiale 8.

## 2. Modèle appliqué

| Énergie | 9 (EF) | 10 | 11 | 12 | 13 | 14 (TN) | 15 | 16 | 17 (VMA) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Coût de soutenabilité | 1 | 1 | 2 | 3 | 4 | 5 | 7 | 10 | 13 |

- Sous 9 : coût nul, dépense énergétique plafonnée à 8.
- Au-dessus de 17 : dépense écrêtée à 17, coût fixé à 13.
- Si le coût du résultat dépasse la soutenabilité restante : dépense bloquée à 8 pour le tour, sans débit de soutenabilité.
- Lorsque la réserve atteint exactement zéro : un dé est retiré ; tous les tours suivants sont bloqués à 8.
- Blackjack : lancer initial de N-2 dés, puis ajout possible des dés restants un par un.
- Réserve de relances partagée sur la course ; une relance remplace le résultat ; chaque dé ne peut être relancé qu'une fois par tour. Les jetons non utilisés sont conservés.

**Point de modélisation :** lorsque la soutenabilité est épuisée, les tours restants sont directement comptés à 8 ; le dé retiré est enregistré mais n'a plus d'effet supplémentaire puisque la dépense est déjà verrouillée à 8.

## 3. Politiques comparées

### Opportuniste

À chaque tour, viser le niveau d'énergie le plus élevé dont le coût est payable avec la soutenabilité immédiatement disponible. Ajouter des dés jusqu'à atteindre la cible. Une relance n'est utilisée que pour corriger un résultat dont le coût excède la réserve restante.

Cette politique privilégie la dépense immédiate et ne valorise pas la réserve destinée aux tours futurs.

### Gestion à long terme

À chaque tour, calculer un budget de soutenabilité par tour égal à `ceil(réserve restante / nombre de tours restants)`. Viser le niveau d'énergie le plus élevé compatible avec ce budget. Les relances servent à corriger les dépassements de cette cible.

Cette politique est une heuristique de répartition, pas un calcul d'optimalité globale.

## 4. Résultats

50 000 courses par configuration ; générateur NumPy, graine 20261117.

### Énergie cumulée

| Politique | Relances | Énergie moyenne | Erreur-type |
|---|---:|---:|---:|
| Opportuniste | 0 | 73,51 | 0,007 |
| Opportuniste | 4 | 73,17 | 0,006 |
| Opportuniste | 8 | 73,13 | 0,005 |
| Long terme | 0 | 74,99 | 0,007 |
| Long terme | 4 | 75,25 | 0,008 |
| Long terme | 8 | **75,50** | 0,008 |

### Autres indicateurs moyens par course

| Politique | Relances | Soutenabilité consommée | Dés perdus | Relances utilisées | Tours bloqués à 8 |
|---|---:|---:|---:|---:|---:|
| Opportuniste | 0 | 7,69 | 0,83 | 0,00 | 5,20 |
| Opportuniste | 4 | 7,80 | 0,89 | 3,46 | 5,52 |
| Opportuniste | 8 | 7,88 | 0,93 | 5,55 | 5,69 |
| Long terme | 0 | 7,79 | 0,83 | 0,00 | 3,98 |
| Long terme | 4 | 7,72 | 0,79 | 3,99 | 3,73 |
| Long terme | 8 | 7,65 | 0,75 | 7,61 | 3,51 |

## 5. Lecture

1. **La gestion à long terme domine l'opportunisme dans ce test.** Sans relance, elle produit environ 1,47 énergie cumulée supplémentaire. La différence vient principalement du rythme de consommation de la soutenabilité : l'opportunisme dépense fortement au début et passe davantage de tours au plafond de 8.
2. **Les relances n'aident pas la politique opportuniste.** Elles augmentent légèrement la consommation de soutenabilité et le nombre de tours bloqués, sans gain d'énergie. Dans cette politique, elles corrigent les résultats inabordables, mais ne changent pas la logique de dépense agressive.
3. **Les relances améliorent la politique à long terme.** Le gain moyen est d'environ +0,26 avec 4 relances, puis +0,25 supplémentaire avec 8. Les 8 jetons sont presque tous utilisés.
4. **Le gain n'est pas principalement une augmentation de soutenabilité consommée.** Avec davantage de relances, la politique à long terme dépense légèrement moins de soutenabilité, perd moins de dés et passe moins de tours bloqués à 8. Les relances servent ici à mieux contrôler les résultats autour de la cible.

## 6. Limites et suite

- Ces deux politiques sont des heuristiques écrites pour rendre la comparaison reproductible. Elles ne représentent ni une stratégie humaine universelle, ni une solution optimale.
- La politique à long terme utilise une règle de budget moyen avec arrondi supérieur ; d'autres calendriers de dépense peuvent être meilleurs.
- La simulation n'intègre pas de variation de dés (d8/d10/d12), de terrain, de profils physiologiques distincts, ni de choix de courbe.
- L'effet du retrait du dé est enregistré, mais la règle de verrouillage à 8 rend son impact mécanique ultérieur nul dans ce test.
- L'écart entre 4 et 8 relances est faible au regard du modèle heuristique. Il ne suffit pas à justifier 8 jetons comme valeur définitive.

**Conclusion expérimentale :** la qualité du dosage de la soutenabilité a un effet plus important que la quantité de relances. Les relances semblent surtout utiles comme outil de correction pour une stratégie qui cherche à respecter un budget de dépense. Le test ne permet pas encore de fixer la réserve définitive ; il justifie de poursuivre avec des politiques plus riches ou un solveur de décision à horizon complet.
