# Profils de référence — vitesses physiologiques

**Statut :** proposition de référence à conserver pour le calibrage de la courbe Race V2  
**Date :** 12 novembre 2026  
**Référentiel :** Jack Daniels, *Daniels' Running Formula*, 4e édition, tables 5.2 et 5.3.

## 1. Objet

Ce document fixe cinq profils de référence permettant de donner des ordres de grandeur crédibles aux vitesses EF, Seuil et VMA de la courbe physiologique de Run It.

Ces profils servent de points d'ancrage pour le travail de conception et les simulations. Ils ne constituent ni des profils de joueurs obligatoires, ni une formule de progression, ni une validation définitive des bornes du système.

## 2. Méthode de construction

Les profils sont espacés de dix points de VDOT : 30, 40, 50, 60 et 70.

Le référentiel Daniels fournit :
- une plage d'allure E (Easy) ;
- une allure T (Threshold) ;
- une allure I (Interval), prescrite pour des répétitions de 3 à 5 minutes.

Pour obtenir un point EF unique, la valeur retenue est le milieu arithmétique de la plage E, exprimée en secondes par kilomètre. Ce choix est une convention de modélisation : l'EF réelle est une plage, et le milieu ne prétend pas représenter une intensité physiologique universelle.

Le Seuil reprend l'allure T. La vitesse I est utilisée comme approximation opérationnelle de la VMA. Cette équivalence est indicative : l'allure I de Daniels et la VMA mesurée en laboratoire ou sur le terrain ne sont pas strictement identiques.

Conversion d'une allure en vitesse :
`v (km/h) = 3600 / allure (secondes/km)`

Les vitesses sont arrondies au dixième de km/h pour la lisibilité. Les valeurs de référence non arrondies peuvent être recalculées à partir des allures indiquées.

## 3. Profils proposés

| Profil indicatif | VDOT | EF (km/h) | Seuil (km/h) | VMA approx. (km/h) |
|---|---:|---:|---:|---:|
| Débutant / faible niveau de performance | 30 | 7,6 | 9,4 | 10,1 |
| Récréatif régulier | 40 | 9,5 | 11,8 | 12,9 |
| Entraîné | 50 | 11,4 | 14,1 | 15,3 |
| Confirmé | 60 | 13,2 | 16,4 | 17,7 |
| Très performant | 70 | 15,0 | 18,6 | 20,1 |

### Allures sources utilisées

| VDOT | Plage E Daniels (min/km) | Point EF retenu (min/km) | T (min/km) | I (min/km) |
|---:|---:|---:|---:|---:|
| 30 | 7:27–8:14 | 7:50,5 | 6:24 | 5:55 |
| 40 | 5:56–6:38 | 6:17 | 5:06 | 4:40 |
| 50 | 4:56–5:34 | 5:15 | 4:15 | 3:55 |
| 60 | 4:15–4:49 | 4:32 | 3:40 | 3:23 |
| 70 | 3:44–4:15 | 3:59,5 | 3:14 | 2:59 |

## 4. Interprétation et limites

1. **VDOT n'est pas une mesure directe de VO₂max.** C'est un indice de performance construit à partir des performances en course et intégrant notamment économie de course et fraction de VO₂max soutenable.
2. **EF est le point le moins déterminé.** Daniels donne une plage assez large. Le point central est choisi pour obtenir une valeur de base exploitable dans le jeu ; il ne doit pas masquer cette variabilité.
3. **I n'est qu'un proxy de VMA.** Il fournit un repère cohérent pour la vitesse proche de VO₂max, mais ne remplace pas une mesure de VMA.
4. **Les profils sont des repères de cohérence.** Ils ne déterminent pas les coordonnées d'énergie des points EF, Seuil et VMA, ni la forme de la courbe entre ces points.
5. **Pas d'extrapolation automatique.** Le profil VDOT 70 donne une référence haute déjà performante. Une extension vers VDOT 80 ou davantage devra être justifiée séparément si le jeu doit représenter des niveaux d'élite.

## 5. Statut pour Run It

Ces cinq triplets sont conservés comme **références de calibrage proposées** pour la composante vitesse de la courbe physiologique.

Ils ne changent pas les règles déjà retenues :
- EF < Seuil < VMA ;
- les trois points physiologiques possèdent chacun une coordonnée énergie et une coordonnée vitesse ;
- la courbe de conversion est une table entière énergie → vitesse, sans interpolation ;
- EF reste le plancher de vitesse et VMA le plafond ;
- l'AS est un repère de course distinct, non un quatrième point physiologique.

La prochaine étape de calibrage consiste à déterminer comment ces vitesses de référence se traduisent en valeurs entières dans la courbe de jeu, et comment les profils intermédiaires sont construits.

## 6. Source

Jack Daniels, *Daniels' Running Formula*, 4th edition, Human Kinetics, 2022, tables 5.2 (« Training Intensities Based on Current VDOT ») et 5.3 (« Training Intensities for Novice Runners and Others Starting With Slow Performances »).

Les allures E, T et I utilisées dans ce document sont reprises de ces tables. Les vitesses en km/h et le choix du point médian EF sont des conversions et conventions de modélisation propres à Run It.
