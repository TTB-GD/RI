# Profils de référence — vitesses physiologiques et allures spécifiques

**Statut :** propositions de référence à conserver pour le calibrage de la courbe Race V2  
**Date :** 12 novembre 2026  
**Référentiel :** Jack Daniels, *Daniels' Running Formula*, 4e édition ; équivalences de performance VDOT et tables d'intensité.

## 1. Objet

Ce document conserve cinq profils de référence permettant de donner des ordres de grandeur crédibles :
- aux vitesses physiologiques EF, Seuil et VMA ;
- aux allures spécifiques de course AS42, AS21, AS10 et AS5.

Ces profils servent de points d'ancrage pour le travail de conception et les simulations. Ils ne constituent ni des profils de joueurs obligatoires, ni une formule de progression, ni une validation définitive des bornes du système.

## 2. Méthode de construction

Les profils sont espacés de dix points de VDOT : 30, 40, 50, 60 et 70.

### 2.1. Points physiologiques EF, Seuil et VMA

Le référentiel Daniels fournit :
- une plage d'allure E (Easy) ;
- une allure T (Threshold) ;
- une allure I (Interval), prescrite pour des répétitions de 3 à 5 minutes.

Pour obtenir un point EF unique, la valeur retenue est le milieu arithmétique de la plage E, exprimée en secondes par kilomètre. Ce choix est une convention de modélisation : l'EF réelle est une plage, et le milieu ne prétend pas représenter une intensité physiologique universelle.

Le Seuil reprend l'allure T. La vitesse I est utilisée comme approximation opérationnelle de la VMA. Cette équivalence est indicative : l'allure I de Daniels et la VMA mesurée en laboratoire ou sur le terrain ne sont pas strictement identiques.

### 2.2. Allures spécifiques AS42, AS21, AS10 et AS5

Les allures spécifiques sont dérivées des performances équivalentes prédites par le modèle VDOT de Daniels pour un même niveau de performance :
- AS42 : allure marathon ;
- AS21 : allure semi-marathon ;
- AS10 : allure 10 km ;
- AS5 : allure 5 km.

Il s'agit d'équivalences théoriques entre distances, pas d'une garantie de performance. Elles supposent notamment une endurance suffisante pour exprimer le potentiel sur marathon. En pratique, un coureur peut présenter un profil moins homogène entre distances, notamment si son endurance spécifique est moins développée.

Conversion d'une allure en vitesse :

`v (km/h) = distance (km) / durée (h)`

Les vitesses sont arrondies au dixième de km/h pour la lisibilité. Les temps de course sources sont conservés ci-dessous afin de permettre de retrouver les conversions.

## 3. Profils proposés

| Profil indicatif | VDOT | EF (km/h) | Seuil (km/h) | VMA approx. (km/h) |
|---|---:|---:|---:|---:|
| Débutant / faible niveau de performance | 30 | 7,6 | 9,4 | 10,1 |
| Récréatif régulier | 40 | 9,5 | 11,8 | 12,9 |
| Entraîné | 50 | 11,4 | 14,1 | 15,3 |
| Confirmé | 60 | 13,2 | 16,4 | 17,7 |
| Très performant | 70 | 15,0 | 18,6 | 20,1 |

### 3.1. Allures sources des points physiologiques

| VDOT | Plage E Daniels (min/km) | Point EF retenu (min/km) | T (min/km) | I (min/km) |
|---:|---:|---:|---:|---:|
| 30 | 7:27–8:14 | 7:50,5 | 6:24 | 5:55 |
| 40 | 5:56–6:38 | 6:17 | 5:06 | 4:40 |
| 50 | 4:56–5:34 | 5:15 | 4:15 | 3:55 |
| 60 | 4:15–4:49 | 4:32 | 3:40 | 3:23 |
| 70 | 3:44–4:15 | 3:59,5 | 3:14 | 2:59 |

### 3.2. Allures spécifiques de course proposées

| Profil | VDOT | AS42 (km/h) | AS21 (km/h) | AS10 (km/h) | AS5 (km/h) |
|---|---:|---:|---:|---:|---:|
| Débutant / faible niveau de performance | 30 | 8,7 | 9,0 | 9,4 | 9,8 |
| Récréatif régulier | 40 | 11,0 | 11,4 | 12,0 | 12,4 |
| Entraîné | 50 | 13,3 | 13,8 | 14,5 | 15,1 |
| Confirmé | 60 | 15,5 | 16,1 | 17,0 | 17,6 |
| Très performant | 70 | 17,5 | 18,5 | 19,4 | 20,1 |

### 3.3. Performances équivalentes utilisées pour les AS

| VDOT | 5 km | 10 km | Semi-marathon | Marathon |
|---:|---:|---:|---:|---:|
| 30 | 30:41 | 1:03:49 | 2:21:17 | 4:49:49 |
| 40 | 24:06 | 50:01 | 1:50:54 | 3:49:37 |
| 50 | 19:56 | 41:20 | 1:31:31 | 3:10:40 |
| 60 | 17:03 | 35:22 | 1:18:09 | 2:43:22 |
| 70 | 14:56 | 31:01 | 1:08:23 | 2:23:13 |


## 3.4. Profils de départ proposés pour le jeu

Pour disposer d'une gamme de départ simple et directement exploitable, huit profils sont proposés avec une EF entière de 8 à 15 km/h, par pas de 1 km/h.

Les valeurs sont construites à partir des cinq profils VDOT de référence :
1. interpolation linéaire, colonne par colonne, entre les points VDOT encadrant la valeur EF recherchée ;
2. arrondi aux km/h entiers ;
3. ajustement minimal lorsque l'arrondi indépendant crée des égalités ou inversions, afin de préserver l'ordre des allures et des points physiologiques.

Les contraintes d'ordre appliquées sont :
- `EF < AS42 < AS21 < Seuil` ;
- `Seuil ≤ AS10 < AS5 ≤ VMA`.

L'égalité Seuil = AS10 est autorisée : le modèle VDOT peut donner une allure 10 km très proche de l'allure seuil, particulièrement pour les profils les moins performants. Les égalités AS5 = VMA sont également tolérées lorsque l'arrondi à 1 km/h ne permet pas de conserver un écart sans déformer davantage la référence. Les valeurs restent des paramètres de départ de jeu, non des mesures physiologiques individuelles.

| Profil de départ | EF | AS42 | AS21 | Seuil | AS10 | AS5 | VMA |
|---|---:|---:|---:|---:|---:|---:|---:|
| P8 | 8 | 9 | 10 | 11 | 11 | 12 | 12 |
| P9 | 9 | 10 | 11 | 12 | 12 | 13 | 13 |
| P10 | 10 | 11 | 12 | 13 | 13 | 14 | 14 |
| P11 | 11 | 12 | 13 | 14 | 14 | 15 | 15 |
| P12 | 12 | 13 | 14 | 15 | 15 | 16 | 16 |
| P13 | 13 | 15 | 16 | 17 | 17 | 18 | 18 |
| P14 | 14 | 16 | 17 | 18 | 18 | 19 | 19 |
| P15 | 15 | 17 | 18 | 19 | 19 | 20 | 20 |

Toutes les valeurs sont en km/h. Les profils P8 à P15 constituent la proposition de gamme de départ pour le jeu. Ils ne remplacent pas les références VDOT décimales des sections précédentes, qui restent conservées comme base de calcul et de traçabilité.


## 4. Interprétation et limites

1. **VDOT n'est pas une mesure directe de VO₂max.** C'est un indice de performance construit à partir des performances en course et intégrant notamment économie de course et fraction de VO₂max soutenable.
2. **EF est le point le moins déterminé.** Daniels donne une plage assez large. Le point central est choisi pour obtenir une valeur de base exploitable dans le jeu ; il ne doit pas masquer cette variabilité.
3. **I n'est qu'un proxy de VMA.** Il fournit un repère cohérent pour la vitesse proche de VO₂max, mais ne remplace pas une mesure de VMA.
4. **Les AS sont des équivalences de performance.** Elles décrivent un profil théorique homogène ; elles ne prennent pas en compte un déficit d'endurance, une spécialisation sur courte distance ou les conditions de course.
5. **Les profils sont des repères de cohérence.** Ils ne déterminent pas les coordonnées d'énergie des points EF, Seuil et VMA, ni la forme de la courbe entre ces points.
6. **Les AS ne sont pas des points physiologiques supplémentaires.** Elles restent des cibles propres à la distance préparée, conformément au modèle Race V2.
7. **Pas d'extrapolation automatique.** Le profil VDOT 70 donne une référence haute déjà performante. Une extension vers VDOT 80 ou davantage devra être justifiée séparément si le jeu doit représenter des niveaux d'élite.

## 5. Statut pour Run It

Ces cinq profils sont conservés comme **références de calibrage proposées** pour :
- la composante vitesse de la courbe physiologique EF / Seuil / VMA ;
- les valeurs de départ des AS42 / AS21 / AS10 / AS5.

Ils ne changent pas les règles déjà retenues :
- EF < Seuil < VMA ;
- les trois points physiologiques possèdent chacun une coordonnée énergie et une coordonnée vitesse ;
- la courbe de conversion est une table entière énergie → vitesse, sans interpolation ;
- EF reste le plancher de vitesse et VMA le plafond ;
- l'AS est un repère de course distinct, non un quatrième point physiologique.

Les valeurs des AS sont des valeurs initiales proposées pour les profils de référence. Leur progression, leur éventuelle saturation et leur relation exacte aux points EF / Seuil / VMA restent régies par les décisions de conception Race V2 et doivent être calibrées par simulation.

## 6. Sources

- Jack Daniels, *Daniels' Running Formula*, 4th edition, Human Kinetics, 2022, tables 5.2 (« Training Intensities Based on Current VDOT ») et 5.3 (« Training Intensities for Novice Runners and Others Starting With Slow Performances »).
- Équivalences de performance VDOT calculées selon les équations Daniels–Gilbert, tableaux de référence VDOT 30 à 70.

Les allures E, T et I utilisées pour les points physiologiques sont reprises des tables Daniels. Les temps équivalents de course et les vitesses AS sont des références de performance calculées selon le modèle VDOT. Les conversions en km/h, le choix du point médian EF et leur utilisation comme valeurs de départ dans Run It sont des conventions de modélisation.
