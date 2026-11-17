# Sensibilité du TN — stratégie long terme

## Protocole
50 000 courses par configuration, graine NumPy 20261117. Pool initial 4d6, 8 tours, réserve de soutenabilité 8 et réserve commune de 8 relances. Stratégie long terme uniquement.

Pour chaque TN de 9 à 14 :
- EF = TN - 5 ; VMA = TN + 3.
- La courbe relative EF→VMA est inchangée : coûts 1, 1, 2, 3, 4, 5, 7, 10, 13.
- Sous EF strictement : coût nul, énergie plafonnée à EF-1.
- Au-dessus de VMA : énergie plafonnée à VMA, coût fixé à 13.
- Si le coût dépasse la réserve restante, tour bloqué à EF-1 sans payer le coût.
- À soutenabilité nulle, un dé est retiré et les tours restants sont bloqués à EF-1.
- Chaque dé ne peut être relancé qu'une fois par tour ; une relance remplace le résultat.

La cible long terme est le niveau d'énergie le plus élevé dont le coût est inférieur ou égal à ceil(soutenabilité restante / tours restants). Les relances corrigent les dépassements de cible. Il s'agit d'une heuristique, pas d'une stratégie optimale.

## Résultats

| TN | EF | VMA | Énergie moyenne / 8 tours | IC95 énergie | Soutenabilité consommée | Dés perdus | Relances utilisées | Tours bloqués EF |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 9 | 4 | 12 | 34.695 | [34.681 ; 34.709] | 7.528 | 0.666 | 7.157 | 4.686 |
| 10 | 5 | 13 | 43.156 | [43.142 ; 43.170] | 7.601 | 0.711 | 7.217 | 4.309 |
| 11 | 6 | 14 | 51.511 | [51.496 ; 51.525] | 7.638 | 0.740 | 7.284 | 3.979 |
| 12 | 7 | 15 | 59.593 | [59.578 ; 59.607] | 7.651 | 0.746 | 7.446 | 3.841 |
| 13 | 8 | 16 | 67.598 | [67.583 ; 67.613] | 7.652 | 0.747 | 7.527 | 3.685 |
| 14 | 9 | 17 | 75.508 | [75.493 ; 75.524] | 7.649 | 0.745 | 7.612 | 3.507 |

## Lecture
- L'énergie moyenne augmente d'environ 8 points par point de TN sur 8 tours. C'est en partie mécanique : EF, TN et VMA, donc l'échelle de score, sont tous translatés.
- La soutenabilité consommée reste proche de 7.5–7.65 : la réserve est presque entièrement utilisée dans toutes les configurations.
- Les dés perdus restent autour de 0.67–0.75 par course ; les relances utilisées autour de 7.16–7.61 sur 8.
- Les tours bloqués à EF diminuent de 4.69 à 3.51, mais EF se déplace aussi. Cette métrique n'est donc pas une comparaison à seuil absolu constant.

## Limite principale
Ce test mesure l'effet combiné du déplacement du TN et de toute la courbe énergie-soutenabilité. Il ne mesure pas l'effet isolé du TN à EF/VMA fixes. Les scores absolus ne doivent pas être interprétés comme une mesure pure de difficulté.
