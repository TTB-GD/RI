# Sensibilité du TN — stratégie long terme

## Question expérimentale

Mesurer l'effet du TN sur la résolution Blackjack, sans déplacer la courbe physiologique énergie–soutenabilité.

## Protocole

- 50 000 courses par TN, graine NumPy 20261117.
- TN testé : 9, 10, 11, 12, 13 et 14.
- Pool initial : 4d6 ; 8 tours.
- Réserve initiale de soutenabilité : 8.
- Réserve commune de relances : 8.
- Stratégie long terme uniquement.

**La courbe reste identique pour tous les TN :**

| Energie | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Soutenabilité | 0 | 1 | 1 | 2 | 3 | 4 | 5 | 7 | 10 | 13 |

EF = 9 et VMA = 17 pour toutes les configurations. Sous 9, le coût est nul et l'énergie produite est plafonnée à 8. Au-dessus de 17, la sortie est plafonnée à 17 et le coût à 13.

### Règle de décision

Le TN est uniquement la cible Blackjack. La cible effective du tour est :

`min(TN, cible_{LT})`

où `cible_LT` est le niveau d'énergie le plus élevé dont le coût est inférieur ou égal à `ceil(soutenabilité restante / tours restants)`. Si aucun niveau à partir de 9 n'est payable dans ce budget, la cible est 8.

Le joueur lance N−2 dés, puis ajoute les dés manquants un par un si le total reste sous la cible. Un total supérieur à la cible est corrigé par relance du dé le plus élevé, dans la limite de la réserve commune. Quand le pool est complet et le total reste sous la cible, la relance porte sur le plus petit dé. Chaque dé ne peut être relancé qu'une fois par tour ; une relance remplace le résultat.

Si le coût final dépasse la soutenabilité restante, le tour est bloqué à 8 sans dépense. Quand la soutenabilité atteint exactement zéro, un dé est perdu et les tours restants sont bloqués à 8.

Il s'agit d'une heuristique explicite, pas d'un solveur de stratégie optimale.

## Résultats

| TN | Energie moyenne / 8 tours | IC95 énergie | Soutenabilité consommée | Dés perdus | Relances utilisées | Tours bloqués à 8 |
|---:|---:|---:|---:|---:|---:|---:|
| 9 | 73.460 | [73.447 ; 73.472] | 7.731 | 0.790 | 7.580 | 2.983 |
| 10 | 75.596 | [75.581 ; 75.612] | 7.628 | 0.716 | 7.610 | 3.377 |
| 11 | 75.512 | [75.496 ; 75.528] | 7.659 | 0.746 | 7.606 | 3.510 |
| 12 | 75.498 | [75.483 ; 75.514] | 7.651 | 0.747 | 7.607 | 3.505 |
| 13 | 75.496 | [75.481 ; 75.512] | 7.651 | 0.746 | 7.610 | 3.519 |
| 14 | 75.511 | [75.495 ; 75.527] | 7.646 | 0.745 | 7.613 | 3.502 |

## Lecture

- TN 9 est en retrait d'environ 2.14 points d'énergie par rapport à TN 10 sur les huit tours.
- De TN 10 à TN 14, les moyennes sont pratiquement identiques : l'écart maximal est d'environ 0.10 point. Les intervalles de confiance se recouvrent largement.
- Dans ce modèle, TN 10 suffit donc à atteindre le plateau de performance de cette heuristique. Augmenter le TN au-delà ne produit pas de gain mesurable.
- La réserve de soutenabilité est presque entièrement dépensée dans toutes les configurations (7.63 à 7.73 sur 8).
- Environ 7.6 relances sur 8 sont utilisées en moyenne : la réserve de relances est presque saturée.
- Le nombre de tours bloqués reste compris entre 2.98 et 3.52. TN 9 en compte moins, mais son énergie totale est également plus faible.

## Limites et interprétation

Ces résultats mesurent l'effet du plafond TN dans cette séquence Blackjack et avec cette politique précise. Ils ne démontrent pas que TN 10 est optimal pour un joueur humain : les décisions de relance sont déterministes et heuristiques, et aucune stratégie alternative n'a été optimisée.

La proximité des résultats de TN 10 à 14 suggère toutefois que, dans les conditions testées, la contrainte de soutenabilité et la réserve de relances deviennent plus déterminantes que le TN dès que celui-ci atteint 10.

Aucun changement du GDD : expérimentation uniquement.
